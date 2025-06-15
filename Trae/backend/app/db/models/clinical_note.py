from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class ClinicalNote(Base):
    """Clinical note model for storing clinical documentation."""
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    note_type: Mapped[str] = mapped_column(String(50), nullable=False)  # progress, assessment, treatment, etc.
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey("patient.id"), nullable=False)
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="clinical_notes")
    created_by: Mapped["User"] = relationship("User", back_populates="clinical_notes")
    attachments: Mapped[List["Attachment"]] = relationship(
        "Attachment", back_populates="clinical_note", cascade="all, delete-orphan"
    )
    
    # FHIR Resource ID
    fhir_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    fhir_resource_type: Mapped[str] = mapped_column(String(50), default="DocumentReference")


class Attachment(Base):
    """Attachment model for storing files related to clinical notes."""
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # image, document, signature, etc.
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)  # S3 key
    clinical_note_id: Mapped[int] = mapped_column(Integer, ForeignKey("clinicalnote.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    clinical_note: Mapped["ClinicalNote"] = relationship("ClinicalNote", back_populates="attachments")