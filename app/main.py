import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.adapters.database import engine
from app import models

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Showcase AI: Application starting up")
    
    models.Portfolio.metadata.create_all(bind=engine)
    
    yield  
    
    logger.info("Showcase AI: Application shutting down")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Showcase AI: Transforming resumes into stunning portfolios.",
    debug=settings.DEBUG,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", include_in_schema=False)
async def health_check():
    return {
        "status": "online",
        "engine": "Gemini-Vision-v1",
        "version": "1.0.0"
    }