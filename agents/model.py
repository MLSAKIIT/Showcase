
import os
import time
import logging
from agno.models.google import Gemini

logger = logging.getLogger(__name__)

# Enforce a global delay between requests to respect Free Tier limits
# 5 RPM = 1 request every 12 seconds. We use 15s to be safe.
RATE_LIMIT_DELAY = 15

class RateLimitedGemini(Gemini):
    """
    A wrapper around Gemini that enforces a strict sleep delay before 
    generating content to avoid 429 Resource Exhausted errors.
    """
    def response(self, messages, *args, **kwargs):
        logger.info(f"⏳ Rate Limiter: Sleeping {RATE_LIMIT_DELAY}s before Gemini request...")
        print(f"⏳ Sleeping {RATE_LIMIT_DELAY}s (Rate Limit)...")
        time.sleep(RATE_LIMIT_DELAY)
        return super().response(messages, *args, **kwargs)

def get_model(model_id: str = None) -> Gemini:
    """
    Returns a configured Gemini model instance with:
    1. Correct API Key priority (GEMINI_API_KEY > GOOGLE_API_KEY)
    2. Automatic Rate Limiting wrapper
    3. Correct ID parsing (handling 'google:' prefix)
    
    Args:
        model_id: Optional model ID override. Defaults to GEMINI_AGENT_MODEL env var.
    """
    # 1. Determine Model ID
    if not model_id:
        model_id = os.getenv("GEMINI_AGENT_MODEL", "gemini-2.0-flash")
    
    # Remove google: prefix if present
    if model_id.startswith("google:"):
        model_id = model_id.split(":", 1)[1]

    # 2. Determine API Key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        logger.warning("⚠️ No API Key found in environment variables (GEMINI_API_KEY or GOOGLE_API_KEY)")

    # 3. Return Rate Limited Instance
    return RateLimitedGemini(id=model_id, api_key=api_key)
