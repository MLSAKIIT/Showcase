from typing import List, Optional
from datetime import datetime, timezone
import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_message import ChatMessage

logger = logging.getLogger(__name__)

class ChatService:

    """
    Service layer for chat message persistence and retrieval.

    Responsibilities:
    - Save chat messages
    - Fetch conversation history
    - Isolate DB logic from WebSocket / API layers
    """

    @staticmethod
    async def save_message(
        db: AsyncSession,
        *,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
        timestamp: Optional[datetime] = None,
    ) -> ChatMessage:
        """
        Persist a single chat message.

        Args:
            db: Active async database session
            user_id: Identifier of the user
            session_id: Chat session identifier
            role: 'user' | 'assistant' | 'system'
            content: Message text
            timestamp: Optional explicit timestamp

        Returns:
            Persisted ChatMessage instance
        """

        try:
            message = ChatMessage(
                user_id=user_id,
                session_id=session_id,
                role=role,
                content=content,
                timestamp=timestamp or datetime.now(timezone.utc),
            )

            db.add(message)
            await db.commit()
            await db.refresh(message)

            return message
            
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to save chat message: {e}")
            raise RuntimeError(f"Database error while saving message: {e}") from e
    

    #to retrieve chat history
    @staticmethod
    async def get_session_history(
        db: AsyncSession,
        *,
        session_id: str,
        limit: Optional[int] = 100,
    ) -> List[ChatMessage]:
        """
        Retrieve conversation history for a session.

        Args:
            db: Active async database session
            session_id: Chat session identifier
            limit: Maximum number of messages to return (default: 100)

        Returns:
            List of ChatMessage objects ordered chronologically
        """
        try:
            stmt = (
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.timestamp.asc())
                .limit(limit)
            )

            result = await db.execute(stmt)
            return list(result.scalars().all())

        except SQLAlchemyError as e:
            logger.error(f"Failed to retrieve session history: {e}")
            raise RuntimeError(f"Database error while fetching history: {e}") from e