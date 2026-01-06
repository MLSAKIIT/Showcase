import logging
import time
from sqlmodel import Session
from app.adapters.database import engine
from app.models.portfolio import Portfolio
from app.services.ocr_service import ocr_service
from app.services.ai_service import ai_service
from fastapi import UploadFile

logger = logging.getLogger(__name__)

async def process_resume_task(job_id: str, file: UploadFile, user_id: str):
   
    start_time = time.time()
    logger.info(f"Job {job_id} started for User {user_id}")

    with Session(engine) as db:
        try:
            logger.info(f"Starting OCR for Job: {job_id}")
            raw_text = await ocr_service.extract_text(file)
            
            logger.info(f"Calling AI Agents for Job: {job_id}")
            portfolio_json = await ai_service.generate_portfolio_content(raw_text)
            
            if not isinstance(portfolio_json, dict) or "hero" not in portfolio_json:
                raise ValueError(f"AI service returned invalid or incomplete portfolio format for Job {job_id}")

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
            logger.exception(f"Critical Failure in Job {job_id}: {str(e)}")
            raise 

        finally:
            await file.close()
            logger.debug(f"Temporary file for Job {job_id} closed")