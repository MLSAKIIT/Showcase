import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.adapters.database import engine, Base
from app.models.portfolio import Portfolio 

# --- YOUR SOUL INJECTION START ---
from app.chat import router as chat_router 
# --- YOUR SOUL INJECTION END ---

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    """
    logger.info("Showcase AI: Application starting up")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("Showcase AI: Application shutting down")
    await engine.dispose()

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

# Team's original routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# --- YOUR SOUL INJECTION START ---
app.include_router(chat_router, prefix="/api/v1/chat")
# --- YOUR SOUL INJECTION END ---

@app.get("/health", include_in_schema=False)
async def health_check():
    return {
        "status": "online",
        "engine": "Gemini-Vision-v1",
        "version": "1.0.0"
    }