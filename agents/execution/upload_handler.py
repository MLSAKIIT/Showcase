"""
UPLOAD & DEPLOY HANDLERS
========================

Upload Handler: Persist files and create jobs
Deploy Handler: Deploy built portfolio to hosting
"""

import os
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger("handlers")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)


# Upload Handler
class UploadHandler:
    """Handles file upload persistence and job creation."""
    
    def __init__(self, base_path: str = "storage/jobs"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
        logger.info("UploadHandler initialized")
    
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process uploaded resume and create job.
        
        Args:
            state: Pipeline state with raw_input
            
        Returns:
            Updated state with job metadata
        """
        try:
            resume_data = state.get("raw_input")
            if not resume_data:
                raise ValueError("No resume data provided")
            
            # Create job
            job_id = str(uuid.uuid4())
            job_dir = os.path.join(self.base_path, job_id)
            os.makedirs(job_dir, exist_ok=True)
            
            # Save raw input
            resume_path = os.path.join(job_dir, "resume.json")
            with open(resume_path, "w", encoding="utf-8") as f:
                json.dump(resume_data, f, indent=2)
            
            state["job"] = {
                "job_id": job_id,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "job_dir": job_dir,
                "resume_path": resume_path
            }
            
            logger.info(f"✓ Job created: {job_id}")
            return state
            
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            raise


# Deploy Handler
class DeployHandler:
    """Handles deployment of built portfolio."""
    
    def __init__(self, provider: str = "mock"):
        """
        Initialize deploy handler.
        
        Args:
            provider: Deployment provider ('mock', 'vercel', 'netlify', 's3')
        """
        self.provider = provider
        logger.info(f"DeployHandler initialized: {provider}")
    
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy built portfolio.
        
        Args:
            state: Pipeline state with build artifacts
            
        Returns:
            Updated state with deployment info
        """
        try:
            build = state.get("build", {})
            job = state.get("job", {})
            
            if not build or not build.get("output_dir"):
                raise ValueError("No build artifacts found")
            
            # Deploy based on provider
            if self.provider == "mock":
                url = self._deploy_mock(job["job_id"])
            elif self.provider == "vercel":
                url = await self._deploy_vercel(build["output_dir"], job["job_id"])
            elif self.provider == "netlify":
                url = await self._deploy_netlify(build["output_dir"], job["job_id"])
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            state["deployment"] = {
                "status": "success",
                "url": url,
                "provider": self.provider,
                "deployed_at": datetime.utcnow().isoformat() + "Z"
            }
            
            logger.info(f"✓ Deployed to {self.provider}: {url}")
            return state
            
        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            state["deployment"] = {
                "status": "failed",
                "error": str(e),
                "provider": self.provider
            }
            return state
    
    def _deploy_mock(self, job_id: str) -> str:
        """Mock deployment (for testing)."""
        return f"https://showcase-{job_id[:8]}.local"
    
    async def _deploy_vercel(self, build_dir: str, job_id: str) -> str:
        """
        Deploy to Vercel.
        
        TODO: Implement with Vercel API
        - Get VERCEL_TOKEN from env
        - Create project
        - Upload files
        - Get deployment URL
        """
        logger.warning("Vercel deployment not implemented")
        return f"https://showcase-{job_id[:8]}.vercel.app"
    
    async def _deploy_netlify(self, build_dir: str, job_id: str) -> str:
        """
        Deploy to Netlify.
        
        TODO: Implement with Netlify API
        - Get NETLIFY_TOKEN from env
        - Create site
        - Upload files
        - Get deployment URL
        """
        logger.warning("Netlify deployment not implemented")
        return f"https://showcase-{job_id[:8]}.netlify.app"