from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user
from app.db.init_db import get_db
from app.db.models.user import User
from app.schemas.patient import Patient as PatientSchema, PatientCreate, PatientUpdate
from app.services.fhir import fhir_service
from app.services.patient import (
    create_patient,
    delete_patient,
    get_patient,
    get_patient_by_mrn,
    get_patients,
    update_patient,
)

router = APIRouter()


@router.get("/", response_model=List[PatientSchema])
async def read_patients(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Retrieve patients."""
    patients = await get_patients(db, skip=skip, limit=limit, search=search)
    return patients


@router.post("/", response_model=PatientSchema)
async def create_new_patient(
    patient_in: PatientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create new patient."""
    # Check if patient with same MRN already exists
    existing_patient = await get_patient_by_mrn(db, patient_in.medical_record_number)
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A patient with this medical record number already exists",
        )
    
    patient = await create_patient(db, patient_in, current_user)
    
    # Generate FHIR resource and update the patient with FHIR ID
    fhir_patient = fhir_service.patient_to_fhir(patient)
    patient.fhir_id = fhir_patient.id
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    
    return patient


@router.get("/{patient_id}", response_model=PatientSchema)
async def read_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get patient by ID."""
    patient = await get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    return patient


@router.put("/{patient_id}", response_model=PatientSchema)
async def update_patient_by_id(
    patient_id: int,
    patient_in: PatientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update a patient."""
    patient = await get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    # Check if updating MRN and if it already exists
    if patient_in.medical_record_number and patient_in.medical_record_number != patient.medical_record_number:
        existing_patient = await get_patient_by_mrn(db, patient_in.medical_record_number)
        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A patient with this medical record number already exists",
            )
    
    patient = await update_patient(db, patient, patient_in)
    return patient


@router.delete("/{patient_id}", response_model=PatientSchema)
async def delete_patient_by_id(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Delete a patient (mark as inactive)."""
    patient = await get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    patient = await delete_patient(db, patient_id)
    return patient


@router.get("/mrn/{medical_record_number}", response_model=PatientSchema)
async def read_patient_by_mrn(
    medical_record_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get patient by medical record number."""
    patient = await get_patient_by_mrn(db, medical_record_number)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    return patient