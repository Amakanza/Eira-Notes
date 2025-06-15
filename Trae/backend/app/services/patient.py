from typing import List, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.patient import Patient
from app.db.models.user import User
from app.schemas.patient import PatientCreate, PatientUpdate
from app.services import entity_tracker


async def get_patient(db: AsyncSession, patient_id: int) -> Optional[Patient]:
    """Get a patient by ID."""
    result = await db.execute(select(Patient).filter(Patient.id == patient_id))
    return result.scalars().first()


async def get_patient_by_mrn(db: AsyncSession, medical_record_number: str) -> Optional[Patient]:
    """Get a patient by medical record number."""
    result = await db.execute(
        select(Patient).filter(Patient.medical_record_number == medical_record_number)
    )
    return result.scalars().first()


async def get_patients(
    db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str] = None
) -> List[Patient]:
    """Get a list of patients with optional search."""
    query = select(Patient)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Patient.first_name.ilike(search_term))
            | (Patient.last_name.ilike(search_term))
            | (Patient.medical_record_number.ilike(search_term))
        )
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_patient(db: AsyncSession, patient_in: PatientCreate, current_user: User) -> Patient:
    """Create a new patient."""
    db_patient = Patient(
        **patient_in.model_dump(exclude_unset=True),
        created_by_id=current_user.id,
    )
    db.add(db_patient)
    
    # Track the creation in the sync outbox
    await entity_tracker.track_entity_creation(db, db_patient)
    
    await db.commit()
    await db.refresh(db_patient)
    return db_patient


async def update_patient(
    db: AsyncSession, db_patient: Patient, patient_in: Union[PatientUpdate, dict]
) -> Patient:
    """Update a patient."""
    patient_data = (
        patient_in.model_dump(exclude_unset=True) if isinstance(patient_in, PatientUpdate) else patient_in
    )
    
    for field, value in patient_data.items():
        if hasattr(db_patient, field):
            setattr(db_patient, field, value)
    
    db.add(db_patient)
    
    # Track the update in the sync outbox
    await entity_tracker.track_entity_update(db, db_patient, patient_data)
    
    await db.commit()
    await db.refresh(db_patient)
    return db_patient


async def delete_patient(db: AsyncSession, patient_id: int) -> Optional[Patient]:
    """Delete a patient (mark as inactive)."""
    patient = await get_patient(db, patient_id)
    if patient:
        patient.is_active = False
        db.add(patient)
        
        # Track the deletion in the sync outbox
        await entity_tracker.track_entity_deletion(db, patient)
        
        await db.commit()
        await db.refresh(patient)
    return patient


async def get_patients_by_user(db: AsyncSession, user_id: int) -> List[Patient]:
    """Get all patients created by a specific user."""
    result = await db.execute(select(Patient).filter(Patient.created_by_id == user_id))
    return result.scalars().all()