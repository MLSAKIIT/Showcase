"""
Debug endpoints for verifying portfolio storage and content.
These endpoints should be disabled in production.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.api import dependencies
from app.models.portfolio import Portfolio
from app.models.job import Job
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.get("/portfolios")
async def list_all_portfolios(
    db: Session = Depends(dependencies.get_db),
    limit: int = 10
):
    """
    List all portfolios in the database (for debugging).
    WARNING: This should be disabled in production!
    """
    statement = select(Portfolio).limit(limit).order_by(Portfolio.created_at.desc())
    portfolios = db.exec(statement).all()
    
    result = []
    for p in portfolios:
        result.append({
            "id": str(p.id),
            "job_id": p.job_id,
            "user_id": p.user_id,
            "full_name": p.full_name,
            "slug": p.slug,
            "has_content": bool(p.content),
            "content_type": type(p.content).__name__,
            "content_keys": list(p.content.keys()) if isinstance(p.content, dict) else None,
            "content_summary": {
                "has_hero": bool(p.content.get("hero") if isinstance(p.content, dict) else False),
                "projects_count": len(p.content.get("projects", [])) if isinstance(p.content, dict) else 0,
                "skills_count": len(p.content.get("skills", [])) if isinstance(p.content, dict) else 0,
                "experience_count": len(p.content.get("experience", [])) if isinstance(p.content, dict) else 0,
            } if isinstance(p.content, dict) else None,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "is_published": p.is_published
        })
    
    return {
        "count": len(result),
        "portfolios": result
    }


@router.get("/portfolios/{job_id}/content")
async def get_portfolio_content(
    job_id: str,
    db: Session = Depends(dependencies.get_db)
):
    """
    Get full portfolio content for a specific job_id (for debugging).
    WARNING: This should be disabled in production!
    """
    statement = select(Portfolio).where(Portfolio.job_id == job_id)
    portfolio = db.exec(statement).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio not found for job_id: {job_id}"
        )
    
    return {
        "portfolio_id": str(portfolio.id),
        "job_id": portfolio.job_id,
        "full_name": portfolio.full_name,
        "content": portfolio.content,
        "content_type": type(portfolio.content).__name__,
        "content_size": len(str(portfolio.content)) if portfolio.content else 0
    }


@router.get("/jobs")
async def list_all_jobs(
    db: Session = Depends(dependencies.get_db),
    limit: int = 20
):
    """
    List all jobs in the database (for debugging).
    WARNING: This should be disabled in production!
    """
    statement = select(Job).limit(limit).order_by(Job.created_at.desc())
    jobs = db.exec(statement).all()
    
    result = []
    for j in jobs:
        result.append({
            "job_id": j.job_id,
            "user_id": j.user_id,
            "status": j.status.value if j.status else None,
            "progress_percentage": j.progress_percentage,
            "current_stage": j.current_stage,
            "has_portfolio": bool(j.portfolio_id),
            "portfolio_id": str(j.portfolio_id) if j.portfolio_id else None,
            "error_message": j.error_message,
            "error_details": j.error_details,
            "started_at": j.started_at.isoformat() if j.started_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            "duration_seconds": j.duration_seconds,
            "created_at": j.created_at.isoformat() if j.created_at else None
        })
    
    return {
        "count": len(result),
        "jobs": result
    }


@router.get("/jobs/{job_id}")
async def get_job_details(
    job_id: str,
    db: Session = Depends(dependencies.get_db)
):
    """
    Get detailed information about a specific job (for debugging).
    WARNING: This should be disabled in production!
    """
    # Get job
    job_statement = select(Job).where(Job.job_id == job_id)
    job = db.exec(job_statement).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found in database."
        )
    
    # Check if portfolio exists
    portfolio_statement = select(Portfolio).where(Portfolio.job_id == job_id)
    portfolio = db.exec(portfolio_statement).first()
    
    result = {
        "job": {
            "job_id": job.job_id,
            "user_id": job.user_id,
            "status": job.status.value if job.status else None,
            "progress_percentage": job.progress_percentage,
            "current_stage": job.current_stage,
            "has_portfolio_id": bool(job.portfolio_id),
            "portfolio_id": str(job.portfolio_id) if job.portfolio_id else None,
            "error_message": job.error_message,
            "error_details": job.error_details,
            "original_filename": job.original_filename,
            "file_type": job.file_type,
            "file_size": job.file_size,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "duration_seconds": job.duration_seconds,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        },
        "portfolio": None,
        "diagnosis": {}
    }
    
    if portfolio:
        result["portfolio"] = {
            "id": str(portfolio.id),
            "job_id": portfolio.job_id,
            "user_id": portfolio.user_id,
            "full_name": portfolio.full_name,
            "slug": portfolio.slug,
            "has_content": bool(portfolio.content),
            "content_type": type(portfolio.content).__name__,
            "content_keys": list(portfolio.content.keys()) if isinstance(portfolio.content, dict) else None,
            "created_at": portfolio.created_at.isoformat() if portfolio.created_at else None,
        }
        result["diagnosis"]["portfolio_status"] = "✅ Portfolio exists"
    else:
        result["diagnosis"]["portfolio_status"] = "❌ Portfolio NOT found"
        
        # Check if job has portfolio_id but portfolio doesn't exist (orphaned reference)
        if job.portfolio_id:
            result["diagnosis"]["warning"] = f"⚠️ Job has portfolio_id ({job.portfolio_id}) but portfolio record not found - possible orphaned reference"
        
        # Provide diagnosis based on job status
        if job.status.value == "failed":
            result["diagnosis"]["reason"] = "Job failed before portfolio creation"
            result["diagnosis"]["error_stage"] = job.error_details.get("stage") if job.error_details else None
        elif job.status.value in ["pending", "processing", "ocr_extracting", "ai_generating", "validating"]:
            result["diagnosis"]["reason"] = "Job is still processing - portfolio will be created when job completes"
        elif job.status.value == "completed":
            result["diagnosis"]["reason"] = "⚠️ Job marked as completed but portfolio not found - possible database issue"
        else:
            result["diagnosis"]["reason"] = f"Unknown status: {job.status.value}"
    
    return result
