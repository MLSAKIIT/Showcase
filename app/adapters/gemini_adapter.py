import asyncio
import google.generativeai as genai
from app.core.config import settings

# 1. MATCHING THE INIT.PY EXCEPTION HIERARCHY
class GeminiError(Exception):
    """Base exception for Gemini adapter"""
    pass

class GeminiAPIError(GeminiError):
    """Specific exception for Gemini API failures"""
    pass

class GeminiResponseParseError(GeminiError):
    """Specific exception for malformed AI responses"""
    pass

class GeminiEmptyResponseError(GeminiError):
    """Specific exception for empty AI responses"""
    pass

class GeminiRateLimitError(GeminiError):
    """Specific exception for rate limiting"""
    pass

# 2. THE ADAPTER CLASS
class GeminiAdapter:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Using flash for faster resume processing
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def vision_to_text(self, image_bytes: bytes) -> str:
        prompt = "Extract all text from this resume. Maintain hierarchy using Markdown."
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                [prompt, {'mime_type': 'image/jpeg', 'data': image_bytes}]
            )
            
            if not response or not hasattr(response, 'text') or not response.text:
                raise GeminiEmptyResponseError("Empty response from Gemini")
                
            return response.text
        except Exception as e:
            if "429" in str(e):
                raise GeminiRateLimitError("Rate limit reached")
            raise GeminiAPIError(f"Gemini API Error: {str(e)}")

# Global instance for the app to use
gemini_adapter = GeminiAdapter()