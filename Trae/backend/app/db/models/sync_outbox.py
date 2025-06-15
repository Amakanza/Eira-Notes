from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base

class SyncOperationType(str):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

class SyncStatus(str):
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    ERROR = "error"

class SyncOutbox(Base):
    """Model for tracking local changes to be synced with the server."""
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., user, patient, appointment, clinical_note
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)   # Can be int or uuid as string
    operation: Mapped[str] = mapped_column(String(10), nullable=False)    # create, update, delete
    payload: Mapped[str] = mapped_column(Text, nullable=False)            # JSON string of the entity data
    status: Mapped[str] = mapped_column(String(10), default=SyncStatus.PENDING)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)