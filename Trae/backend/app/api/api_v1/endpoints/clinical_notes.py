from typing import Any, List

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_clinician, get_current_active_user
from app.db.init_db import get_db
from app.db.models.user import User
from app.schemas.clinical_note import (
    Attachment as AttachmentSchema,
    AttachmentCreate,
    ClinicalNote as ClinicalNoteSchema,
    ClinicalNoteCreate,
    ClinicalNoteUpdate,
)
from app.services.clinical_note import (
    add_attachment,
    create_clinical_note,
    delete_attachment,
    delete_clinical_note,
    get_attachment,
    get_clinical_note,
    get_clinical_notes,
    get_patient_clinical_notes,
    update_clinical_note,
)
from app.services.fhir import fhir_service
from app.services.patient import get_patient
from app.services.reporting import reporting_service
from app.services.storage import storage_service

router = APIRouter()


@router.get("/", response_model=List[ClinicalNoteSchema])
async def read_clinical_notes(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Retrieve clinical notes."""
    notes = await get_clinical_notes(db, skip=skip, limit=limit)
    return notes


@router.post("/", response_model=ClinicalNoteSchema)
async def create_new_clinical_note(
    note_in: ClinicalNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_clinician),
) -> Any:
    """Create new clinical note."""
    # Check if patient exists
    patient = await get_patient(db, note_in.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    note = await create_clinical_note(db, note_in, current_user)
    
    # Generate FHIR resource and update the note with FHIR ID
    fhir_doc = fhir_service.clinical_note_to_fhir(note)
    note.fhir_id = fhir_doc.id
    db.add(note)
    await db.commit()
    await db.refresh(note)
    
    return note


@router.get("/{note_id}", response_model=ClinicalNoteSchema)
async def read_clinical_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get clinical note by ID."""
    note = await get_clinical_note(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical note not found",
        )
    return note


@router.put("/{note_id}", response_model=ClinicalNoteSchema)
async def update_clinical_note_by_id(
    note_id: int,
    note_in: ClinicalNoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_clinician),
) -> Any:
    """Update a clinical note."""
    note = await get_clinical_note(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical note not found",
        )
    
    note = await update_clinical_note(db, note, note_in)
    return note


@router.delete("/{note_id}", response_model=ClinicalNoteSchema)
async def delete_clinical_note_by_id(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_clinician),
) -> Any:
    """Delete a clinical note (mark as deleted)."""
    note = await get_clinical_note(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical note not found",
        )
    
    note = await delete_clinical_note(db, note_id)
    return note


@router.get("/patient/{patient_id}", response_model=List[ClinicalNoteSchema])
async def read_patient_clinical_notes(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get clinical notes for a specific patient."""
    # Check if patient exists
    patient = await get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    notes = await get_patient_clinical_notes(db, patient_id, skip=skip, limit=limit)
    return notes


@router.post("/{note_id}/attachments", response_model=AttachmentSchema)
async def upload_attachment(
    note_id: int,
    file: UploadFile = File(...),
    file_type: str = Query(..., pattern="^(image|document|signature|other)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_clinician),
) -> Any:
    """Upload an attachment to a clinical note."""
    # Check if note exists
    note = await get_clinical_note(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical note not found",
        )
    
    # Upload file to S3
    file_path, filename = await storage_service.upload_file(
        file, folder=f"attachments/{note_id}"
    )
    
    # Create attachment record
    attachment_in = AttachmentCreate(
        filename=filename,
        file_type=file_type,
        file_path=file_path,
    )
    
    attachment = await add_attachment(db, note_id, attachment_in)
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create attachment record",
        )
    
    return attachment


@router.get("/{note_id}/attachments/{attachment_id}", response_model=AttachmentSchema)
async def read_attachment(
    note_id: int,
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get attachment by ID."""
    attachment = await get_attachment(db, attachment_id)
    if not attachment or attachment.clinical_note_id != note_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )
    return attachment


@router.delete("/{note_id}/attachments/{attachment_id}", response_model=AttachmentSchema)
async def delete_attachment_by_id(
    note_id: int,
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_clinician),
) -> Any:
    """Delete an attachment."""
    attachment = await get_attachment(db, attachment_id)
    if not attachment or attachment.clinical_note_id != note_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )
    
    # Delete file from S3
    storage_service.delete_file(attachment.file_path)
    
    # Delete attachment record
    attachment = await delete_attachment(db, attachment_id)
    return attachment


@router.get("/{note_id}/download")
async def download_attachment(
    note_id: int,
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get a presigned URL for downloading an attachment."""
    attachment = await get_attachment(db, attachment_id)
    if not attachment or attachment.clinical_note_id != note_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )
    
    url = storage_service.generate_presigned_url(attachment.file_path)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download URL",
        )
    
    return {"url": url}


@router.get("/{note_id}/report")
async def generate_report(
    note_id: int,
    format_type: str = Query("pdf", pattern="^(pdf|docx)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Generate a report for a clinical note."""
    note = await get_clinical_note(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical note not found",
        )
    
    try:
        file_path = await reporting_service.generate_clinical_note_report(note, format_type)
        url = storage_service.generate_presigned_url(file_path)
        if not url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate download URL",
            )
        
        return {"url": url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )