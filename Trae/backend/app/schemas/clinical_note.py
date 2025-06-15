from datetime import datetime
from typing import List, Optional

from pydantic import Field

from app.db.base_class import BaseSchema


# Attachment schemas
class AttachmentBase(BaseSchema):
    """Base attachment schema with shared properties."""
    filename: Optional[str] = None
    file_type: Optional[str] = None


class AttachmentCreate(AttachmentBase):
    """Attachment creation schema."""
    filename: str
    file_type: str = Field(..., pattern="^(image|document|signature|other)$")
    file_path: str


class Attachment(AttachmentBase):
    """Attachment response schema."""
    id: int
    filename: str
    file_type: str
    file_path: str
    clinical_note_id: int
    created_at: datetime


# Clinical Note schemas
class ClinicalNoteBase(BaseSchema):
    """Base clinical note schema with shared properties."""
    title: Optional[str] = None
    content: Optional[str] = None
    note_type: Optional[str] = None


class ClinicalNoteCreate(ClinicalNoteBase):
    """Clinical note creation schema."""
    title: str
    content: str
    note_type: str = Field(
        ..., pattern="^(progress|assessment|treatment|initial|discharge|other)$"
    )
    patient_id: int


class ClinicalNoteUpdate(ClinicalNoteBase):
    """Clinical note update schema."""
    pass


class ClinicalNote(ClinicalNoteBase):
    """Clinical note response schema."""
    id: int
    title: str
    content: str
    note_type: str
    patient_id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    fhir_id: Optional[str] = None
    attachments: List[Attachment] = []