from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException
from app.schemas.resume import ResumeUploadResponse
from app.tasks import process_resume_task
from app.api import dependencies
import uuid

router = APIRouter()

@router.post("/upload", response_model=ResumeUploadResponse, status_code=202)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db=Depends(dependencies.get_db)
):
   
    if not file.filename.endswith((".pdf", ".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="Invalid file format.")

    job_id = str(uuid.uuid4())

    background_tasks.add_task(process_resume_task, job_id, file, "guest_user")

    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Resume received.Portfolio design in progress."
    }