from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.api import dependencies
from app.core.security import verify_firebase_token
from app.models.portfolio import Portfolio
from app.models.job import Job, JobStatus
from app.schemas.portfolio import PortfolioUpdate
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

#PRIVATE ROUTES (Requires Google Login)

@router.get("/me", response_model=List[Portfolio])
async def get_my_portfolios(
    db: Session = Depends(dependencies.get_db),
    current_user: dict = Depends(verify_firebase_token)
):
    user_id = current_user.get("uid")
    statement = (
        select(Portfolio)
        .where(Portfolio.user_id == user_id)
        .order_by(Portfolio.created_at.desc())
    )
    results = db.exec(statement).all()
    return results

@router.get("/{job_id}")
async def get_portfolio_by_job(
    job_id: str,
    db: Session = Depends(dependencies.get_db),
    # Relaxed auth for demo polling
    # current_user: dict = Depends(verify_firebase_token)
):
    """
    Get portfolio by job_id.
    
    If portfolio doesn't exist yet, returns job status information
    to help user understand if it's still processing or failed.
    """
    statement = select(Portfolio).where(Portfolio.job_id == job_id)
    portfolio = db.exec(statement).first()

    if portfolio:
        # Portfolio exists, return it
        # Log for debugging
        logger.info(f"Portfolio found for job_id {job_id}: ID={portfolio.id}, Name={portfolio.full_name}")
        logger.info(f"Portfolio content type: {type(portfolio.content)}, Keys: {list(portfolio.content.keys()) if isinstance(portfolio.content, dict) else 'N/A'}")
        if isinstance(portfolio.content, dict):
            logger.info(f"Portfolio content summary: hero={bool(portfolio.content.get('hero'))}, projects={len(portfolio.content.get('projects', []))}, skills={len(portfolio.content.get('skills', []))}")
        return portfolio
    
    # Portfolio doesn't exist - check job status
    job_statement = select(Job).where(Job.job_id == job_id)
    job = db.exec(job_statement).first()
    
    if not job:
        # Neither portfolio nor job exists
        logger.warning(f"Portfolio lookup failed: Neither portfolio nor job found for job_id {job_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Job {job_id} not found. Please check your job_id and try again.",
                "job_id": job_id,
                "suggestion": "Verify the job_id is correct. You can check all jobs at /api/v1/debug/jobs (development only)"
            }
        )
    
    # Job exists but portfolio doesn't - provide helpful status info
    logger.warning(f"Portfolio not found for job_id {job_id}, but job exists with status: {job.status.value}")
    
    if job.status == JobStatus.FAILED:
        error_info = {
            "message": job.error_message,
            "stage": job.current_stage,
            "details": job.error_details
        } if job.error_message else None
        
        logger.error(f"Job {job_id} failed: {job.error_message}")
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail={
                "message": "Portfolio generation failed.",
                "job_id": job_id,
                "status": job.status.value,
                "error": error_info,
                "suggestion": "Please try uploading your resume again or check the error details.",
                "debug_endpoint": f"/api/v1/debug/jobs/{job_id} (development only)"
            }
        )
    elif job.status in [JobStatus.PENDING, JobStatus.PROCESSING, JobStatus.OCR_EXTRACTING, 
                        JobStatus.AI_GENERATING, JobStatus.VALIDATING]:
        # Still processing
        logger.info(f"Job {job_id} still processing: {job.status.value} at {job.current_stage} ({job.progress_percentage}%)")
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail={
                "message": "Portfolio is still being generated. Please check back in a moment.",
                "job_id": job_id,
                "status": job.status.value,
                "progress_percentage": job.progress_percentage,
                "current_stage": job.current_stage,
                "suggestion": f"Check job status at /api/v1/jobs/{job_id} or wait a few seconds and try again.",
                "debug_endpoint": f"/api/v1/debug/jobs/{job_id} (development only)"
            }
        )
    elif job.status == JobStatus.COMPLETED:
        # Job completed but portfolio missing - this is a problem!
        logger.error(f"Job {job_id} marked as COMPLETED but portfolio not found! This indicates a database issue.")
        logger.error(f"Job portfolio_id: {job.portfolio_id}, Job completed_at: {job.completed_at}")
        
        # Check if portfolio exists with different job_id (unlikely but possible)
        all_portfolios = db.exec(select(Portfolio)).all()
        logger.warning(f"Total portfolios in DB: {len(all_portfolios)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Portfolio not found despite job completion. This may indicate a database issue.",
                "job_id": job_id,
                "status": job.status.value,
                "job_portfolio_id": str(job.portfolio_id) if job.portfolio_id else None,
                "suggestion": "Please contact support or try uploading your resume again.",
                "debug_endpoint": f"/api/v1/debug/jobs/{job_id} (development only)"
            }
        )
    else:
        # Unknown status
        logger.warning(f"Job {job_id} has unknown status: {job.status.value}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Portfolio not found.",
                "job_id": job_id,
                "status": job.status.value,
                "suggestion": f"Check job status at /api/v1/jobs/{job_id} for more information.",
                "debug_endpoint": f"/api/v1/debug/jobs/{job_id} (development only)"
            }
        )

@router.patch("/{job_id}/publish", response_model=Portfolio)
async def update_portfolio_settings(
    job_id: str,
    update_data: PortfolioUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: dict = Depends(verify_firebase_token)
):
    statement = select(Portfolio).where(Portfolio.job_id == job_id)
    db_portfolio = db.exec(statement).first()

    if not db_portfolio:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Portfolio not found",
                "message": f"No portfolio found for job_id: {job_id}",
                "job_id": job_id,
                "suggestion": "Please verify the job_id is correct or check if the portfolio generation completed successfully."
            }
        )
    
    if db_portfolio.user_id != current_user.get("uid"):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Unauthorized",
                "message": "You don't have permission to update this portfolio.",
                "job_id": job_id,
                "suggestion": "This portfolio belongs to a different user. Please use your own portfolio."
            }
        )

    obj_data = update_data.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_portfolio, key, value)

    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

#PUBLIC ROUTES (No Login Required)

@router.get("/public/{slug}", response_model=Portfolio)
async def get_public_portfolio(
    slug: str,
    db: Session = Depends(dependencies.get_db)
):
    statement = select(Portfolio).where(
        Portfolio.slug == slug,
        Portfolio.is_published == True
    )
    portfolio = db.exec(statement).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Portfolio not found",
                "message": f"No public portfolio found with slug: {slug}",
                "slug": slug,
                "possible_reasons": [
                    "The portfolio doesn't exist",
                    "The portfolio is not published (is_published=False)",
                    "The slug is incorrect"
                ],
                "suggestion": "Please verify the slug is correct or contact the portfolio owner."
            }
        )
    return portfolio
