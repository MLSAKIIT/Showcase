import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.adapters.database import get_db
from app.services.github_auth_service import (
    exchange_code_for_token,
    get_github_user,
    create_or_update_user,
)
from app.models.user import UserRead


logger = logging.getLogger(__name__)

router = APIRouter()


class GitHubCallbackRequest(BaseModel):
    code: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


def create_access_token(user_id: int) -> str:
    """Create a JWT access token for the user."""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@router.post("/github/callback", response_model=AuthResponse)
async def github_callback(
    request: GitHubCallbackRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Handle GitHub OAuth callback.
    
    Receives the authorization code from the frontend, exchanges it for an
    access token, fetches the user's GitHub profile, and returns a JWT.
    """
    try:
        # Exchange code for GitHub access token
        github_access_token = await exchange_code_for_token(request.code)
        
        # Fetch user profile from GitHub
        github_user = await get_github_user(github_access_token)
        
        # Create or update user in database
        user = await create_or_update_user(session, github_user, github_access_token)
        
        # Create JWT for our application
        access_token = create_access_token(user.id)
        
        logger.info(f"User {user.username} authenticated via GitHub")
        
        return AuthResponse(
            access_token=access_token,
            user=UserRead(
                id=user.id,
                github_id=user.github_id,
                username=user.username,
                email=user.email,
                name=user.name,
                avatar_url=user.avatar_url,
                created_at=user.created_at,
            ),
        )
        
    except Exception as e:
        logger.error(f"GitHub authentication failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"GitHub authentication failed: {str(e)}"
        )


@router.get("/me", response_model=UserRead)
async def get_current_user(
    session: AsyncSession = Depends(get_db)
):
    """Get the currently authenticated user's profile."""
    # TODO: Implement JWT verification and return current user
    raise HTTPException(status_code=501, detail="Not implemented yet")
