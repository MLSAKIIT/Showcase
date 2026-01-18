"""
async adapter for Google Gemini API.

This module handles all HTTP communication with Gemini, including:
- Async requests with connection pooling
- Exponential backoff and retry logic
- Rate limit detection (429 handling)
- Response parsing and validation
- Typed exception handling

Architecture: Called by agents via dependency injection.

Usage:
    adapter = GeminiAdapter(api_key="...", max_retries=3)
    text = await adapter.generate_text(prompt="...", temperature=0.7)
    await adapter.close()

Exceptions:
    - GeminiAPIError: HTTP/service errors
    - GeminiRateLimitError: 429 rate limiting
    - GeminiResponseParseError: Invalid response structure
    - GeminiEmptyResponseError: Empty content returned

See: agents/generation/content_generator.py for usage examples.
"""


import asyncio
import logging
import httpx
from typing import Optional
import google.genai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)


# Exception classes for Gemini adapter
class GeminiError(Exception):
    """Base exception for Gemini adapter errors."""
    pass

class GeminiAPIError(GeminiError):
    """Gemini API returned an error status code."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"Gemini API error {status_code}: {message}")

class GeminiResponseParseError(GeminiError):
    """Failed to parse Gemini response structure."""
    pass

class GeminiEmptyResponseError(GeminiError):
    """Gemini returned empty or invalid content."""
    pass

class GeminiRateLimitError(GeminiError):
    """Gemini rate limit exceeded."""
    pass

class GeminiAdapter:
    """
    Infrastructure adapter for Google Gemini.
    """

    GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


    def __init__(self,
                api_key: str,
                model_name: str = "gemini-pro",
                timeout_seconds: int = 30,
                max_retries: int = 3,
                vision_model_name: str = "gemini-1.5-flash"
                ) -> None:
        
        if not api_key:
            raise ValueError("Gemini API key is required")

        self.api_key = api_key
        # Use newer model default
        self.api_key = api_key
        # Use newer model default if not specified
        self.model_name = "gemini-1.5-flash" if model_name == "gemini-pro" else model_name
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

        self._endpoint = (
            f"{self.GEMINI_BASE_URL}/models/{self.model_name}:generateContent"
        )
        
        self._client = httpx.AsyncClient(timeout=timeout_seconds)

        # Initialize SDK for Vision (Hybrid approach)
        # New google.genai API uses Client instead of configure
        self.genai_client = genai.Client(api_key=api_key)
        self.vision_model_name = vision_model_name


    async def close(self) -> None:
        """Close the HTTP client. Call this on shutdown."""
        await self._client.aclose()


    async def generate_text(self,
                            prompt: str,
                            temperature: float = 0.7,
                            max_tokens: int = 2048,
                            ) -> str:
        
        """
        Send a prompt to Gemini and return generated text.
        """

        last_exception: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                text = await self._call_gemini(
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                
                logger.info(
                    "Gemini generation succeeded on attempt %d (length: %d chars)",
                    attempt,
                    len(text),
                )
                return text

            except GeminiRateLimitError as exc:
                last_exception = exc
                backoff = min(2 ** (attempt - 1), 60)  # 1s, 2s, 4s, capped at 60s
                logger.warning(
                    "Rate limit hit (attempt %d/%d), backing off %ds",
                    attempt,
                    self.max_retries,
                    backoff,
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(backoff)
                continue

            except (GeminiAPIError, GeminiResponseParseError, GeminiEmptyResponseError) as exc:
                last_exception = exc
                logger.warning(
                    "Gemini request failed (attempt %d/%d): %s",
                    attempt,
                    self.max_retries,
                    str(exc),
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** (attempt - 1))  # Exponential backoff
                continue

            except Exception as exc:
                # Unexpected errors - don't retry
                logger.error("Unexpected error calling Gemini: %s", exc, exc_info=True)
                raise GeminiError(f"Unexpected Gemini error: {exc}") from exc

        # All retries have exhausted
        raise GeminiError(
            f"Gemini generation failed after {self.max_retries} attempts"
        ) from last_exception


    async def _call_gemini(self,      
                            prompt: str,
                            temperature: float,
                            max_tokens: int,
                            ) -> str:

        """
        Low-level Gemini REST API call.
        """

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        params = {"key": self.api_key}

        try:
            response = await self._client.post(
                self._endpoint,
                params=params,
                json=payload,
            )
        except httpx.TimeoutException as exc:
            raise GeminiAPIError(0, f"Request timeout after {self.timeout_seconds}s") from exc
        except httpx.RequestError as exc:
            raise GeminiAPIError(0, f"Network error: {exc}") from exc

        # Handle non-200 status codes (429 for rate limiting)
        if response.status_code == 429:
            raise GeminiRateLimitError("Rate limit exceeded")
        
        if response.status_code >= 500:
            raise GeminiAPIError(
                response.status_code,
                "Gemini service unavailable (5xx error)"
            )
        
        if response.status_code != 200:
            logger.error(
                "Gemini API error %d: %s",
                response.status_code,
                response.text[:500],
            )
            raise GeminiAPIError(
                response.status_code,
                f"API request failed: {response.text[:200]}"
            )

        # Parse JSON response
        try:
            data = response.json()
        except ValueError as exc:
            logger.error("Non-JSON response from Gemini: %s", response.text[:500])
            raise GeminiResponseParseError("Gemini returned non-JSON response") from exc

        return self._extract_text(data)


    def _extract_text(self, data: dict) -> str:

        """
        Extract generated text from Gemini response.
        """
        
        # Check for error in the response
        if "error" in data:
            error = data["error"]
            error_code = error.get("code", 0)
            error_msg = error.get("message", "No error message provided")
            
            # Ensure code is int (Gemini sometimes returns string codes)
            if not isinstance(error_code, int):
                error_code = 0
            
            raise GeminiAPIError(error_code, error_msg)

        # Extract text from nested structure
        try:
            candidates = data.get("candidates")
            if not candidates:
                raise GeminiEmptyResponseError("No candidates returned from Gemini")

            content = candidates[0].get("content")
            if not content:
                raise GeminiResponseParseError("Missing 'content' in response")

            parts = content.get("parts")
            if not parts:
                raise GeminiResponseParseError("Missing 'parts' in response")

            text = parts[0].get("text")
            if text is None:
                raise GeminiResponseParseError("Missing 'text' in parts")
            
            if not text.strip():
                raise GeminiEmptyResponseError("Gemini returned empty text")

            return text.strip()

        except GeminiError:
            # Re-raise our typed errors unchanged
            raise

        except (KeyError, IndexError, TypeError) as exc:
            logger.error("Failed to parse Gemini response: %s", data)
            raise GeminiResponseParseError(
                f"Invalid response structure: {type(exc).__name__}"
            ) from exc
        


    #Vision model for OCR if needed
    async def vision_to_text(self, image_bytes: bytes, mime_type: str = "image/jpeg", prompt: Optional[str] = None) -> str:
        """
        Extract text from images or PDFs using Gemini Vision API.
        
        Args:
            image_bytes: File content as bytes
            mime_type: MIME type of the file (image/jpeg, image/png, application/pdf)
            prompt: Optional custom prompt for extraction
        
        Returns:
            Extracted text as string
        
        Raises:
            GeminiError: If extraction fails
        """
        # Use optimized prompt based on file type
        if not prompt:
            if mime_type == "application/pdf":
                prompt = (
                    "Extract all text from this PDF document. "
                    "Maintain the structure and formatting. "
                    "Include all sections, headings, bullet points, and content. "
                    "If the document is a resume, extract all personal information, "
                    "work experience, education, and skills."
                )
            else:
                prompt = (
                    "Extract all text from this image. "
                    "Maintain the formatting and structure. "
                    "Include all visible text, numbers, and symbols."
                )

        try:
            logger.debug(
                f"Calling Gemini Vision API for OCR: "
                f"mime_type={mime_type}, size={len(image_bytes)} bytes"
            )
            
            # Using the new google.genai API
            # Content format for new API
            from google.genai import types
            
            # Create content parts
            parts = [
                types.Part.from_text(prompt),
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            ]
            
            # Call Gemini Vision API with timeout handling
            try:
                logger.info(
                    f"Calling Gemini Vision API: model={self.vision_model_name}, "
                    f"parts_count={len(parts)}, timeout={self.timeout_seconds}s"
                )
                
                response = await asyncio.wait_for(
                    self.genai_client.aio.models.generate_content(
                        model=self.vision_model_name,
                        contents=parts
                    ),
                    timeout=self.timeout_seconds
                )
                
                logger.info(f"Gemini Vision API call completed successfully")
                
            except asyncio.TimeoutError:
                logger.error(
                    f"OCR request timed out after {self.timeout_seconds} seconds. "
                    f"File size: {len(image_bytes)} bytes, MIME type: {mime_type}"
                )
                raise GeminiError(
                    f"OCR request timed out after {self.timeout_seconds} seconds. "
                    "The file may be too large or complex."
                )
            except Exception as api_error:
                logger.error(
                    f"Gemini Vision API call failed: {type(api_error).__name__}: {str(api_error)}",
                    exc_info=True
                )
                raise GeminiError(
                    f"OCR API call failed: {str(api_error)}"
                ) from api_error
            
            # Extract text from response
            if not response:
                raise GeminiEmptyResponseError("Gemini Vision returned no response")
            
            # New API structure: response.candidates[0].content.parts[0].text
            if not hasattr(response, 'candidates') or not response.candidates:
                raise GeminiEmptyResponseError("Gemini Vision returned no candidates")
            
            candidate = response.candidates[0]
            if not hasattr(candidate, 'content') or not candidate.content:
                raise GeminiEmptyResponseError("Gemini Vision returned empty content")
            
            if not hasattr(candidate.content, 'parts') or not candidate.content.parts:
                raise GeminiEmptyResponseError("Gemini Vision returned no parts")
            
            # Get text from first part
            text_part = candidate.content.parts[0]
            if not hasattr(text_part, 'text') or not text_part.text:
                raise GeminiEmptyResponseError("Gemini Vision returned empty text")
            
            extracted_text = text_part.text.strip()
            
            if not extracted_text:
                raise GeminiEmptyResponseError(
                    "No text was extracted. The file may contain only images without text."
                )
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters via OCR")
            return extracted_text
            
        except GeminiError:
            # Re-raise our typed errors
            raise
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Vision OCR failed: {error_msg}", exc_info=True)
            
            # Provide more specific error messages
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                raise GeminiError(
                    "OCR service quota exceeded. Please try again later."
                ) from e
            elif "timeout" in error_msg.lower():
                raise GeminiError(
                    "OCR request timed out. The file may be too large. "
                    "Please try a smaller file or split the document."
                ) from e
            elif "invalid" in error_msg.lower() or "format" in error_msg.lower():
                raise GeminiError(
                    f"Invalid file format for OCR: {error_msg}"
                ) from e
            else:
                raise GeminiError(f"OCR failed: {error_msg}") from e

# Instantiate Singleton
gemini_adapter = GeminiAdapter(
    api_key=settings.GEMINI_API_KEY,
    model_name=settings.GEMINI_AGENT_MODEL,
    vision_model_name=settings.GEMINI_VISION_MODEL
)