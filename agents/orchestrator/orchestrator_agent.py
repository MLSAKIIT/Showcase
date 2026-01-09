"""
ORCHESTRATOR.PY
================
Minimal coordinator for Showcase agent pipeline.

Pipeline:
1. Data preprocessing
2. Schema building
3. Content generation
4. Validation
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from agents.middleware.data_preprocessor import DataPreprocessor
from agents.core.schema_builder import SchemaBuilderAgent
from agents.generation.generation_agent import GenerationAgent
from agents.validation.validation_agent import PortfolioValidator

logger = logging.getLogger("agents.orchestrator")
logger.setLevel(logging.INFO)


class PipelineError(Exception):
    """Pipeline execution failed."""
    pass


class PortfolioOrchestrator:
    """
    Minimal portfolio generation orchestrator.
    """

    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.schema_builder = SchemaBuilderAgent()
        self.generator = GenerationAgent()
        self.validator = PortfolioValidator()

        logger.info("PortfolioOrchestrator initialized")

    async def run(
        self,
        parsed_data: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run the full portfolio pipeline.
        """

        self._validate_input(parsed_data)

        try:
            # 1. Preprocess
            logger.info("Stage 1: Preprocessing")
            profile = await self.preprocessor.preprocess(parsed_data)

            # 2. Build schema
            logger.info("Stage 2: Schema building")
            schema = await self.schema_builder.build_schema(profile)

            # 3. Generate content
            logger.info("Stage 3: Content generation")
            portfolio = await self.generator.generate(
                schema=schema,
                user_data=profile,
                preferences=user_preferences
            )

            # 4. Validate output
            logger.info("Stage 4: Validation")
            portfolio = await self.validator.validate_and_enhance(
                portfolio,
                original_data=profile
            )

            portfolio["metadata"] = {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "pipeline": "showcase-ai",
                "status": "completed",
            }

            return portfolio

        except Exception as e:
            logger.error("Pipeline failed", exc_info=True)
            raise PipelineError(str(e)) from e

    # Helpers

    def _validate_input(self, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict) or not data:
            raise PipelineError("Input must be a non-empty dictionary")

        if not (data.get("name") or data.get("email")):
            raise PipelineError("Input must contain name or email")

        if not any([
            data.get("skills"),
            data.get("projects"),
            data.get("experience"),
            data.get("education")
        ]):
            raise PipelineError("Input lacks meaningful content")
