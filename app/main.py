
"""
FastAPI application entry point.
This module:
- Configures the FastAPI application
- Sets up CORS middleware
- Manages application lifespan (DB, adapters)
- Registers API routers
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import chat
from app.api.routes import api_router
from app.core.config import settings
from app.adapters.database import engine
from app.models.portfolio import Portfolio
from app.models.chat_message import ChatMessage
from app.models.user import User
from app.models.job import Job

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Creates database tables on startup (development only).
    In production, use Alembic migrations instead.
    """
    logger.info("Showcase AI: Application starting up")
    
    # Create tables (only for development)
    # In production, use: alembic upgrade head
    if settings.DEBUG:
        from sqlmodel import SQLModel
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created (development mode)")
    
    yield
    
    logger.info("Showcase AI: Application shutting down")
    engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Showcase AI: Transforming resumes into stunning portfolios.",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS middleware configuration
# In production, replace ["*"] with specific allowed origins
cors_origins = settings.BACKEND_CORS_ORIGINS if settings.BACKEND_CORS_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "online",
        "engine": "Gemini-Vision-v1",
        "version": "1.0.0",
    }
