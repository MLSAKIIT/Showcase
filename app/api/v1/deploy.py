"""
Deploy API endpoints for GitHub-based deployment.

This module handles:
1. GitHub OAuth callback for deployment (with repo scope)
2. Creating GitHub repositories and pushing code
3. Triggering Vercel deployments
"""

import logging
import os
from typing import Optional, Any, Dict
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.adapters.database import get_db
from app.services.github_auth_service import exchange_code_for_token, get_github_user
from agents.deployment_agent import deploy_to_github_and_vercel

logger = logging.getLogger(__name__)

router = APIRouter()


class DeployCallbackRequest(BaseModel):
    code: str
    portfolio_data: Optional[Dict[str, Any]] = None
    job_id: Optional[str] = None


class DeployResponse(BaseModel):
    success: bool
    github_token: Optional[str] = None
    github_repo_url: Optional[str] = None
    deployment_url: Optional[str] = None
    message: str


@router.post("/github/callback", response_model=DeployResponse)
async def deploy_github_callback(
    request: DeployCallbackRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Handle GitHub OAuth callback for deployment.
    
    This endpoint is called after the user authorizes the app with repo scope.
    It exchanges the code for a token and triggers the deployment process.
    """
    try:
        # Exchange code for GitHub access token
        github_access_token = await exchange_code_for_token(request.code)
        
        # Fetch user profile from GitHub to get username
        github_user = await get_github_user(github_access_token)
        github_username = github_user.get("login", "user")
        
        # If no portfolio data provided, just return the token for future use
        if not request.portfolio_data:
            logger.info(f"GitHub connected for user {github_username}, no portfolio to deploy")
            return DeployResponse(
                success=True,
                github_token=github_access_token,
                message="GitHub connected successfully. You can now deploy portfolios."
            )
        
        # Trigger deployment
        logger.info(f"Starting deployment for user {github_username}")
        
        # Generate repo name from portfolio data
        portfolio_name = request.portfolio_data.get("hero", {}).get("name", "portfolio")
        repo_name = f"{portfolio_name.lower().replace(' ', '-')}-portfolio"
        
        # Call the deployment agent
        result = await deploy_to_github_and_vercel(
            portfolio_data=request.portfolio_data,
            github_token=github_access_token,
            github_username=github_username,
            repo_name=repo_name,
            template_id=request.portfolio_data.get("template_id", "one_temp")
        )
        
        return DeployResponse(
            success=result.get("success", False),
            github_token=github_access_token,
            github_repo_url=result.get("github_url"),
            deployment_url=result.get("deployment_url"),
            message=result.get("message", "Deployment completed")
        )
        
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Deployment failed: {str(e)}"
        )


@router.post("/trigger")
async def trigger_deployment(
    portfolio_data: Dict[str, Any],
    session: AsyncSession = Depends(get_db)
):
    """
    Trigger deployment using a stored GitHub token.
    
    This endpoint is for users who have already connected their GitHub account.
    """
    # TODO: Get stored GitHub token from user session/database
    raise HTTPException(
        status_code=501,
        detail="Direct deployment not yet implemented. Please use the Publish button to connect GitHub first."
    )
