"""
Main AI pipeline orchestration.
"""
import os
import json
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models import Job, Artifact, Resume, ChatMessage
from app.ocr.ocr_adapter import OCRAdapter
from app.ai_providers.gemini_adapter import GeminiAdapter
from app.frontend_generator.generator import generate_frontend_bundle


def process_resume_pipeline(job_id: int, db: Session) -> Dict[str, Any]:
    """
    Execute the full pipeline:
    1. OCR extraction
    2. Structured JSON generation
    3. Gemini content pass
    4. Gemini frontend pass
    5. Validation & auto-fix
    6. Frontend generation
    7. Preview generation
    """
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {"success": False, "error": "Job not found"}

        file_path = job.metadata.get("file_path")
        if not file_path or not os.path.exists(file_path):
            return {"success": False, "error": "Resume file not found"}

        # Step 1: OCR extraction
        ocr_adapter = OCRAdapter()
        ocr_text = ocr_adapter.extract_text(file_path)

        # Create/update resume record
        resume = db.query(Resume).filter(Resume.job_id == job_id).first()
        if not resume:
            resume = Resume(
                job_id=job_id,
                original_filename=job.metadata.get("original_filename", ""),
                file_path=file_path,
                ocr_text=ocr_text
            )
            db.add(resume)
        else:
            resume.ocr_text = ocr_text
        db.commit()

        # Step 2: Structured JSON generation (Gemini)
        gemini = GeminiAdapter()
        structured_json = gemini.generate_structured_resume(ocr_text)

        resume.structured_json = structured_json
        db.commit()

        # Save structured JSON artifact
        artifacts_dir = os.path.join(os.path.dirname(__file__), "..", "artifacts")
        os.makedirs(artifacts_dir, exist_ok=True)
        json_path = os.path.join(artifacts_dir, f"{job_id}_resume.json")
        with open(json_path, "w") as f:
            json.dump(structured_json, f, indent=2)

        json_artifact = Artifact(
            job_id=job_id,
            artifact_type="resume_json",
            file_path=json_path,
            file_url=f"/api/v1/artifacts/{job_id}/resume.json"
        )
        db.add(json_artifact)

        # Step 3: Gemini content pass (enhance content)
        enhanced_content = gemini.enhance_content(structured_json)
        
        # Log interaction
        msg = ChatMessage(
            job_id=job_id,
            role="assistant",
            content=f"Enhanced resume content with AI suggestions"
        )
        db.add(msg)

        # Step 4: Gemini frontend pass (generate UI JSON)
        ui_json = gemini.generate_frontend_json(enhanced_content)

        # Step 5: Validation & auto-fix
        validated_ui = gemini.validate_and_fix_ui(ui_json)

        # Step 6: Frontend generation
        bundle_path = generate_frontend_bundle(job_id, validated_ui, db)

        # Step 7: Preview generation (copy index.html to previews)
        previews_dir = os.path.join(os.path.dirname(__file__), "..", "previews")
        os.makedirs(previews_dir, exist_ok=True)
        
        # Extract bundle and copy preview
        import zipfile
        preview_path = os.path.join(previews_dir, f"{job_id}", "index.html")
        os.makedirs(os.path.dirname(preview_path), exist_ok=True)
        
        if os.path.exists(bundle_path):
            with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
                # Extract index.html to preview location
                if 'index.html' in zip_ref.namelist():
                    zip_ref.extract('index.html', os.path.dirname(preview_path))
                    preview_path = os.path.join(os.path.dirname(preview_path), "index.html")

        preview_artifact = Artifact(
            job_id=job_id,
            artifact_type="preview",
            file_path=preview_path,
            file_url=f"/preview/{job_id}/index.html"
        )
        db.add(preview_artifact)

        db.commit()

        return {
            "success": True,
            "job_id": job_id,
            "resume_json": json_path,
            "bundle_path": bundle_path,
            "preview_url": f"/preview/{job_id}/index.html"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

