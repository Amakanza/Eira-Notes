from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user
from app.db.init_db import get_db
from app.db.models.user import User
from app.services.clinical_note import get_clinical_note
from app.services.patient import get_patient
from app.services.reporting import reporting_service
from app.services.storage import storage_service

router = APIRouter()


@router.get("/clinical-note/{note_id}")
async def generate_clinical_note_report(
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
        
        return {"url": url, "filename": f"clinical_note_{note_id}.{format_type}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )


@router.get("/patient-summary/{patient_id}")
async def generate_patient_summary_report(
    patient_id: int,
    format_type: str = Query("pdf", pattern="^(pdf|docx)$"),
    include_notes: bool = True,
    include_appointments: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Generate a summary report for a patient."""
    patient = await get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    try:
        file_path = await reporting_service.generate_patient_summary_report(
            patient, 
            format_type,
            include_notes=include_notes,
            include_appointments=include_appointments
        )
        url = storage_service.generate_presigned_url(file_path)
        if not url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate download URL",
            )
        
        return {"url": url, "filename": f"patient_summary_{patient_id}.{format_type}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )


@router.get("/templates")
async def list_report_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """List available report templates."""
    try:
        templates = reporting_service.list_templates()
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}",
        )


@router.get("/custom/{template_name}")
async def generate_custom_report(
    template_name: str,
    patient_id: int,
    format_type: str = Query("pdf", pattern="^(pdf|docx)$"),
    note_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Generate a custom report using a specific template."""
    # Check if patient exists
    patient = await get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    # Check if note exists if note_id is provided
    note = None
    if note_id:
        note = await get_clinical_note(db, note_id)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Clinical note not found",
            )
    
    try:
        file_path = await reporting_service.generate_custom_report(
            template_name,
            patient,
            format_type,
            note=note
        )
        url = storage_service.generate_presigned_url(file_path)
        if not url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate download URL",
            )
        
        return {"url": url, "filename": f"{template_name}_{patient_id}.{format_type}"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )