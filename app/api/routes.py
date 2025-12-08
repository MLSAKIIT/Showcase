"""
FastAPI route handlers.
"""
import os
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Job, JobStatus, Artifact
from app.tasks import process_resume_task, deploy_to_vercel_task

router = APIRouter()


@router.post("/resumes/upload")
async def upload_resume(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Upload a resume file and start processing pipeline.
    Returns job_id for tracking.
    """
    # Validate file type
    allowed_extensions = {".pdf", ".png", ".jpg", ".jpeg", ".docx"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Create job record
    job = Job(status=JobStatus.PENDING)
    db.add(job)
    db.commit()
    db.refresh(job)

    # Save uploaded file
    uploads_dir = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    
    file_path = os.path.join(uploads_dir, f"{job.id}_{file.filename}")
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Update job metadata
    job.metadata = {"original_filename": file.filename, "file_path": file_path}
    db.commit()

    # Queue background task
    process_resume_task.delay(job.id)

    return {"job_id": job.id, "status": job.status.value, "message": "Resume uploaded and processing started"}


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """
    Get job status, logs, and artifact URLs.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get artifact URLs
    artifacts = db.query(Artifact).filter(Artifact.job_id == job_id).all()
    artifact_urls = {
        artifact.artifact_type: artifact.file_url or f"/api/v1/artifacts/{artifact.id}"
        for artifact in artifacts
    }

    # Get chat messages as logs
    logs = [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.created_at.isoformat()
        }
        for msg in job.chat_messages
    ]

    return {
        "job_id": job.id,
        "status": job.status.value,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
        "error_message": job.error_message,
        "artifacts": artifact_urls,
        "logs": logs,
    }


@router.get("/preview/{job_id}")
async def preview_job(job_id: int, db: Session = Depends(get_db)):
    """
    Serve preview page for a job (Next.js static route).
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if preview artifact exists
    preview_artifact = db.query(Artifact).filter(
        Artifact.job_id == job_id,
        Artifact.artifact_type == "preview"
    ).first()

    if not preview_artifact:
        raise HTTPException(status_code=404, detail="Preview not yet generated")

    preview_path = preview_artifact.file_path
    if os.path.exists(preview_path):
        return FileResponse(preview_path)
    
    raise HTTPException(status_code=404, detail="Preview file not found")


@router.post("/jobs/{job_id}/deploy")
async def deploy_job(
    job_id: int,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Trigger Vercel deployment for a job's frontend bundle.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Job must be completed before deployment. Current status: {job.status.value}"
        )

    # Check if frontend bundle exists
    bundle_artifact = db.query(Artifact).filter(
        Artifact.job_id == job_id,
        Artifact.artifact_type == "frontend_bundle"
    ).first()

    if not bundle_artifact:
        raise HTTPException(status_code=404, detail="Frontend bundle not found")

    # Queue deployment task
    deploy_to_vercel_task.delay(job_id)

    return {
        "job_id": job_id,
        "message": "Deployment started",
        "bundle_path": bundle_artifact.file_path
    }

