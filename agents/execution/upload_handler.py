import os
<<<<<<< HEAD
import uuid
import json
from datetime import datetime
from typing import Dict, Any

BASE_STORAGE_PATH = "storage/jobs"


class UploadHandler:
    """
    Handles file upload persistence and job creation.
    """

    def __init__(self, base_path: str = BASE_STORAGE_PATH):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        resume_data = state.get("raw_input")
        if not resume_data:
            raise ValueError("No resume data provided")

        job_id = str(uuid.uuid4())
        job_dir = os.path.join(self.base_path, job_id)
        os.makedirs(job_dir, exist_ok=True)

        # Save raw input
        with open(os.path.join(job_dir, "resume.json"), "w") as f:
            json.dump(resume_data, f, indent=2)

        state["job"] = {
            "job_id": job_id,
            "created_at": datetime.utcnow().isoformat(),
            "job_dir": job_dir
        }

        return state
=======
from typing import Dict, Any


class DeployHandler:
    """
    Handles deployment of built site.
    """

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        build = state["build"]
        job = state["job"]

        # MOCK DEPLOY (production-safe abstraction)
        deployment_url = self._mock_deploy(build["output_dir"], job["job_id"])

        state["deployment"] = {
            "status": "success",
            "url": deployment_url
        }

        return state

    def _mock_deploy(self, build_dir: str, job_id: str) -> str:
        """
        Replace with:
        - Vercel API
        - Netlify API
        - S3 + CloudFront
        """
        return f"https://deploy.example.com/{job_id}"
>>>>>>> 1e6abe464a5baebe118a48d62818195d91f563e5
