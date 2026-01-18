from fastapi import APIRouter
from app.api.v1 import resume, portfolio, auth, jobs
from app.core.config import settings

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(resume.router, prefix="/resume", tags=["Resume Processing"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio Management"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Job Status"])

# Debug endpoints (only in development)
if settings.ENV == "development" or settings.DEBUG:
    from app.api.v1 import debug
    api_router.include_router(debug.router, tags=["Debug"])
