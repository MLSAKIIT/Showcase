"""
Celery background tasks for pipeline processing.
"""
import os
from celery import Celery
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Job, JobStatus, Artifact, Resume, ChatMessage
from app.ai_pipeline import process_resume_pipeline
from app.ai_providers.gemini_adapter import GeminiAdapter

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("showcase", broker=REDIS_URL, backend=REDIS_URL)


@celery_app.task(name="process_resume_task")
def process_resume_task(job_id: int):
    """
    Main pipeline task: OCR -> Structured JSON -> Gemini passes -> Validation -> Frontend generation.
    """
    db: Session = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {"error": "Job not found"}

        job.status = JobStatus.PROCESSING
        db.commit()

        # Run pipeline
        result = process_resume_pipeline(job_id, db)

        if result.get("success"):
            job.status = JobStatus.COMPLETED
        else:
            job.status = JobStatus.FAILED
            job.error_message = result.get("error", "Unknown error")

        db.commit()
        return {"job_id": job_id, "status": job.status.value, **result}

    except Exception as e:
        db.rollback()
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            db.commit()
        return {"error": str(e)}
    finally:
        db.close()


@celery_app.task(name="deploy_to_vercel_task")
def deploy_to_vercel_task(job_id: int):
    """
    Deploy frontend bundle to Vercel.
    """
    db: Session = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {"error": "Job not found"}

        bundle_artifact = db.query(Artifact).filter(
            Artifact.job_id == job_id,
            Artifact.artifact_type == "frontend_bundle"
        ).first()

        if not bundle_artifact:
            return {"error": "Frontend bundle not found"}

        # TODO: Implement Vercel deployment
        # - Extract bundle.zip
        # - Use Vercel API to deploy
        # - Update artifact with deployment URL

        vercel_token = os.getenv("VERCEL_TOKEN")
        if not vercel_token:
            return {"error": "VERCEL_TOKEN not configured"}

        # Placeholder for Vercel deployment
        deployment_url = f"https://showcase-{job_id}.vercel.app"  # TODO: Actual deployment

        bundle_artifact.file_url = deployment_url
        bundle_artifact.metadata = {"deployed": True, "deployment_url": deployment_url}
        db.commit()

        return {
            "job_id": job_id,
            "deployment_url": deployment_url,
            "status": "deployed"
        }

    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

