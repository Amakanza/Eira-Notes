from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Appointment(Base):
    """Appointment model for scheduling patient appointments."""
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey("patient.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="scheduled"  # scheduled, confirmed, cancelled, completed
    )
    appointment_type: Mapped[str] = mapped_column(String(50), nullable=False)  # initial, follow-up, etc.
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments")
    created_by: Mapped["User"] = relationship("User", back_populates="appointments")
    
    # FHIR Resource ID
    fhir_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    fhir_resource_type: Mapped[str] = mapped_column(String(50), default="Appointment")
    
    @property
    def duration(self) -> timedelta:
        """Calculate the duration of the appointment."""
        return self.end_time - self.start_time