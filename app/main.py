"""
FastAPI main application entry point.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from app.database import engine, Base
from app.api.routes import router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Resume Processing Pipeline API",
    description="API for processing resumes through OCR, AI, and frontend generation",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Serve static preview files
preview_dir = os.path.join(os.path.dirname(__file__), "..", "previews")
os.makedirs(preview_dir, exist_ok=True)

if os.path.exists(preview_dir):
    app.mount("/preview", StaticFiles(directory=preview_dir, html=True), name="preview")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Resume Processing Pipeline API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

