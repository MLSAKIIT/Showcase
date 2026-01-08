import httpx
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.user import User


GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"


async def exchange_code_for_token(code: str) -> str:
    """
    Exchange the authorization code for an access token.
    
    Args:
        code: The authorization code from GitHub OAuth callback
        
    Returns:
        The GitHub access token
        
    Raises:
        Exception: If token exchange fails
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GITHUB_TOKEN_URL,
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        
        if response.status_code != 200:
            raise Exception(f"GitHub token exchange failed: {response.text}")
        
        data = response.json()
        
        if "error" in data:
            raise Exception(f"GitHub OAuth error: {data.get('error_description', data['error'])}")
        
        return data["access_token"]


async def get_github_user(access_token: str) -> dict:
    """
    Fetch the authenticated user's profile from GitHub.
    
    Args:
        access_token: The GitHub access token
        
    Returns:
        Dictionary containing user profile data
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GITHUB_USER_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch GitHub user: {response.text}")
        
        return response.json()


async def create_or_update_user(
    session: AsyncSession,
    github_user: dict,
    access_token: str
) -> User:
    """
    Create a new user or update an existing one based on GitHub ID.
    
    Args:
        session: Async database session
        github_user: User data from GitHub API
        access_token: GitHub access token to store
        
    Returns:
        The created or updated User object
    """
    # Check if user already exists
    statement = select(User).where(User.github_id == github_user["id"])
    result = await session.execute(statement)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        # Update existing user
        existing_user.username = github_user["login"]
        existing_user.email = github_user.get("email")
        existing_user.name = github_user.get("name")
        existing_user.avatar_url = github_user.get("avatar_url")
        existing_user.github_access_token = access_token
        existing_user.updated_at = datetime.utcnow()
        session.add(existing_user)
        await session.commit()
        await session.refresh(existing_user)
        return existing_user
    
    # Create new user
    new_user = User(
        github_id=github_user["id"],
        username=github_user["login"],
        email=github_user.get("email"),
        name=github_user.get("name"),
        avatar_url=github_user.get("avatar_url"),
        github_access_token=access_token,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
