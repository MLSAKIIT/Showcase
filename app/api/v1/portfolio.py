import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from app.api import dependencies
from app.core.security import verify_firebase_token
from app.models.portfolio import Portfolio
from app.models.job import Job, JobStatus
from app.schemas.portfolio import PortfolioUpdate
from app.schemas.responses import APIResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# New Schemas for Template/AI Endpoints
# ============================================================================

class ColorScheme(BaseModel):
    """Color preferences for template customization."""
    primary: str = Field(default="#3B82F6", description="Primary brand color")
    secondary: str = Field(default="#6B7280", description="Secondary color")
    accent: str = Field(default="#10B981", description="Accent color")


class FeatureToggles(BaseModel):
    """Feature toggles for template customization."""
    dark_mode: bool = Field(default=True)
    animations: bool = Field(default=True)
    contact_form: bool = Field(default=True)


class CustomizationRequest(BaseModel):
    """Request for customizing a portfolio template."""
    template_id: str
    colors: Optional[ColorScheme] = None
    features: Optional[FeatureToggles] = None
    custom_instructions: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request for AI customization."""
    message: str
    job_id: Optional[str] = None
    template_id: Optional[str] = None


# ============================================================================
# Existing Portfolio CRUD Endpoints
# ============================================================================



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


# ============================================================================
# New Template & AI Endpoints
# ============================================================================

@router.get("/templates", response_model=APIResponse)
async def list_templates():
    """
    List all available portfolio templates.
    """
    try:
        from agents.tools.template_tools import TemplateRegistryTools
        
        tools = TemplateRegistryTools()
        templates_json = tools.list_templates()
        templates = json.loads(templates_json)
        
        return APIResponse.success(data={"templates": templates})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}", response_model=APIResponse)
async def get_template(template_id: str):
    """
    Get detailed information about a specific template.
    """
    try:
        from agents.tools.template_tools import TemplateRegistryTools
        
        tools = TemplateRegistryTools()
        template_json = tools.get_template(template_id)
        
        if "not found" in template_json.lower():
            raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")
        
        template = json.loads(template_json)
        return APIResponse.success(data=template)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/customize", response_model=APIResponse)
async def customize_portfolio_template(
    request: CustomizationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(dependencies.get_db),
):
    """
    Customize a portfolio template with colors, features, and AI instructions.
    """
    try:
        from agents.tools.file_tools import FileSystemTools
        
        file_tools = FileSystemTools()
        copy_result = file_tools.copy_template(request.template_id)
        
        if "Error" in copy_result:
            raise HTTPException(status_code=400, detail=copy_result)
        
        customizations = []
        if request.colors:
            customizations.append(f"Colors: {request.colors.primary}")
        if request.features:
            customizations.append(f"Dark mode: {request.features.dark_mode}")
        if request.custom_instructions:
            customizations.append(f"Custom: {request.custom_instructions}")
        
        return APIResponse.success(
            data={
                "template_id": request.template_id,
                "output_path": copy_result,
                "customizations": customizations,
                "message": "Template copied. Use /chat for AI customizations.",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=APIResponse)
async def chat_with_portfolio_ai(request: ChatRequest):
    """
    Chat with the AI for natural language portfolio customization.
    
    Send requests like:
    - "Make it dark blue with orange accents"
    - "Add a particle animation background"
    - "Enable dark mode toggle"
    """
    try:
        from agents.teams.portfolio_team import portfolio_team
        
        prompt = request.message
        if request.template_id:
            prompt = f"Template: {request.template_id}\n\n{request.message}"
        
        response = await portfolio_team.arun(prompt)
        
        return APIResponse.success(
            data={
                "response": str(response),
                "template_id": request.template_id,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/features", response_model=APIResponse)
async def list_available_features():
    """
    List all available features that can be toggled.
    """
    features = [
        {"id": "dark_mode", "name": "Dark Mode Toggle", "default": True},
        {"id": "animations", "name": "Animations", "default": True},
        {"id": "contact_form", "name": "Contact Form", "default": True},
        {"id": "blog_section", "name": "Blog Section", "default": False},
    ]
    return APIResponse.success(data={"features": features})

