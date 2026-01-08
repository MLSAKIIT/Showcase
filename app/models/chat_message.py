from datetime import datetime, timezone

from sqlalchemy import (String,
                        Text,
                        DateTime,
                        Index,
                        )

from sqlalchemy.orm import Mapped, mapped_column

from app.adapters.database import Base


class ChatMessage(Base):

    """
    Stores individual chat messages exchanged during a chatbot session.

    This table is intentionally designed WITHOUT foreign keys to auth tables,
    allowing flexible user identity handling until authentication is finalized.
    """

    __tablename__ = "chat_messages"


    # Primary Key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # string-based for now
    user_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=False,
        doc="Identifier of the user (e.g., dev_user_01, oauth subject, etc.)",
    )

    # Session identifier to group messages of one conversation
    session_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=False,
        doc="Chat session identifier to group related messages",
    )

    # Message role
    role: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Message role: user | assistant | system",
    )

    # Message content
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Raw text content of the message",
    )

    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),  # ✅ Modern approach
        doc="UTC timestamp when the message was created",
    )


# Indexes for efficient querying
Index("ix_chat_messages_user_id", ChatMessage.user_id)
Index("ix_chat_messages_session_id", ChatMessage.session_id)
Index("ix_chat_messages_session_timestamp", ChatMessage.session_id, ChatMessage.timestamp)
