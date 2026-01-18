"""
Text extraction service using PyMuPDF for PDF files.
"""
import logging
import io
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MIN_TEXT_LENGTH = 10  # Minimum expected text length after extraction

class TextExtractionService:
    """
    Text extraction service for PDF files using PyMuPDF.
    
    Only supports PDF files - no OCR for images.
    """
    
    async def extract_text(self, file: UploadFile) -> str:
        """
        Extract text from uploaded PDF file using PyMuPDF.
        
        Supports:
        - PDF files (application/pdf) only
        
        Note: This method does NOT close the file. The caller is responsible
        for closing it after all processing is complete.
        """
        try:
            # Reset file position
            await file.seek(0)
            
            # Validate file type
            if not file.content_type:
                raise ValueError("File content type is missing")
            
            # Only support PDFs
            if file.content_type != "application/pdf":
                raise ValueError(
                    f"Unsupported file type: {file.content_type}. "
                    f"Only PDF files are supported."
                )

            # Read file content
            content = await file.read()
            
            if not content:
                raise ValueError("File is empty or could not be read")

            if len(content) > MAX_FILE_SIZE:
                raise ValueError(
                    f"File size ({len(content) / 1024 / 1024:.2f}MB) exceeds "
                    f"the maximum allowed size ({MAX_FILE_SIZE / 1024 / 1024}MB)"
                )

            # Reset file position for potential reuse by caller
            await file.seek(0)
            
            logger.info(
                f"Extracting text from PDF: {file.filename}, "
                f"size: {len(content)} bytes"
            )
            
            # Extract text from PDF
            extracted_text = await self._extract_from_pdf(content, file.filename)
            
            # Validate extracted text
            if not extracted_text:
                raise ValueError(
                    "No text could be extracted from the PDF. "
                    "The PDF may be corrupted, empty, or contain only images without text."
                )
            
            if len(extracted_text.strip()) < MIN_TEXT_LENGTH:
                logger.warning(
                    f"Extracted text is very short ({len(extracted_text)} chars). "
                    f"File: {file.filename}"
                )
                # Still return it, but log a warning
            
            logger.info(
                f"Successfully extracted {len(extracted_text)} characters "
                f"from {file.filename}"
            )
            
            return extracted_text.strip()

        except ValueError as ve:
            logger.error(f"Text extraction validation error: {ve}")
            raise HTTPException(
                status_code=400, 
                detail={
                    "error": "File validation failed",
                    "message": str(ve),
                    "suggestion": "Please ensure the file is a valid PDF with readable text."
                }
            )
        except Exception as e:
            logger.error(f"Unexpected text extraction error: {e}", exc_info=True)
            raise RuntimeError(
                f"Text extraction failed: {str(e)}. "
                "Please try uploading the file again or contact support."
            )
    
    async def _extract_from_pdf(self, pdf_bytes: bytes, filename: str) -> str:
        """
        Extract text from PDF using PyMuPDF (fitz).
        
        This is fast and reliable for PDFs with text content.
        """
        pdf_document = None
        try:
            import fitz  # PyMuPDF
            
            logger.info(f"Extracting text from PDF using PyMuPDF: {filename}")
            
            # Create a BytesIO object from the bytes to ensure it's a proper stream
            pdf_stream = io.BytesIO(pdf_bytes)
            
            # Open PDF from bytes stream
            pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")
            
            if pdf_document.page_count == 0:
                raise ValueError("PDF has no pages")
            
            # Extract text from all pages
            text_parts = []
            page_count = pdf_document.page_count
            
            for page_num in range(page_count):
                page = pdf_document[page_num]
                page_text = page.get_text()
                if page_text.strip():
                    text_parts.append(page_text)
            
            # Store page count before closing
            extracted_text = "\n\n".join(text_parts)
            
            # Close document properly
            if pdf_document:
                pdf_document.close()
                pdf_document = None
            
            if not text_parts:
                raise ValueError("No text found in PDF. The PDF may contain only images without text.")
            
            logger.info(
                f"Extracted {len(extracted_text)} characters from {page_count} page(s)"
            )
            
            return extracted_text
            
        except ImportError:
            raise RuntimeError(
                "PyMuPDF (fitz) is not installed. "
                "Please install it with: pip install pymupdf"
            )
        except Exception as e:
            error_msg = str(e)
            logger.error(f"PyMuPDF extraction failed: {error_msg}", exc_info=True)
            
            # Ensure document is closed even on error
            if pdf_document:
                try:
                    pdf_document.close()
                except:
                    pass
            
            if "not a PDF" in error_msg.lower() or "invalid" in error_msg.lower():
                raise ValueError(f"Invalid PDF file: {error_msg}")
            elif "closed" in error_msg.lower():
                raise RuntimeError(
                    f"PDF document was closed prematurely. "
                    f"This may indicate a file handling issue. Error: {error_msg}"
                )
            else:
                raise RuntimeError(f"PDF text extraction failed: {error_msg}")

# Keep the old name for backward compatibility
ocr_service = TextExtractionService()
