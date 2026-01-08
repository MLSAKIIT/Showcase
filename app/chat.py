import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import google.generativeai as genai
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Simple configuration without the version parameter
genai.configure(api_key=settings.GEMINI_API_KEY)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔌 WebSocket Connected - Using Gemini Next-Gen")
    
    try:
        # Switching to the new model string as requested.
        # Your team likely wants 'gemini-2.0-flash' or 'gemini-3-flash'
        model = genai.GenerativeModel('gemini-2.0-flash') 
        
        chat_session = model.start_chat(history=[])

        while True:
            user_input = await websocket.receive_text()
            
            # Streaming remains the most professional way to handle this
            response = chat_session.send_message(user_input, stream=True)
            
            for chunk in response:
                if chunk.text:
                    await websocket.send_text(chunk.text)
            
            await websocket.send_text("__END_OF_STREAM__")

    except WebSocketDisconnect:
        logger.info("🔌 Connection closed")
    except Exception as e:
        logger.error(f"❌ Gemini Error: {str(e)}")
        await websocket.send_text(f"Error: {str(e)}")