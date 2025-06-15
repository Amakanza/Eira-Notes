from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user
from app.db.init_db import get_db
from app.db.models.user import User
from app.services.appointment import get_appointment
from app.services.clinical_note import get_clinical_note
from app.services.fhir import fhir_service
from app.services.patient import get_patient, get_patient_by_fhir_id

router = APIRouter()


@router.get("/Patient/{fhir_id}")
async def get_fhir_patient(
    fhir_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get a patient as a FHIR Patient resource."""
    patient = await get_patient_by_fhir_id(db, fhir_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    fhir_patient = fhir_service.patient_to_fhir(patient)
    return fhir_patient.dict()


@router.get("/Patient")
async def search_fhir_patients(
    name: Optional[str] = None,
    identifier: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Search for patients as FHIR Patient resources."""
    # This is a simplified implementation of FHIR search
    # In a real-world scenario, you would implement more search parameters
    # and proper FHIR search semantics
    
    patients = await fhir_service.search_patients(db, name=name, identifier=identifier)
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(patients),
        "entry": [
            {
                "resource": fhir_service.patient_to_fhir(patient).dict(),
                "fullUrl": f"Patient/{patient.fhir_id}"
            }
            for patient in patients
        ]
    }


@router.get("/DocumentReference/{fhir_id}")
async def get_fhir_document_reference(
    fhir_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get a clinical note as a FHIR DocumentReference resource."""
    note = await fhir_service.get_clinical_note_by_fhir_id(db, fhir_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical note not found",
        )
    
    fhir_doc = fhir_service.clinical_note_to_fhir(note)
    return fhir_doc.dict()


@router.get("/DocumentReference")
async def search_fhir_document_references(
    patient: Optional[str] = None,
    date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Search for clinical notes as FHIR DocumentReference resources."""
    # This is a simplified implementation of FHIR search
    # In a real-world scenario, you would implement more search parameters
    # and proper FHIR search semantics
    
    notes = await fhir_service.search_clinical_notes(db, patient=patient, date=date)
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(notes),
        "entry": [
            {
                "resource": fhir_service.clinical_note_to_fhir(note).dict(),
                "fullUrl": f"DocumentReference/{note.fhir_id}"
            }
            for note in notes
        ]
    }


@router.get("/Appointment/{fhir_id}")
async def get_fhir_appointment(
    fhir_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get an appointment as a FHIR Appointment resource."""
    appointment = await fhir_service.get_appointment_by_fhir_id(db, fhir_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    
    fhir_appointment = fhir_service.appointment_to_fhir(appointment)
    return fhir_appointment.dict()


@router.get("/Appointment")
async def search_fhir_appointments(
    patient: Optional[str] = None,
    date: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Search for appointments as FHIR Appointment resources."""
    # This is a simplified implementation of FHIR search
    # In a real-world scenario, you would implement more search parameters
    # and proper FHIR search semantics
    
    appointments = await fhir_service.search_appointments(db, patient=patient, date=date, status=status)
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(appointments),
        "entry": [
            {
                "resource": fhir_service.appointment_to_fhir(appointment).dict(),
                "fullUrl": f"Appointment/{appointment.fhir_id}"
            }
            for appointment in appointments
        ]
    }


@router.post("/Patient")
async def create_fhir_patient(
    fhir_patient: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create a patient from a FHIR Patient resource."""
    try:
        patient_data = fhir_service.fhir_patient_to_patient_dict(fhir_patient)
        patient = await fhir_service.create_patient_from_fhir(db, patient_data, current_user)
        return fhir_service.patient_to_fhir(patient).dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create patient: {str(e)}",
        )