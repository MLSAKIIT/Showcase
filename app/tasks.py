import logging
import time
from fastapi import UploadFile
from sqlmodel import Session
from app.adapters.database import engine
from app.models.portfolio import Portfolio
from app.services.ocr_service import ocr_service
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

async def process_resume_task(job_id: str, file: UploadFile, user_id: str):
    start_time = time.time()
    logger.info(f"Starting processing for Job: {job_id} (User: {user_id})")

    with Session(engine) as db:
        try:
            raw_text = await ocr_service.extract_text(file)
            
            if not raw_text or not raw_text.strip():
                raise ValueError(f"OCR returned empty content for Job {job_id}")
            
            portfolio_json = await ai_service.generate_portfolio_content(raw_text)
            
            new_portfolio = Portfolio(
                job_id=job_id,
                user_id=user_id,
                full_name=portfolio_json.get("hero", {}).get("name", "User"),
                content=portfolio_json,
                is_published=False
            )
            
            db.add(new_portfolio)
            db.commit()

            db.refresh(new_portfolio)
            
            duration = time.time() - start_time
            logger.info(f"Job {job_id} successfully completed in {duration:.2f}s")

        except Exception as e:
            db.rollback()
            elapsed = time.time() - start_time
            logger.exception(f"Job {job_id} failed after {elapsed:.2f}s: {str(e)}")
            raise

        finally:
            await file.close()
            logger.debug(f"Resource cleanup for Job {job_id} finalized")