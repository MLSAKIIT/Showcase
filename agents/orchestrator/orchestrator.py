import logging
import asyncio
from typing import Dict, Any, Optional

# Import the agents we fixed
from agents.middleware.data_preprocessor import DataPreprocessor
from agents.core.schema_builder import SchemaBuilder
from agents.generation.content_generator import ContentGenerator
from agents.validation.validator import PortfolioValidator

logger = logging.getLogger("agents.orchestrator")

class PortfolioOrchestrator:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        # Initialize specialized agents
        self.preprocessor = DataPreprocessor()
        self.schema_builder = SchemaBuilder()
        self.content_generator = ContentGenerator() # This is the Gemini Brain
        self.validator = PortfolioValidator()

    async def process_resume(
        self, 
        parsed_data: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        
        try:
            # 1. Preprocess
            preprocessed = await self.preprocessor.preprocess(parsed_data)
            
            # 2. Build Structural Schema
            schema = await self.schema_builder.build_schema(preprocessed)
            
            # 3. CALL THE BRAIN (Gemini)
            # We MUST pass the data into the content_generator we just upgraded
            logger.info("Orchestrator: Calling Gemini Content Generator...")
            generated_result = await self.content_generator.generate(
                schema=schema,
                user_data=preprocessed,
                preferences=user_preferences
            )
            
            # 4. Validate
            validated = await self.validator.validate_and_enhance(
                generated_result,
                original_data=preprocessed
            )
            
            return validated
            
        except Exception as e:
            logger.error(f"Orchestrator Pipeline failed: {str(e)}")
            return {"content": f"Pipeline Error: {str(e)}", "status": "error"}