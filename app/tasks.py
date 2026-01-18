import logging
import time
import traceback
import re
from datetime import datetime
from io import BytesIO
from fastapi import UploadFile
from sqlmodel import Session, select
from app.adapters.database import engine
from app.models.portfolio import Portfolio
from app.models.job import Job, JobStatus
from app.services.ocr_service import ocr_service
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

async def process_resume_task(job_id: str, file_bytes: bytes, filename: str, content_type: str, user_id: str):
    """
    Background task to process resume and generate portfolio.
    
    This function:
    1. Updates job status throughout processing
    2. Persists errors to database for user visibility
    3. Creates portfolio record on success
    4. Handles file cleanup properly
    
    Args:
        job_id: Unique job identifier
        file_bytes: File content as bytes (read before passing to background task)
        filename: Original filename
        content_type: MIME type of the file
        user_id: User identifier
    """
    start_time = time.time()
    logger.info("=" * 60)
    logger.info(f"Job {job_id}: BACKGROUND TASK STARTED for User {user_id}")
    logger.info(f"Job {job_id}: File: {filename}, Type: {content_type}, Size: {len(file_bytes)} bytes")
    logger.info("=" * 60)
    
    # Create UploadFile from bytes for compatibility with OCR service
    file = UploadFile(
        filename=filename,
        file=BytesIO(file_bytes),
        headers={"content-type": content_type}
    )
    
    db = None
    try:
        # Update existing job to PROCESSING status (job was created in upload endpoint)
        with Session(engine) as db:
            job = db.exec(select(Job).where(Job.job_id == job_id)).first()
            if not job:
                logger.error(f"Job {job_id} not found in database. Cannot start processing.")
                return
            
            # Update job to processing status
            job.update_status(JobStatus.PROCESSING, "initialization")
            job.started_at = datetime.utcnow()
            job.progress_percentage = 10
            db.add(job)
            db.commit()
            logger.info(f"Job {job_id}: Updated to PROCESSING status")
        
        # Stage 1: Text Extraction (PyMuPDF for PDFs, Gemini Vision for images)
        try:
            with Session(engine) as db:
                job = db.exec(select(Job).where(Job.job_id == job_id)).first()
                if job:
                    job.update_status(JobStatus.OCR_EXTRACTING, "text_extraction")
                    job.progress_percentage = 20
                    db.add(job)
                    db.commit()
            
            raw_text = await ocr_service.extract_text(file)
            
            if not raw_text or not raw_text.strip():
                raise ValueError(f"Text extraction returned empty content for Job {job_id}")
            
            logger.info(f"Job {job_id}: Text extraction complete. Extracted {len(raw_text)} characters.")
            
        except Exception as ocr_error:
            error_type = type(ocr_error).__name__
            error_message = str(ocr_error)
            
            # Create user-friendly error message
            if "API" in error_type or "key" in error_message.lower():
                user_message = "Text extraction service configuration error. Please contact support."
            elif "timeout" in error_message.lower() or "time" in error_message.lower():
                user_message = "Text extraction timed out. The file may be too large or complex."
            elif "empty" in error_message.lower() or "no text" in error_message.lower():
                user_message = "Could not extract text from the file. Please ensure the file contains readable text."
            else:
                user_message = f"Failed to extract text from resume: {error_message}"
            
            error_details = {
                "stage": "text_extraction",
                "error_type": error_type,
                "error_message": error_message,
                "user_message": user_message,
                "traceback": traceback.format_exc()
            }
            
            with Session(engine) as db:
                job = db.exec(select(Job).where(Job.job_id == job_id)).first()
                if job:
                    job.mark_failed(user_message, error_details)
                    db.add(job)
                    db.commit()
                    logger.error(f"Job {job_id} failed at OCR stage: {error_message}")
            
            raise RuntimeError(user_message) from ocr_error
        
        # Stage 2: AI Generation
        try:
            with Session(engine) as db:
                job = db.exec(select(Job).where(Job.job_id == job_id)).first()
                if job:
                    job.update_status(JobStatus.AI_GENERATING, "ai_generation")
                    job.progress_percentage = 50
                    db.add(job)
                    db.commit()
            
            portfolio_json = await ai_service.generate_portfolio_content(raw_text)
            logger.info(f"Job {job_id}: AI generation complete. Saving to DB...")
            
        except Exception as ai_error:
            error_type = type(ai_error).__name__
            error_message = str(ai_error)
            
            # Create user-friendly error message
            if "API" in error_type or "key" in error_message.lower() or "authentication" in error_message.lower():
                user_message = "AI service configuration error. Please contact support."
            elif "quota" in error_message.lower() or "limit" in error_message.lower():
                user_message = "AI service quota exceeded. Please try again later."
            elif "timeout" in error_message.lower() or "time" in error_message.lower():
                user_message = "AI generation timed out. The resume may be too complex. Please try again."
            elif "validation" in error_message.lower() or "schema" in error_message.lower():
                user_message = "Generated portfolio data didn't meet quality standards. Please try again."
            else:
                user_message = f"Failed to generate portfolio content: {error_message}"
            
            error_details = {
                "stage": "ai_generation",
                "error_type": error_type,
                "error_message": error_message,
                "user_message": user_message,
                "traceback": traceback.format_exc()
            }
            
            with Session(engine) as db:
                job = db.exec(select(Job).where(Job.job_id == job_id)).first()
                if job:
                    job.mark_failed(user_message, error_details)
                    db.add(job)
                    db.commit()
                    logger.error(f"Job {job_id} failed at AI generation stage: {error_message}")
            
            raise RuntimeError(user_message) from ai_error
        
        # Stage 3: Validation & Saving
        try:
            with Session(engine) as db:
                job = db.exec(select(Job).where(Job.job_id == job_id)).first()
                if job:
                    job.update_status(JobStatus.VALIDATING, "saving_portfolio")
                    job.progress_percentage = 90
                    db.add(job)
                    db.commit()
            
            # Create portfolio record
            with Session(engine) as db:
                full_name = portfolio_json.get("hero", {}).get("name", "Aspiring Professional")
                # Generate slug from full name
                slug = _generate_slug(full_name, job_id)
                
                # Log portfolio content structure for debugging
                logger.info(f"Job {job_id}: Saving portfolio with content keys: {list(portfolio_json.keys())}")
                logger.info(f"Job {job_id}: Portfolio hero data: {portfolio_json.get('hero', {}).get('name', 'N/A')}")
                logger.info(f"Job {job_id}: Portfolio has {len(portfolio_json.get('projects', []))} projects")
                logger.info(f"Job {job_id}: Portfolio has {len(portfolio_json.get('skills', []))} skill categories")
                
                new_portfolio = Portfolio(
                    job_id=job_id,
                    user_id=user_id,
                    full_name=full_name,
                    email=portfolio_json.get("hero", {}).get("email"),
                    slug=slug,
                    content=portfolio_json,
                    is_published=False
                )
                
                db.add(new_portfolio)
                db.commit()
                db.refresh(new_portfolio)
                
                # Verify content was saved
                logger.info(f"Job {job_id}: Portfolio saved with ID {new_portfolio.id}")
                logger.info(f"Job {job_id}: Portfolio content type: {type(new_portfolio.content)}")
                logger.info(f"Job {job_id}: Portfolio content keys after save: {list(new_portfolio.content.keys()) if isinstance(new_portfolio.content, dict) else 'Not a dict'}")
                
                # Update job with portfolio ID and mark as completed
                job = db.exec(select(Job).where(Job.job_id == job_id)).first()
                if job:
                    job.portfolio_id = new_portfolio.id
                    duration = time.time() - start_time
                    job.mark_completed(duration)
                    db.add(job)
                    db.commit()
            
            duration = time.time() - start_time
            logger.info(f"Job {job_id}: Successfully completed in {duration:.2f}s")
            
        except Exception as save_error:
            error_type = type(save_error).__name__
            error_message = str(save_error)
            
            # Create user-friendly error message
            if "database" in error_message.lower() or "connection" in error_message.lower():
                user_message = "Database error while saving portfolio. Please try again."
            elif "constraint" in error_message.lower() or "unique" in error_message.lower():
                user_message = "Portfolio already exists for this job. Please check your portfolio list."
            elif "validation" in error_message.lower() or "schema" in error_message.lower():
                user_message = "Portfolio data validation failed. Please try uploading again."
            else:
                user_message = f"Failed to save portfolio: {error_message}"
            
            error_details = {
                "stage": "saving_portfolio",
                "error_type": error_type,
                "error_message": error_message,
                "user_message": user_message,
                "traceback": traceback.format_exc()
            }
            
            with Session(engine) as db:
                job = db.exec(select(Job).where(Job.job_id == job_id)).first()
                if job:
                    job.mark_failed(user_message, error_details)
                    db.add(job)
                    db.commit()
                    logger.error(f"Job {job_id} failed at saving stage: {error_message}")
            
            raise RuntimeError(user_message) from save_error

    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Job {job_id}: FAILED after {elapsed:.2f}s"
        logger.error(error_msg, exc_info=True)
        
        # Ensure error is persisted (if not already done in stage handlers)
        try:
            with Session(engine) as db:
                job = db.exec(select(Job).where(Job.job_id == job_id)).first()
                if job and job.status != JobStatus.FAILED:
                    error_details = {
                        "stage": job.current_stage or "unknown",
                        "error_type": type(e).__name__,
                        "traceback": traceback.format_exc()
                    }
                    job.mark_failed(str(e), error_details)
                    db.add(job)
                    db.commit()
        except Exception as db_error:
            logger.error(f"Failed to persist error to database: {db_error}", exc_info=True)

    finally:
        # File cleanup - this is the ONLY place we close the file
        try:
            await file.close()
            logger.debug(f"Resource cleanup for Job {job_id} finalized")
        except Exception as close_error:
            logger.warning(f"Error closing file for Job {job_id}: {close_error}")


def _generate_slug(name: str, job_id: str) -> str:
    """Generate a URL-friendly slug from name and job_id."""
    # Convert name to slug
    slug_base = re.sub(r'[^\w\s-]', '', name.lower())
    slug_base = re.sub(r'[-\s]+', '-', slug_base)
    slug_base = slug_base.strip('-')
    
    # Add job_id suffix to ensure uniqueness
    return f"{slug_base}-{job_id[:8]}" if slug_base else f"portfolio-{job_id[:8]}"
