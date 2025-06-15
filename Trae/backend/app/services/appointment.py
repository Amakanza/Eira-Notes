from datetime import datetime
from typing import List, Optional, Union

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.appointment import Appointment
from app.db.models.user import User
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.services import entity_tracker


async def get_appointment(db: AsyncSession, appointment_id: int) -> Optional[Appointment]:
    """Get an appointment by ID."""
    result = await db.execute(
        select(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.is_deleted == False,
        )
    )
    return result.scalars().first()


async def get_appointments(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[Appointment]:
    """Get a list of appointments."""
    result = await db.execute(
        select(Appointment)
        .filter(Appointment.is_deleted == False)
        .order_by(Appointment.start_time)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_patient_appointments(
    db: AsyncSession, patient_id: int, skip: int = 0, limit: int = 100
) -> List[Appointment]:
    """Get appointments for a specific patient."""
    result = await db.execute(
        select(Appointment)
        .filter(
            Appointment.patient_id == patient_id,
            Appointment.is_deleted == False,
        )
        .order_by(Appointment.start_time)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_appointments_by_date_range(
    db: AsyncSession, start_date: datetime, end_date: datetime
) -> List[Appointment]:
    """Get appointments within a date range."""
    result = await db.execute(
        select(Appointment)
        .filter(
            Appointment.is_deleted == False,
            or_(
                and_(
                    Appointment.start_time >= start_date,
                    Appointment.start_time <= end_date,
                ),
                and_(
                    Appointment.end_time >= start_date,
                    Appointment.end_time <= end_date,
                ),
                and_(
                    Appointment.start_time <= start_date,
                    Appointment.end_time >= end_date,
                ),
            ),
        )
        .order_by(Appointment.start_time)
    )
    return result.scalars().all()


async def create_appointment(
    db: AsyncSession, appointment_in: AppointmentCreate, current_user: User
) -> Appointment:
    """Create a new appointment."""
    db_appointment = Appointment(
        **appointment_in.model_dump(exclude_unset=True),
        created_by_id=current_user.id,
        status="scheduled",
    )
    db.add(db_appointment)
    
    # Track the creation in the sync outbox
    await entity_tracker.track_entity_creation(db, db_appointment)
    
    await db.commit()
    await db.refresh(db_appointment)
    return db_appointment


async def update_appointment(
    db: AsyncSession, db_appointment: Appointment, appointment_in: Union[AppointmentUpdate, dict]
) -> Appointment:
    """Update an appointment."""
    appointment_data = (
        appointment_in.model_dump(exclude_unset=True)
        if isinstance(appointment_in, AppointmentUpdate)
        else appointment_in
    )
    
    for field, value in appointment_data.items():
        if hasattr(db_appointment, field):
            setattr(db_appointment, field, value)
    
    db.add(db_appointment)
    
    # Track the update in the sync outbox
    await entity_tracker.track_entity_update(db, db_appointment, appointment_data)
    
    await db.commit()
    await db.refresh(db_appointment)
    return db_appointment


async def delete_appointment(db: AsyncSession, appointment_id: int) -> Optional[Appointment]:
    """Delete an appointment (mark as deleted)."""
    appointment = await get_appointment(db, appointment_id)
    if appointment:
        appointment.is_deleted = True
        db.add(appointment)
        
        # Track the deletion in the sync outbox
        await entity_tracker.track_entity_deletion(db, appointment)
        
        await db.commit()
        await db.refresh(appointment)
    return appointment


async def check_appointment_conflicts(
    db: AsyncSession, start_time: datetime, end_time: datetime, exclude_id: Optional[int] = None
) -> List[Appointment]:
    """Check for appointment conflicts in the given time range."""
    query = select(Appointment).filter(
        Appointment.is_deleted == False,
        or_(
            and_(
                Appointment.start_time <= start_time,
                Appointment.end_time > start_time,
            ),
            and_(
                Appointment.start_time < end_time,
                Appointment.end_time >= end_time,
            ),
            and_(
                Appointment.start_time >= start_time,
                Appointment.end_time <= end_time,
            ),
        ),
    )
    
    if exclude_id:
        query = query.filter(Appointment.id != exclude_id)
    
    result = await db.execute(query)
    return result.scalars().all()