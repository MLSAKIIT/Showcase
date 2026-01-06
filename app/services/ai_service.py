import logging
from pydantic import ValidationError
from agents.integration import generate_portfolio
from app.schemas.portfolio import PortfolioOutput

logger = logging.getLogger(__name__)

class AIService:
    async def generate_portfolio_content(self, raw_text: str) -> dict:
        try:
            logger.info("AI Generation pipeline started")
            portfolio_data = await generate_portfolio(raw_text)

            if not isinstance(portfolio_data, dict):
                logger.error(f"AI pipeline returned type {type(portfolio_data)} instead of dict")
                raise RuntimeError("AI pipeline returned invalid portfolio payload")

            try:
                validated_data = PortfolioOutput(**portfolio_data)
                logger.info("AI output successfully validated against PortfolioOutput schema")
                
                return validated_data.model_dump()

            except ValidationError as e:
                logger.error(f"AI Schema validation failed: {str(e)}")
                raise RuntimeError("AI returned data that does not match the required portfolio structure")

        except Exception as e:
            if not isinstance(e, RuntimeError):
                logger.exception("Critical failure in the AI generation pipeline")
            raise

ai_service = AIService()