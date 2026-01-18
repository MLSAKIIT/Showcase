import uuid
import os
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select
from app.schemas.resume import ResumeUploadResponse
from app.tasks import process_resume_task
from app.api import dependencies
from app.core.security import verify_firebase_token
from app.models.job import Job, JobStatus
from app.services.ocr_service import ocr_service

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.get("/metadata/{job_id}")
async def get_file_metadata(
    job_id: str,
    db: Session = Depends(dependencies.get_db),
):
    """
    Get comprehensive file metadata for an uploaded resume.
    
    Returns detailed information about the uploaded file including:
    - File information (name, size, type, format)
    - Upload information (timestamp, user)
    - Processing status and progress
    - Related portfolio information (if available)
    """
    statement = select(Job).where(Job.job_id == job_id)
    job = db.exec(statement).first()
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "File metadata not found",
                "message": f"No file metadata found for job_id: {job_id}",
                "job_id": job_id,
                "suggestion": "The resume may not have been uploaded, or the job_id is incorrect."
            }
        )
    
    # Extract file extension and format
    file_extension = None
    file_format = None
    if job.original_filename:
        parts = job.original_filename.rsplit('.', 1)
        if len(parts) == 2:
            file_extension = parts[1].lower()
            format_map = {
                'pdf': 'PDF Document',
                'png': 'PNG Image',
                'jpg': 'JPEG Image',
                'jpeg': 'JPEG Image',
                'docx': 'Word Document'
            }
            file_format = format_map.get(file_extension, 'Unknown')
    
    # Calculate human-readable file size
    file_size_kb = None
    file_size_mb = None
    if job.file_size:
        file_size_kb = round(job.file_size / 1024, 2)
        file_size_mb = round(job.file_size / 1024 / 1024, 2)
    
    # Build comprehensive metadata response
    metadata = {
        "file": {
            "filename": job.original_filename,
            "extension": file_extension,
            "format": file_format,
            "mime_type": job.file_type,
            "size": {
                "bytes": job.file_size,
                "kilobytes": file_size_kb,
                "megabytes": file_size_mb,
                "human_readable": f"{file_size_mb} MB" if file_size_mb and file_size_mb >= 1 else f"{file_size_kb} KB" if file_size_kb else "0 bytes"
            }
        },
        "upload": {
            "job_id": job.job_id,
            "user_id": job.user_id,
            "uploaded_at": job.created_at.isoformat() if job.created_at else None,
            "uploaded_timestamp": job.created_at.timestamp() if job.created_at else None,
            "upload_status": "success" if job.original_filename else "unknown"
        },
        "processing": {
            "status": job.status.value,
            "progress_percentage": job.progress_percentage,
            "current_stage": job.current_stage,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "duration_seconds": job.duration_seconds,
            "is_completed": job.status.value == "completed",
            "is_failed": job.status.value == "failed",
            "is_processing": job.status.value in ["processing", "ocr_extracting", "ai_generating", "validating"]
        },
        "error": None,
        "portfolio": None
    }
    
    # Add error information if failed
    if job.status.value == "failed":
        metadata["error"] = {
            "message": job.error_message,
            "stage": job.current_stage,
            "details": job.error_details,
            "occurred_at": job.completed_at.isoformat() if job.completed_at else None
        }
    
    # Add portfolio information if available
    if job.portfolio_id:
        from app.models.portfolio import Portfolio
        portfolio_statement = select(Portfolio).where(Portfolio.id == job.portfolio_id)
        portfolio = db.exec(portfolio_statement).first()
        if portfolio:
            metadata["portfolio"] = {
                "portfolio_id": str(portfolio.id),
                "slug": portfolio.slug,
                "full_name": portfolio.full_name,
                "is_published": portfolio.is_published,
                "created_at": portfolio.created_at.isoformat() if portfolio.created_at else None
            }
    
    return {
        "success": True,
        "metadata": metadata,
        "summary": {
            "file_name": job.original_filename,
            "file_size": metadata["file"]["size"]["human_readable"],
            "status": job.status.value,
            "has_portfolio": bool(job.portfolio_id)
        }
    }


@router.get("/upload/{job_id}")
async def confirm_resume_upload(
    job_id: str,
    db: Session = Depends(dependencies.get_db),
):
    """
    Confirm if a resume was uploaded and stored in the database.
    
    Returns:
    - Upload confirmation status
    - File metadata (filename, size, type)
    - Upload timestamp
    - Job status
    """
    statement = select(Job).where(Job.job_id == job_id)
    job = db.exec(statement).first()
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Resume upload not found",
                "message": f"No resume upload found for job_id: {job_id}",
                "job_id": job_id,
                "uploaded": False,
                "suggestion": "The resume may not have been uploaded, or the job_id is incorrect."
            }
        )
    
    # Resume upload confirmed - return metadata
    return {
        "uploaded": True,
        "confirmed": True,
        "job_id": job.job_id,
        "file_metadata": {
            "filename": job.original_filename,
            "file_size": job.file_size,
            "file_size_mb": round(job.file_size / 1024 / 1024, 2) if job.file_size else None,
            "file_type": job.file_type,
            "uploaded_at": job.created_at.isoformat() if job.created_at else None,
        },
        "job_status": {
            "status": job.status.value,
            "progress_percentage": job.progress_percentage,
            "current_stage": job.current_stage,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        },
        "message": f"Resume '{job.original_filename}' was successfully uploaded and recorded in the database.",
        "note": "The file content itself is not stored - only metadata. The file is processed in memory."
    }


@router.get("/uploads")
async def list_my_uploads(
    db: Session = Depends(dependencies.get_db),
    limit: int = 20,
    # current_user: dict = Depends(verify_firebase_token)  # Uncomment for auth
):
    """
    List all resume uploads for the current user.
    
    Note: Currently returns all uploads (for demo). Uncomment auth for user-specific results.
    """
    # For demo: get all jobs, or filter by user_id if auth is enabled
    # user_id = current_user.get("uid") if current_user else None
    
    statement = select(Job).order_by(Job.created_at.desc()).limit(limit)
    # if user_id:
    #     statement = statement.where(Job.user_id == user_id)
    
    jobs = db.exec(statement).all()
    
    uploads = []
    for job in jobs:
        uploads.append({
            "job_id": job.job_id,
            "filename": job.original_filename,
            "file_size": job.file_size,
            "file_size_mb": round(job.file_size / 1024 / 1024, 2) if job.file_size else None,
            "file_type": job.file_type,
            "status": job.status.value,
            "progress_percentage": job.progress_percentage,
            "uploaded_at": job.created_at.isoformat() if job.created_at else None,
            "has_portfolio": bool(job.portfolio_id),
            "portfolio_id": str(job.portfolio_id) if job.portfolio_id else None,
        })
    
    return {
        "count": len(uploads),
        "uploads": uploads,
        "message": f"Found {len(uploads)} resume upload(s) in the database."
    }

@router.post("/upload", response_model=ResumeUploadResponse, status_code=202)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(dependencies.get_db),
    # Allow guest uploads for public demo
    # current_user: dict = Depends(verify_firebase_token) 
):
    """
    Upload a resume file for processing.
    
    Validates file type and size, creates a job record, and starts background processing.
    """
    # Mock user for public demo or extract from token manually if present
    current_user = {"uid": "guest_" + str(uuid.uuid4())[:8], "email": "guest@showcase.ai"}

    # Validate file extension
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Missing filename",
                "message": "The uploaded file must have a filename.",
                "suggestion": "Please ensure your file has a name before uploading."
            }
        )
    
    file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ""
    if not file.filename.lower().endswith((".pdf",)):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Unsupported file format",
                "message": f"File format '.{file_ext}' is not supported.",
                "supported_formats": ["PDF"],
                "received_format": file_ext.upper() if file_ext else "Unknown",
                "suggestion": "Please upload a PDF file."
            }
        )
    
    # Validate file size and read content into memory
    # IMPORTANT: Read file content before passing to background task
    # because the file stream will be closed after the response is sent
    try:
        file_content = await file.read()
        file_size = len(file_content)
        # Don't reset - we'll pass the bytes to the background task
    except Exception as read_error:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "File read error",
                "message": f"Could not read the uploaded file: {str(read_error)}",
                "suggestion": "Please ensure the file is not corrupted and try again."
            }
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Empty file",
                "message": "The uploaded file is empty (0 bytes).",
                "filename": file.filename,
                "suggestion": "Please upload a file that contains content."
            }
        )
    
    if file_size > MAX_FILE_SIZE:
        file_size_mb = file_size / 1024 / 1024
        max_size_mb = MAX_FILE_SIZE / 1024 / 1024
        raise HTTPException(
            status_code=400,
            detail={
                "error": "File too large",
                "message": f"File size ({file_size_mb:.2f}MB) exceeds the maximum allowed size ({max_size_mb}MB).",
                "file_size_mb": round(file_size_mb, 2),
                "max_size_mb": max_size_mb,
                "filename": file.filename,
                "suggestion": f"Please compress your file or use a smaller file (max {max_size_mb}MB)."
            }
        )
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    user_id = current_user.get("uid")

    # Create job record with PENDING status
    try:
        job = Job(
            job_id=job_id,
            user_id=user_id,
            status=JobStatus.PENDING,
            original_filename=file.filename,
            file_size=file_size,
            file_type=file.content_type,
        )
        db.add(job)
        db.commit()
    except Exception as db_error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Database error",
                "message": f"Failed to create job record: {str(db_error)}",
                "suggestion": "Please try again. If the problem persists, contact support."
            }
        )

    # Start background processing
    # IMPORTANT: Pass file_bytes instead of file object
    # because the file stream will be closed after response is sent
    try:
        import logging
        task_logger = logging.getLogger(__name__)
        task_logger.info(f"Adding background task for job_id: {job_id}")
        task_logger.info(f"File: {file.filename}, Size: {file_size} bytes, Type: {file.content_type}")
        
        # Pass file content as bytes to background task
        background_tasks.add_task(
            process_resume_task, 
            job_id, 
            file_content,  # Pass bytes instead of file object
            file.filename,
            file.content_type,
            user_id
        )
        
        task_logger.info(f"Background task queued successfully for job_id: {job_id}")
    except Exception as task_error:
        # If background task fails to queue, mark job as failed
        job.status = JobStatus.FAILED
        job.error_message = f"Failed to start background processing: {str(task_error)}"
        db.add(job)
        db.commit()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Processing initialization failed",
                "message": "The file was received but we couldn't start processing it.",
                "job_id": job_id,
                "suggestion": "Please try uploading again. If the problem persists, contact support."
            }
        )

    return {
        "job_id": job_id,
        "status": "pending",
        "message": f"Resume received for {current_user.get('email')}. Portfolio design in progress.",
        "next_steps": {
            "check_status": f"Use job_id '{job_id}' to check status at /api/v1/jobs/{job_id}",
            "estimated_time": "Processing typically takes 30-60 seconds"
        }
    }


@router.post("/extract-text")
async def extract_text_from_file(
    file: UploadFile = File(...),
    db: Session = Depends(dependencies.get_db),
):
    """
    Extract text from an uploaded file (PDF or image) and return it immediately.
    
    This is a test/debug endpoint to verify text extraction is working.
    Does NOT create a job or process the file further.
    
    Returns:
        - Extracted text
        - File metadata
        - Extraction statistics
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Missing filename",
                    "message": "The uploaded file must have a filename."
                }
            )
        
        file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ""
        if not file.filename.lower().endswith((".pdf",)):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Unsupported file format",
                    "message": f"File format '.{file_ext}' is not supported.",
                    "supported_formats": ["PDF"],
                    "suggestion": "Please upload a PDF file."
                }
            )
        
        # Read file to get size and content
        await file.seek(0)
        file_content = await file.read()
        file_size = len(file_content)
        
        # Create a new UploadFile from the bytes for the OCR service
        # This ensures the file stream is fresh and not closed
        from io import BytesIO
        file_for_extraction = UploadFile(
            filename=file.filename,
            file=BytesIO(file_content),
            headers={"content-type": file.content_type}
        )
        
        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Empty file",
                    "message": "The uploaded file is empty (0 bytes)."
                }
            )
        
        if file_size > MAX_FILE_SIZE:
            file_size_mb = file_size / 1024 / 1024
            max_size_mb = MAX_FILE_SIZE / 1024 / 1024
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "File too large",
                    "message": f"File size ({file_size_mb:.2f}MB) exceeds maximum ({max_size_mb}MB)."
                }
            )
        
        # Extract text
        import time
        start_time = time.time()
        
        extracted_text = await ocr_service.extract_text(file_for_extraction)
        
        extraction_time = time.time() - start_time
        
        # Calculate statistics
        word_count = len(extracted_text.split())
        char_count = len(extracted_text)
        line_count = len(extracted_text.split('\n'))
        
        # Extraction method
        extraction_method = "PyMuPDF"
        
        return {
            "success": True,
            "file": {
                "filename": file.filename,
                "content_type": file.content_type,
                "size_bytes": file_size,
                "size_mb": round(file_size / 1024 / 1024, 2)
            },
            "extraction": {
                "method": extraction_method,
                "time_seconds": round(extraction_time, 3),
                "text_length": char_count,
                "word_count": word_count,
                "line_count": line_count
            },
            "text": extracted_text,
            "preview": {
                "first_500_chars": extracted_text[:500],
                "last_500_chars": extracted_text[-500:] if len(extracted_text) > 500 else extracted_text
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Text extraction failed",
                "message": str(e)
            }
        )
    finally:
        # Clean up files
        try:
            await file.close()
            if 'file_for_extraction' in locals():
                await file_for_extraction.close()
        except:
            pass
