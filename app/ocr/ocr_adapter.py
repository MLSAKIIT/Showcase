"""
OCR adapter with pytesseract fallback and cloud provider interfaces.
"""
import os
from typing import Optional
from abc import ABC, abstractmethod

try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_path
    import docx
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False


class OCRProvider(ABC):
    """Abstract base class for OCR providers."""
    
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """Extract text from file."""
        pass


class TesseractOCRProvider(OCRProvider):
    """Pytesseract-based OCR provider (fallback)."""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text using pytesseract."""
        if not PYTESSERACT_AVAILABLE:
            raise RuntimeError("pytesseract not available. Install: pip install pytesseract pillow pdf2image")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == ".pdf":
            # Convert PDF to images
            images = convert_from_path(file_path)
            text_parts = []
            for image in images:
                text = pytesseract.image_to_string(image)
                text_parts.append(text)
            return "\n\n".join(text_parts)
        
        elif file_ext in {".png", ".jpg", ".jpeg"}:
            # Direct image OCR
            image = Image.open(file_path)
            return pytesseract.image_to_string(image)
        
        elif file_ext == ".docx":
            # Extract from DOCX
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")


class GoogleVisionOCRProvider(OCRProvider):
    """Google Vision API OCR provider (placeholder)."""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_VISION_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_VISION_API_KEY not set")
    
    def extract_text(self, file_path: str) -> str:
        """Extract text using Google Vision API."""
        # TODO: Implement Google Vision API
        # from google.cloud import vision
        # client = vision.ImageAnnotatorClient()
        # with open(file_path, 'rb') as image_file:
        #     content = image_file.read()
        # image = vision.Image(content=content)
        # response = client.document_text_detection(image=image)
        # return response.full_text_annotation.text
        raise NotImplementedError("Google Vision OCR not yet implemented")


class AWSTextractOCRProvider(OCRProvider):
    """AWS Textract OCR provider (placeholder)."""
    
    def __init__(self):
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        if not self.access_key or not self.secret_key:
            raise ValueError("AWS credentials not set")
    
    def extract_text(self, file_path: str) -> str:
        """Extract text using AWS Textract."""
        # TODO: Implement AWS Textract
        # import boto3
        # textract = boto3.client('textract', aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        # with open(file_path, 'rb') as document:
        #     response = textract.detect_document_text(Document={'Bytes': document.read()})
        # return ' '.join([block['Text'] for block in response['Blocks'] if block['BlockType'] == 'LINE'])
        raise NotImplementedError("AWS Textract OCR not yet implemented")


class OCRAdapter:
    """
    Main OCR adapter that tries cloud providers first, falls back to pytesseract.
    """
    
    def __init__(self, preferred_provider: Optional[str] = None):
        """
        Initialize OCR adapter.
        
        Args:
            preferred_provider: "google_vision", "aws_textract", or None for auto-fallback
        """
        self.preferred_provider = preferred_provider
        self._provider = None
    
    def _get_provider(self) -> OCRProvider:
        """Get OCR provider based on configuration."""
        if self._provider:
            return self._provider
        
        # Try preferred provider first
        if self.preferred_provider == "google_vision":
            try:
                self._provider = GoogleVisionOCRProvider()
                return self._provider
            except (ValueError, NotImplementedError):
                pass
        
        if self.preferred_provider == "aws_textract":
            try:
                self._provider = AWSTextractOCRProvider()
                return self._provider
            except (ValueError, NotImplementedError):
                pass
        
        # Fallback to pytesseract
        if PYTESSERACT_AVAILABLE:
            self._provider = TesseractOCRProvider()
            return self._provider
        
        raise RuntimeError(
            "No OCR provider available. Install pytesseract or configure cloud OCR credentials."
        )
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from file using available OCR provider."""
        provider = self._get_provider()
        return provider.extract_text(file_path)

