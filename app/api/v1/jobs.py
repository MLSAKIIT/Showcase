from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.api import dependencies
from app.models.job import Job, JobStatus

router = APIRouter()


@router.get("/{job_id}")
async def get_job_status(
    job_id: str,
    db: Session = Depends(dependencies.get_db),
):
    """
    Get the status of a job by job_id.
    
    Returns:
    - Job status (pending, processing, completed, failed)
    - Progress percentage
    - Current stage
    - Error message (if failed)
    - Duration (if completed)
    """
    statement = select(Job).where(Job.job_id == job_id)
    job = db.exec(statement).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Job not found",
                "message": f"No job found with ID: {job_id}",
                "job_id": job_id,
                "suggestion": "Please verify the job ID is correct. You may need to upload your resume again."
            }
        )

    # Build response
    response = {
        "job_id": job.job_id,
        "status": job.status.value,
        "progress_percentage": job.progress_percentage,
        "current_stage": job.current_stage,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
    }

    # Add timing information
    if job.started_at:
        response["started_at"] = job.started_at.isoformat()
    if job.completed_at:
        response["completed_at"] = job.completed_at.isoformat()
    if job.duration_seconds is not None:
        response["duration_seconds"] = job.duration_seconds

    # Add error information if failed
    if job.status == JobStatus.FAILED:
        error_info = {
            "message": job.error_message,
            "stage": job.current_stage,
            "details": job.error_details,
        }
        
        # Add user-friendly suggestions based on error stage
        if job.current_stage == "ocr_extraction":
            error_info["suggestion"] = "The file may be corrupted or unreadable. Please try uploading a different file or ensure the file contains clear, readable text."
        elif job.current_stage == "ai_generation":
            error_info["suggestion"] = "AI generation failed. This may be due to service limits or the resume content. Please try again in a few moments."
        elif job.current_stage == "saving_portfolio":
            error_info["suggestion"] = "Portfolio creation failed. Please try uploading your resume again."
        else:
            error_info["suggestion"] = "Please try uploading your resume again. If the problem persists, contact support."
        
        response["error"] = error_info

    # Add portfolio ID if completed
    if job.status == JobStatus.COMPLETED and job.portfolio_id:
        response["portfolio_id"] = str(job.portfolio_id)

    return response


@router.get("/{job_id}/status")
async def get_job_status_simple(
    job_id: str,
    db: Session = Depends(dependencies.get_db),
):
    """
    Simple endpoint returning just the job status.
    Useful for polling.
    """
    statement = select(Job).where(Job.job_id == job_id)
    job = db.exec(statement).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Job not found",
                "message": f"No job found with ID: {job_id}",
                "job_id": job_id,
                "suggestion": "Please verify the job ID is correct. You may need to upload your resume again."
            }
        )

    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "progress": job.progress_percentage,
    }
