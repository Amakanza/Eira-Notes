from typing import List, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models.clinical_note import Attachment, ClinicalNote
from app.db.models.user import User
from app.schemas.clinical_note import AttachmentCreate, ClinicalNoteCreate, ClinicalNoteUpdate
from app.services import entity_tracker


async def get_clinical_note(db: AsyncSession, note_id: int) -> Optional[ClinicalNote]:
    """Get a clinical note by ID."""
    result = await db.execute(
        select(ClinicalNote)
        .filter(ClinicalNote.id == note_id, ClinicalNote.is_deleted == False)
        .options(joinedload(ClinicalNote.attachments))
    )
    return result.scalars().first()


async def get_clinical_notes(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[ClinicalNote]:
    """Get a list of clinical notes."""
    result = await db.execute(
        select(ClinicalNote)
        .filter(ClinicalNote.is_deleted == False)
        .options(joinedload(ClinicalNote.attachments))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_patient_clinical_notes(
    db: AsyncSession, patient_id: int, skip: int = 0, limit: int = 100
) -> List[ClinicalNote]:
    """Get clinical notes for a specific patient."""
    result = await db.execute(
        select(ClinicalNote)
        .filter(
            ClinicalNote.patient_id == patient_id,
            ClinicalNote.is_deleted == False,
        )
        .options(joinedload(ClinicalNote.attachments))
        .order_by(ClinicalNote.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def create_clinical_note(
    db: AsyncSession, note_in: ClinicalNoteCreate, current_user: User
) -> ClinicalNote:
    """Create a new clinical note."""
    db_note = ClinicalNote(
        **note_in.model_dump(exclude_unset=True),
        created_by_id=current_user.id,
    )
    db.add(db_note)
    
    # Track the creation in the sync outbox
    await entity_tracker.track_entity_creation(db, db_note)
    
    await db.commit()
    await db.refresh(db_note)
    return db_note


async def update_clinical_note(
    db: AsyncSession, db_note: ClinicalNote, note_in: Union[ClinicalNoteUpdate, dict]
) -> ClinicalNote:
    """Update a clinical note."""
    note_data = (
        note_in.model_dump(exclude_unset=True) if isinstance(note_in, ClinicalNoteUpdate) else note_in
    )
    
    for field, value in note_data.items():
        if hasattr(db_note, field):
            setattr(db_note, field, value)
    
    db.add(db_note)
    
    # Track the update in the sync outbox
    await entity_tracker.track_entity_update(db, db_note, note_data)
    
    await db.commit()
    await db.refresh(db_note)
    return db_note


async def delete_clinical_note(db: AsyncSession, note_id: int) -> Optional[ClinicalNote]:
    """Delete a clinical note (mark as deleted)."""
    note = await get_clinical_note(db, note_id)
    if note:
        note.is_deleted = True
        db.add(note)
        
        # Track the deletion in the sync outbox
        await entity_tracker.track_entity_deletion(db, note)
        
        await db.commit()
        await db.refresh(note)
    return note


async def add_attachment(
    db: AsyncSession, note_id: int, attachment_in: AttachmentCreate
) -> Optional[Attachment]:
    """Add an attachment to a clinical note."""
    note = await get_clinical_note(db, note_id)
    if not note:
        return None
    
    db_attachment = Attachment(
        **attachment_in.model_dump(exclude_unset=True),
        clinical_note_id=note_id,
    )
    db.add(db_attachment)
    
    # Track the creation in the sync outbox
    await entity_tracker.track_entity_creation(db, db_attachment)
    
    await db.commit()
    await db.refresh(db_attachment)
    return db_attachment


async def get_attachment(db: AsyncSession, attachment_id: int) -> Optional[Attachment]:
    """Get an attachment by ID."""
    result = await db.execute(select(Attachment).filter(Attachment.id == attachment_id))
    return result.scalars().first()


async def delete_attachment(db: AsyncSession, attachment_id: int) -> Optional[Attachment]:
    """Delete an attachment."""
    attachment = await get_attachment(db, attachment_id)
    if attachment:
        # Track the deletion in the sync outbox before actually deleting
        await entity_tracker.track_entity_deletion(db, attachment)
        
        await db.delete(attachment)
        await db.commit()
    return attachment