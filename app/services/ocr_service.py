from app.adapters.gemini_adapter import gemini_adapter
from fastapi import UploadFile, HTTPException

MAX_FILE_SIZE = 5 * 1024 * 1024  

class OCRService:
    async def extract_text(self, file: UploadFile) -> str:
        try:
            await file.seek(0)
            if file.content_type not in {"image/jpeg", "image/png", "application/pdf"}:
                raise ValueError(f"Unsupported file type: {file.content_type}")

            content = await file.read()

            if len(content) > MAX_FILE_SIZE:
                raise ValueError("File size exceeds the 5MB limit")

            return await gemini_adapter.vision_to_text(content)

        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            raise RuntimeError(f"OCR Pipeline failed: {str(e)}")

        finally:
            await file.close()

ocr_service = OCRService()