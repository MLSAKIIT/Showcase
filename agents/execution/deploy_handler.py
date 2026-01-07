import os
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