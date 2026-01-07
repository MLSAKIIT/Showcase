import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import google.generativeai as genai
from google.generativeai.types import RequestOptions
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Global configuration
genai.configure(api_key=settings.GEMINI_API_KEY)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔌 WebSocket Connected")
    
    try:
        # We explicitly force 'v1' here to stop the 404/v1beta errors
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            request_options=RequestOptions(api_version='v1')
        )
        
        chat_session = model.start_chat(history=[])

        while True:
            # Wait for user message from React
            user_input = await websocket.receive_text()
            
            # Use the SDK to stream the response
            response = chat_session.send_message(user_input, stream=True)
            
            for chunk in response:
                if chunk.text:
                    await websocket.send_text(chunk.text)
            
            # Send the special end token our frontend looks for
            await websocket.send_text("__END_OF_STREAM__")

    except WebSocketDisconnect:
        logger.info("🔌 Connection closed by user")
    except Exception as e:
        logger.error(f"❌ Gemini Error: {str(e)}")
        # Send error to the UI bubble so you can see it
        await websocket.send_text(f"Error: {str(e)}")