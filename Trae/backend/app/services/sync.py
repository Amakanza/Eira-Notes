from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.sync_outbox import SyncOperationType, SyncOutbox, SyncStatus
from app.db.models.user import User
from app.db.models.patient import Patient
from app.db.models.appointment import Appointment
from app.db.models.clinical_note import ClinicalNote, Attachment

from app.services import patient as patient_service
from app.services import appointment as appointment_service
from app.services import clinical_note as clinical_note_service

from app.schemas.sync import SyncEntityChange
from app.schemas.patient import PatientCreate, PatientUpdate
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.schemas.clinical_note import ClinicalNoteCreate, ClinicalNoteUpdate, AttachmentCreate

import json
from datetime import datetime, timezone


async def process_entity_change(db: AsyncSession, change: SyncEntityChange, current_user: User) -> Dict[str, Any]:
    """Process a single entity change (create, update, or delete)."""
    result = {
        "entity_type": change.entity_type,
        "entity_id": change.entity_id,
        "operation": change.operation,
        "status": "success",
        "error_message": None
    }
    
    try:
        if change.operation == SyncOperationType.CREATE or change.operation == SyncOperationType.UPDATE:
            # Handle create or update (upsert)
            entity = await upsert_entity(db, change, current_user)
            if entity:
                result["entity_id"] = str(entity.id)  # Update with actual ID if it was created
        elif change.operation == SyncOperationType.DELETE:
            # Handle delete
            success = await delete_entity(db, change)
            if not success:
                result["status"] = "error"
                result["error_message"] = f"Entity {change.entity_type} with ID {change.entity_id} not found"
        else:
            result["status"] = "error"
            result["error_message"] = f"Unknown operation: {change.operation}"
    except Exception as e:
        result["status"] = "error"
        result["error_message"] = str(e)
    
    return result


async def upsert_entity(db: AsyncSession, change: SyncEntityChange, current_user: User) -> Optional[Any]:
    """Upsert (create or update) an entity based on the change data."""
    entity_type = change.entity_type
    entity_id = change.entity_id
    payload = change.payload
    
    if entity_type == "patient":
        return await upsert_patient(db, entity_id, payload, current_user)
    elif entity_type == "appointment":
        return await upsert_appointment(db, entity_id, payload, current_user)
    elif entity_type == "clinical_note":
        return await upsert_clinical_note(db, entity_id, payload, current_user)
    elif entity_type == "attachment":
        return await upsert_attachment(db, entity_id, payload, current_user)
    else:
        raise ValueError(f"Unsupported entity type: {entity_type}")


async def delete_entity(db: AsyncSession, change: SyncEntityChange) -> bool:
    """Delete an entity based on the change data."""
    entity_type = change.entity_type
    entity_id = change.entity_id
    
    try:
        entity_id_int = int(entity_id)
    except ValueError:
        return False  # ID must be an integer
    
    if entity_type == "patient":
        patient = await patient_service.delete_patient(db, entity_id_int)
        return patient is not None
    elif entity_type == "appointment":
        appointment = await appointment_service.delete_appointment(db, entity_id_int)
        return appointment is not None
    elif entity_type == "clinical_note":
        note = await clinical_note_service.delete_clinical_note(db, entity_id_int)
        return note is not None
    elif entity_type == "attachment":
        attachment = await clinical_note_service.delete_attachment(db, entity_id_int)
        return attachment is not None
    else:
        return False


async def upsert_patient(db: AsyncSession, entity_id: str, payload: Dict[str, Any], current_user: User) -> Patient:
    """Upsert a patient."""
    try:
        patient_id = int(entity_id) if entity_id != "new" else None
    except ValueError:
        patient_id = None
    
    # Check if patient exists
    existing_patient = None
    if patient_id:
        existing_patient = await patient_service.get_patient(db, patient_id)
    
    # If patient doesn't exist but has a medical_record_number, try to find by MRN
    if not existing_patient and "medical_record_number" in payload:
        existing_patient = await patient_service.get_patient_by_mrn(db, payload["medical_record_number"])
    
    # Create or update patient
    if existing_patient:
        # Update existing patient
        return await patient_service.update_patient(db, existing_patient, payload)
    else:
        # Create new patient
        patient_create = PatientCreate(**payload)
        return await patient_service.create_patient(db, patient_create, current_user)


async def upsert_appointment(db: AsyncSession, entity_id: str, payload: Dict[str, Any], current_user: User) -> Appointment:
    """Upsert an appointment."""
    try:
        appointment_id = int(entity_id) if entity_id != "new" else None
    except ValueError:
        appointment_id = None
    
    # Check if appointment exists
    existing_appointment = None
    if appointment_id:
        existing_appointment = await appointment_service.get_appointment(db, appointment_id)
    
    # Create or update appointment
    if existing_appointment:
        # Update existing appointment
        return await appointment_service.update_appointment(db, existing_appointment, payload)
    else:
        # Create new appointment
        appointment_create = AppointmentCreate(**payload)
        return await appointment_service.create_appointment(db, appointment_create, current_user)


async def upsert_clinical_note(db: AsyncSession, entity_id: str, payload: Dict[str, Any], current_user: User) -> ClinicalNote:
    """Upsert a clinical note."""
    try:
        note_id = int(entity_id) if entity_id != "new" else None
    except ValueError:
        note_id = None
    
    # Check if clinical note exists
    existing_note = None
    if note_id:
        existing_note = await clinical_note_service.get_clinical_note(db, note_id)
    
    # Create or update clinical note
    if existing_note:
        # Update existing clinical note
        return await clinical_note_service.update_clinical_note(db, existing_note, payload)
    else:
        # Create new clinical note
        note_create = ClinicalNoteCreate(**payload)
        return await clinical_note_service.create_clinical_note(db, note_create, current_user)


async def upsert_attachment(db: AsyncSession, entity_id: str, payload: Dict[str, Any], current_user: User) -> Attachment:
    """Upsert an attachment."""
    try:
        attachment_id = int(entity_id) if entity_id != "new" else None
    except ValueError:
        attachment_id = None
    
    # Check if attachment exists
    existing_attachment = None
    if attachment_id:
        existing_attachment = await clinical_note_service.get_attachment(db, attachment_id)
    
    # Create or update attachment
    if existing_attachment:
        # Update existing attachment - not supported, attachments are immutable
        raise ValueError("Updating attachments is not supported")
    else:
        # Create new attachment
        if "clinical_note_id" not in payload:
            raise ValueError("clinical_note_id is required for creating an attachment")
            
        attachment_create = AttachmentCreate(**payload)
        return await clinical_note_service.add_attachment(db, payload["clinical_note_id"], attachment_create)


async def track_entity_change(db: AsyncSession, entity_type: str, entity_id: str, operation: str, payload: Dict[str, Any]) -> SyncOutbox:
    """Track an entity change in the sync outbox."""
    # Create a new sync outbox entry
    sync_outbox = SyncOutbox(
        entity_type=entity_type,
        entity_id=entity_id,
        operation=operation,
        payload=json.dumps(payload),
        status=SyncStatus.PENDING
    )
    
    db.add(sync_outbox)
    await db.commit()
    await db.refresh(sync_outbox)
    return sync_outbox


async def get_changes_since(db: AsyncSession, since_timestamp: datetime) -> List[SyncEntityChange]:
    """Get all changes since the given timestamp."""
    result = await db.execute(
        select(SyncOutbox)
        .filter(SyncOutbox.updated_at >= since_timestamp)
        .order_by(SyncOutbox.updated_at)
    )
    outbox_entries = result.scalars().all()
    
    changes = []
    for entry in outbox_entries:
        try:
            payload = json.loads(entry.payload) if entry.payload else {}
            changes.append(SyncEntityChange(
                entity_type=entry.entity_type,
                entity_id=entry.entity_id,
                operation=entry.operation,
                payload=payload,
                status=entry.status,
                error_message=entry.error_message,
                updated_at=entry.updated_at.isoformat() if entry.updated_at else None
            ))
        except Exception as e:
            # Skip invalid entries
            continue
    
    return changes


async def mark_changes_as_synced(db: AsyncSession, change_ids: List[int]) -> None:
    """Mark changes as synced."""
    if not change_ids:
        return
        
    await db.execute(
        update(SyncOutbox)
        .where(SyncOutbox.id.in_(change_ids))
        .values(status=SyncStatus.SYNCED, updated_at=datetime.now(timezone.utc))
    )
    await db.commit()