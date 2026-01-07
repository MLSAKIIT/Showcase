import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.chat import router as chat_router 
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
    title="Showcase AI",
    lifespan=lifespan
)

# Open CORS gates completely to kill the "OPTIONS" errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# We are forcing the routes to be clean. 
# If your routes.py has a prefix, this will help us find it.
app.include_router(chat_router, prefix="/api/v1/chat")
@app.get("/health")
async def health():
    return {"status": "online"}