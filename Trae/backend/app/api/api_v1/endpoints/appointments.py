from datetime import date, datetime, timedelta
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_clinician, get_current_active_user
from app.db.init_db import get_db
from app.db.models.user import User
from app.schemas.appointment import (
    Appointment as AppointmentSchema,
    AppointmentCreate,
    AppointmentUpdate,
)
from app.services.appointment import (
    check_appointment_conflict,
    create_appointment,
    delete_appointment,
    get_appointment,
    get_appointments,
    get_appointments_by_date_range,
    get_patient_appointments,
    update_appointment,
)
from app.services.fhir import fhir_service
from app.services.patient import get_patient

router = APIRouter()


@router.get("/", response_model=List[AppointmentSchema])
async def read_appointments(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Retrieve appointments with optional date range filtering."""
    if start_date and end_date:
        appointments = await get_appointments_by_date_range(
            db, start_date, end_date, skip=skip, limit=limit
        )
    else:
        appointments = await get_appointments(db, skip=skip, limit=limit)
    return appointments


@router.post("/", response_model=AppointmentSchema)
async def create_new_appointment(
    appointment_in: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_clinician),
) -> Any:
    """Create new appointment."""
    # Check if patient exists
    patient = await get_patient(db, appointment_in.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    # Check for appointment conflicts
    conflict = await check_appointment_conflict(
        db, 
        None,  # No appointment ID for new appointments
        appointment_in.start_time, 
        appointment_in.end_time,
        appointment_in.provider_id
    )
    
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The appointment conflicts with an existing appointment",
        )
    
    appointment = await create_appointment(db, appointment_in, current_user)
    
    # Generate FHIR resource and update the appointment with FHIR ID
    fhir_appointment = fhir_service.appointment_to_fhir(appointment)
    appointment.fhir_id = fhir_appointment.id
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    
    return appointment


@router.get("/{appointment_id}", response_model=AppointmentSchema)
async def read_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get appointment by ID."""
    appointment = await get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentSchema)
async def update_appointment_by_id(
    appointment_id: int,
    appointment_in: AppointmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_clinician),
) -> Any:
    """Update an appointment."""
    appointment = await get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    
    # Check for appointment conflicts if times are being updated
    if appointment_in.start_time and appointment_in.end_time:
        conflict = await check_appointment_conflict(
            db, 
            appointment_id,
            appointment_in.start_time, 
            appointment_in.end_time,
            appointment_in.provider_id or appointment.provider_id
        )
        
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The updated appointment conflicts with an existing appointment",
            )
    
    appointment = await update_appointment(db, appointment, appointment_in)
    return appointment


@router.delete("/{appointment_id}", response_model=AppointmentSchema)
async def delete_appointment_by_id(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_clinician),
) -> Any:
    """Delete an appointment (mark as deleted)."""
    appointment = await get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    
    appointment = await delete_appointment(db, appointment_id)
    return appointment


@router.get("/patient/{patient_id}", response_model=List[AppointmentSchema])
async def read_patient_appointments(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    include_past: bool = False,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get appointments for a specific patient."""
    # Check if patient exists
    patient = await get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    # If include_past is False, only return future appointments
    start_date = None if include_past else datetime.now().date()
    
    appointments = await get_patient_appointments(
        db, patient_id, start_date=start_date, skip=skip, limit=limit
    )
    return appointments


@router.get("/today/", response_model=List[AppointmentSchema])
async def read_today_appointments(
    db: AsyncSession = Depends(get_db),
    provider_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get appointments for today."""
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    appointments = await get_appointments_by_date_range(
        db, today, tomorrow, provider_id=provider_id
    )
    return appointments


@router.get("/week/", response_model=List[AppointmentSchema])
async def read_week_appointments(
    db: AsyncSession = Depends(get_db),
    provider_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get appointments for the current week."""
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=7)  # Next Monday
    
    appointments = await get_appointments_by_date_range(
        db, start_of_week, end_of_week, provider_id=provider_id
    )
    return appointments