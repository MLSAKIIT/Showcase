"""
Gemini AI adapter with abstracted interface.
Returns deterministic content for testing.
"""
import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class GeminiAdapter:
    """
    Adapter for Google Gemini API.
    Returns deterministic mock responses for testing.
    TODO: Replace with actual Gemini API calls in production.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("WARNING: GEMINI_API_KEY not set. Using mock responses.")
    
    def _call_gemini(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Call Gemini API (or return mock response).
        TODO: Implement actual Gemini API call using google-generativeai.
        """
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            # TODO: Implement actual API call using new google.genai package
            # import google.genai as genai
            # from google.genai import types
            # client = genai.Client(api_key=self.api_key)
            # contents = [types.Part.from_text(prompt)]
            # response = await client.aio.models.generate_content(
            #     model="gemini-1.5-pro",
            #     contents=contents
            # )
            # return response.candidates[0].content.parts[0].text
            pass
        
        # Mock deterministic response for testing
        return self._get_mock_response(prompt)
    
    def _get_mock_response(self, prompt: str) -> str:
        """Return deterministic mock response based on prompt type."""
        prompt_lower = prompt.lower()
        
        if "structured" in prompt_lower or "json" in prompt_lower:
            return json.dumps({
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-234-567-8900",
                "summary": "Experienced software engineer with expertise in Python and FastAPI.",
                "experience": [
                    {
                        "title": "Senior Software Engineer",
                        "company": "Tech Corp",
                        "period": "2020 - Present",
                        "description": "Led development of microservices architecture."
                    }
                ],
                "education": [
                    {
                        "degree": "BS Computer Science",
                        "school": "University of Technology",
                        "year": "2018"
                    }
                ],
                "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"]
            }, indent=2)
        
        elif "frontend" in prompt_lower or "ui" in prompt_lower:
            return json.dumps({
                "theme": {
                    "primaryColor": "#3b82f6",
                    "secondaryColor": "#1e40af",
                    "fontFamily": "Inter, sans-serif"
                },
                "sections": [
                    {
                        "type": "header",
                        "content": {
                            "name": "John Doe",
                            "title": "Senior Software Engineer",
                            "contact": {
                                "email": "john.doe@example.com",
                                "phone": "+1-234-567-8900"
                            }
                        }
                    },
                    {
                        "type": "summary",
                        "content": "Experienced software engineer with expertise in Python and FastAPI."
                    },
                    {
                        "type": "experience",
                        "content": {
                            "title": "Experience",
                            "items": [
                                {
                                    "title": "Senior Software Engineer",
                                    "company": "Tech Corp",
                                    "period": "2020 - Present",
                                    "description": "Led development of microservices architecture."
                                }
                            ]
                        }
                    },
                    {
                        "type": "education",
                        "content": {
                            "title": "Education",
                            "items": [
                                {
                                    "degree": "BS Computer Science",
                                    "school": "University of Technology",
                                    "year": "2018"
                                }
                            ]
                        }
                    },
                    {
                        "type": "skills",
                        "content": {
                            "title": "Skills",
                            "items": ["Python", "FastAPI", "PostgreSQL", "Docker"]
                        }
                    }
                ]
            }, indent=2)
        
        elif "enhance" in prompt_lower or "improve" in prompt_lower:
            return json.dumps({
                "enhanced": True,
                "suggestions": [
                    "Added quantifiable achievements",
                    "Improved action verbs",
                    "Enhanced technical keywords"
            ]
            }, indent=2)
        
        else:
            return json.dumps({"response": "Mock AI response", "prompt": prompt[:100]})
    
    def generate_structured_resume(self, ocr_text: str) -> Dict[str, Any]:
        """
        Generate structured JSON from OCR text.
        """
        prompt = f"""
        Extract structured resume data from the following text and return valid JSON:
        
        {ocr_text[:2000]}
        
        Return JSON with fields: name, email, phone, summary, experience (array), education (array), skills (array).
        """
        
        response = self._call_gemini(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "name": "Extracted from OCR",
                "email": "",
                "phone": "",
                "summary": ocr_text[:500],
                "experience": [],
                "education": [],
                "skills": []
            }
    
    def enhance_content(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance resume content with AI suggestions.
        """
        prompt = f"""
        Review and enhance the following resume data. Return enhanced JSON:
        
        {json.dumps(structured_data, indent=2)}
        
        Improve descriptions, add quantifiable achievements, and enhance professional language.
        """
        
        response = self._call_gemini(prompt)
        try:
            enhanced = json.loads(response)
            return enhanced if isinstance(enhanced, dict) else structured_data
        except json.JSONDecodeError:
            return structured_data
    
    def generate_frontend_json(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate UI JSON specification for frontend generation.
        """
        prompt = f"""
        Generate a frontend UI JSON specification for displaying this resume:
        
        {json.dumps(resume_data, indent=2)}
        
        Return JSON with theme (colors, fonts) and sections (header, summary, experience, education, skills).
        """
        
        response = self._call_gemini(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback UI JSON
            return {
                "theme": {"primaryColor": "#3b82f6", "fontFamily": "Inter"},
                "sections": [{"type": "header", "content": resume_data}]
            }
    
    def validate_and_fix_ui(self, ui_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate UI JSON and auto-fix any issues.
        """
        prompt = f"""
        Validate and fix the following UI JSON specification. Return corrected JSON:
        
        {json.dumps(ui_json, indent=2)}
        
        Ensure all required fields are present and valid.
        """
        
        response = self._call_gemini(prompt)
        try:
            validated = json.loads(response)
            return validated if isinstance(validated, dict) else ui_json
        except json.JSONDecodeError:
            return ui_json