"""
Agno agent example that orchestrates the resume processing pipeline.
"""
import os
import sys
import time
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# TODO: Import Agno agents when available
# from agno import Agent, Task, Pipeline

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


class PipelineAgent:
    """
    Example agent that orchestrates upload -> pipeline -> validation -> vercel deploy.
    TODO: Replace with actual Agno agent implementation.
    """
    
    def __init__(self):
        self.api_base = API_BASE_URL
    
    def upload_resume(self, file_path: str) -> Dict[str, Any]:
        """Upload resume file and return job_id."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
            response = requests.post(
                f"{self.api_base}/api/v1/resumes/upload",
                files=files
            )
            response.raise_for_status()
            return response.json()
    
    def wait_for_completion(self, job_id: int, timeout: int = 300, poll_interval: int = 5) -> Dict[str, Any]:
        """Wait for job to complete."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = requests.get(f"{self.api_base}/api/v1/jobs/{job_id}")
            response.raise_for_status()
            job_data = response.json()
            
            if job_data['status'] == 'completed':
                return job_data
            elif job_data['status'] == 'failed':
                raise RuntimeError(f"Job failed: {job_data.get('error_message', 'Unknown error')}")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")
    
    def deploy_to_vercel(self, job_id: int) -> Dict[str, Any]:
        """Trigger Vercel deployment."""
        response = requests.post(f"{self.api_base}/api/v1/jobs/{job_id}/deploy")
        response.raise_for_status()
        return response.json()
    
    def run_pipeline(self, resume_path: str, auto_deploy: bool = False) -> Dict[str, Any]:
        """
        Orchestrate the full pipeline:
        1. Upload resume
        2. Wait for processing
        3. Validate results
        4. Deploy to Vercel (optional)
        """
        print(f"🚀 Starting pipeline for resume: {resume_path}")
        
        # Step 1: Upload
        print("📤 Uploading resume...")
        upload_result = self.upload_resume(resume_path)
        job_id = upload_result['job_id']
        print(f"✅ Uploaded. Job ID: {job_id}")
        
        # Step 2: Wait for processing
        print("⏳ Waiting for processing...")
        job_result = self.wait_for_completion(job_id)
        print(f"✅ Processing complete!")
        print(f"   Preview URL: {self.api_base}{job_result.get('artifacts', {}).get('preview', 'N/A')}")
        
        # Step 3: Validate
        if job_result['status'] != 'completed':
            raise RuntimeError(f"Job did not complete successfully: {job_result}")
        
        if not job_result.get('artifacts'):
            raise RuntimeError("No artifacts generated")
        
        print("✅ Validation passed")
        
        # Step 4: Deploy (optional)
        if auto_deploy:
            print("🚀 Deploying to Vercel...")
            deploy_result = self.deploy_to_vercel(job_id)
            print(f"✅ Deployment started: {deploy_result.get('deployment_url', 'N/A')}")
            return {**job_result, "deployment": deploy_result}
        
        return job_result


def main():
    """Main entry point for agent script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Resume processing pipeline agent")
    parser.add_argument("resume_path", help="Path to resume file (PDF/Image/DOCX)")
    parser.add_argument("--deploy", action="store_true", help="Auto-deploy to Vercel after processing")
    parser.add_argument("--api-url", default=API_BASE_URL, help="API base URL")
    
    args = parser.parse_args()
    
    agent = PipelineAgent()
    agent.api_base = args.api_url
    
    try:
        result = agent.run_pipeline(args.resume_path, auto_deploy=args.deploy)
        print("\n✅ Pipeline completed successfully!")
        print(f"Job ID: {result['job_id']}")
        return 0
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

