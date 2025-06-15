from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.db.base_class import BaseSchema


# Shared properties
class UserBase(BaseSchema):
    """Base user schema with shared properties."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    """User creation schema."""
    email: EmailStr
    password: str
    full_name: str
    role: str = Field(..., pattern="^(admin|clinician|reception)$")


# Properties to receive via API on update
class UserUpdate(UserBase):
    """User update schema."""
    password: Optional[str] = None


# Properties to return via API
class User(UserBase):
    """User response schema."""
    id: int
    email: EmailStr
    full_name: str
    role: str
    created_at: datetime
    updated_at: datetime


# Properties for user login
class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str


# Properties for password change
class PasswordChange(BaseModel):
    """Password change schema."""
    current_password: str
    new_password: str