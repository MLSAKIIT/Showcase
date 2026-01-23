"""
FastAPI application entry point.

This module:
- Configures the FastAPI application
- Sets up CORS middleware
- Registers exception handlers
- Manages application lifespan (DB, adapters)
- Registers API routers
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import chat
from app.api.routes import api_router
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.adapters.database import engine
from app.middleware.exception_handler import add_exception_handlers

# Import models to ensure they're registered with SQLModel
from app.models.portfolio import Portfolio  # noqa: F401
from app.models.chat_message import ChatMessage  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.job import Job  # noqa: F401

# Initialize logging
setup_logging(
    level="DEBUG" if settings.DEBUG else "INFO",
    log_to_console=True,
    log_to_file=not settings.is_testing()
)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Manages startup and shutdown events:
    - Creates database tables on startup (development only)
    - Disposes database engine on shutdown
    
    In production, use Alembic migrations instead of auto-creating tables.
    """
    logger.info("Showcase AI: Application starting up")
    logger.info(f"Environment: {settings.ENV} | Debug: {settings.DEBUG}")
    
    # Create tables (only for development)
    # In production, use: alembic upgrade head
    if settings.DEBUG:
        from sqlmodel import SQLModel
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created (development mode)")
    
    yield
    
    logger.info("Showcase AI: Application shutting down")
    engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Showcase AI: Transforming resumes into stunning portfolios.",
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Register exception handlers
add_exception_handlers(app)

# CORS middleware configuration
cors_origins = settings.BACKEND_CORS_ORIGINS if settings.BACKEND_CORS_ORIGINS else ["*"]
if settings.is_production() and "*" in cors_origins:
    logger.warning("CORS is configured to allow all origins in production. Consider restricting this.")

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
    """
    Health check endpoint.
    
    Returns basic status information about the application.
    Used by load balancers and monitoring systems.
    """
    return {
        "status": "online",
        "engine": "Gemini-Vision-v1",
        "version": "1.0.0",
        "environment": settings.ENV,
    }


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs": f"{settings.API_V1_STR}/docs" if settings.DEBUG else None,
        "health": "/health",
    }
