import logging
import os
import json
from typing import Dict, Any, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Priority 1: Check Environment Variables (Best Practice)
        # Priority 2: Use the Hardcoded Key you provided (Emergency Fallback)
        self.api_key = os.getenv("GEMINI_API_KEY") or "AIzaSyDEDoZaKvBXB1IPdvJu6dgifCV_4PpFmiE"
        self.secret_key = os.getenv("SECRET_KEY") or "Showcase_AI_Secure_Key"
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Using 1.5-flash for speed and reliability
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini Engine successfully fueled and ready.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {str(e)}")
        else:
            logger.error("CRITICAL: No API Key found. System is offline.")

    async def generate(self, schema: Dict[str, Any], user_data: Dict[str, Any], preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.api_key:
            return {"content": "Error: Brain power missing (API Key).", "status": "error"}

        logger.info("Sending data to Gemini for professional transformation...")
        
        # This prompt is designed to make the Chatbot act like a high-end consultant
        prompt = f"""
        You are 'Showcase AI', a premium portfolio architect. 
        Your goal is to transform messy resume data into a polished, recruiter-ready portfolio.
        
        CONTEXT:
        - Secret Token: {self.secret_key} (Internal Use)
        - User Data: {user_data}
        - Schema Structure: {schema}
        
        TASK:
        1. Write a high-impact 'Hero Section' with a bold headline.
        2. Create a 'Professional Narrative' that summarizes their unique value.
        3. List their 'Signature Projects' with results-oriented bullet points.
        
        RESPONSE FORMAT:
        Use clean Markdown with headers (##), bold text (**), and lists (-). 
        Make it look beautiful in a pink and purple themed UI.
        """

        try:
            # Call the actual AI
            response = self.model.generate_content(prompt)
            
            if response.text:
                return {
                    "content": response.text,
                    "status": "success",
                    "metadata": {"model": "gemini-1.5-flash", "structured": True}
                }
            else:
                return {"content": "The AI returned an empty response.", "status": "empty"}

        except Exception as e:
            logger.error(f"Generation Error: {str(e)}")
            return {
                "content": "I encountered a glitch in my neural net. Please try again in a moment!",
                "error": str(e),
                "status": "failed"
            }