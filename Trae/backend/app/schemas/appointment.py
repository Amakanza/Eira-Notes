from datetime import datetime, timedelta
from typing import Optional

from pydantic import Field, validator

from app.db.base_class import BaseSchema


# Shared properties
class AppointmentBase(BaseSchema):
    """Base appointment schema with shared properties."""
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    appointment_type: Optional[str] = None
    location: Optional[str] = None


# Properties to receive via API on creation
class AppointmentCreate(AppointmentBase):
    """Appointment creation schema."""
    title: str
    start_time: datetime
    end_time: datetime
    appointment_type: str = Field(
        ..., pattern="^(initial|follow_up|consultation|procedure|other)$"
    )
    patient_id: int
    
    @validator("end_time")
    def end_time_must_be_after_start_time(cls, v, values):
        """Validate that end_time is after start_time."""
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


# Properties to receive via API on update
class AppointmentUpdate(AppointmentBase):
    """Appointment update schema."""
    status: Optional[str] = Field(
        None, pattern="^(scheduled|confirmed|cancelled|completed)$"
    )
    
    @validator("end_time")
    def end_time_must_be_after_start_time(cls, v, values):
        """Validate that end_time is after start_time."""
        if v and "start_time" in values and values["start_time"] and v <= values["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


# Properties to return via API
class Appointment(AppointmentBase):
    """Appointment response schema."""
    id: int
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: str
    appointment_type: str
    location: Optional[str] = None
    patient_id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    fhir_id: Optional[str] = None
    
    # Computed property
    duration: timedelta