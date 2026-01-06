import asyncio
import google.generativeai as genai
from app.core.config import settings

class GeminiAdapter:
    def __init__(self):
    
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.vision_model = genai.GenerativeModel(settings.GEMINI_VISION_MODEL)

    async def vision_to_text(self, image_bytes: bytes) -> str:
       
        prompt = (
            "Extract all text from this resume. "
            "Maintain the hierarchy, formatting, and sections using Markdown."
        )

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.vision_model.generate_content,
                    [prompt, {'mime_type': 'image/jpeg', 'data': image_bytes}]
                ),
                timeout=30
            )
        except asyncio.TimeoutError:
            raise RuntimeError("Gemini OCR request timed out after 30 seconds")
        except Exception as e:
            raise RuntimeError(f"Gemini SDK encountered an error: {str(e)}")

        if not response or not hasattr(response, 'text') or not response.text:
            raise RuntimeError("Gemini returned an empty or malformed OCR response")

        return response.text

gemini_adapter = GeminiAdapter()