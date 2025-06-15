from datetime import date, datetime
from typing import Optional

from pydantic import EmailStr, Field

from app.db.base_class import BaseSchema


# Shared properties
class PatientBase(BaseSchema):
    """Base patient schema with shared properties."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    medical_record_number: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_id: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class PatientCreate(PatientBase):
    """Patient creation schema."""
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str = Field(..., pattern="^(male|female|other|unknown)$")
    medical_record_number: str


# Properties to receive via API on update
class PatientUpdate(PatientBase):
    """Patient update schema."""
    pass


# Properties to return via API
class Patient(PatientBase):
    """Patient response schema."""
    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    medical_record_number: str
    created_at: datetime
    updated_at: datetime
    created_by_id: int
    fhir_id: Optional[str] = None
    
    # Computed properties
    full_name: str
    age: int