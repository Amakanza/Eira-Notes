from datetime import datetime
from typing import Any, Dict, Optional, Union

from fhir.resources.appointment import Appointment as FHIRAppointment
from fhir.resources.documentreference import DocumentReference
from fhir.resources.patient import Patient as FHIRPatient

from app.db.models.appointment import Appointment
from app.db.models.clinical_note import ClinicalNote
from app.db.models.patient import Patient


class FHIRService:
    """Service for handling FHIR resource conversion and interoperability."""
    
    def patient_to_fhir(self, patient: Patient) -> FHIRPatient:
        """Convert a Patient model to a FHIR Patient resource."""
        # Create a FHIR Patient resource
        fhir_patient = FHIRPatient(
            id=patient.fhir_id or f"patient-{patient.id}",
            meta={
                "lastUpdated": patient.updated_at.isoformat(),
            },
            identifier=[{
                "system": "http://eira.clinical/mrn",
                "value": patient.medical_record_number,
            }],
            name=[{
                "family": patient.last_name,
                "given": [patient.first_name],
                "use": "official",
            }],
            gender=patient.gender,
            birthDate=patient.date_of_birth.isoformat(),
            active=patient.is_active,
        )
        
        # Add optional fields if they exist
        if patient.phone:
            fhir_patient.telecom = [{
                "system": "phone",
                "value": patient.phone,
                "use": "home",
            }]
        
        if patient.email:
            if not hasattr(fhir_patient, "telecom"):
                fhir_patient.telecom = []
            fhir_patient.telecom.append({
                "system": "email",
                "value": patient.email,
            })
        
        if patient.address:
            fhir_patient.address = [{
                "text": patient.address,
                "use": "home",
            }]
        
        if patient.emergency_contact_name and patient.emergency_contact_phone:
            fhir_patient.contact = [{
                "name": {
                    "text": patient.emergency_contact_name,
                },
                "telecom": [{
                    "system": "phone",
                    "value": patient.emergency_contact_phone,
                }],
                "relationship": [{
                    "text": "Emergency Contact",
                }],
            }]
        
        return fhir_patient
    
    def clinical_note_to_fhir(self, note: ClinicalNote) -> DocumentReference:
        """Convert a ClinicalNote model to a FHIR DocumentReference resource."""
        # Create a FHIR DocumentReference resource
        fhir_doc = DocumentReference(
            id=note.fhir_id or f"note-{note.id}",
            meta={
                "lastUpdated": note.updated_at.isoformat(),
            },
            status="current" if not note.is_deleted else "entered-in-error",
            type={
                "text": note.note_type,
            },
            subject={
                "reference": f"Patient/{note.patient.fhir_id or f'patient-{note.patient_id}'}",
                "display": note.patient.full_name,
            },
            date=note.created_at.isoformat(),
            author=[{
                "reference": f"Practitioner/practitioner-{note.created_by_id}",
                "display": note.created_by.full_name,
            }],
            title=note.title,
            content=[{
                "attachment": {
                    "contentType": "text/plain",
                    "data": note.content,
                    "title": note.title,
                },
            }],
        )
        
        # Add attachments if they exist
        for attachment in note.attachments:
            fhir_doc.content.append({
                "attachment": {
                    "contentType": "application/octet-stream",
                    "url": f"https://eira.clinical/api/v1/attachments/{attachment.id}",
                    "title": attachment.filename,
                },
            })
        
        return fhir_doc
    
    def appointment_to_fhir(self, appointment: Appointment) -> FHIRAppointment:
        """Convert an Appointment model to a FHIR Appointment resource."""
        # Create a FHIR Appointment resource
        status_map = {
            "scheduled": "booked",
            "confirmed": "booked",
            "cancelled": "cancelled",
            "completed": "fulfilled",
        }
        
        fhir_appointment = FHIRAppointment(
            id=appointment.fhir_id or f"appointment-{appointment.id}",
            meta={
                "lastUpdated": appointment.updated_at.isoformat(),
            },
            status=status_map.get(appointment.status, "booked"),
            appointmentType={
                "text": appointment.appointment_type,
            },
            description=appointment.title,
            start=appointment.start_time.isoformat(),
            end=appointment.end_time.isoformat(),
            created=appointment.created_at.isoformat(),
            participant=[
                {
                    "actor": {
                        "reference": f"Patient/{appointment.patient.fhir_id or f'patient-{appointment.patient_id}'}",
                        "display": appointment.patient.full_name,
                    },
                    "status": "accepted",
                },
                {
                    "actor": {
                        "reference": f"Practitioner/practitioner-{appointment.created_by_id}",
                        "display": appointment.created_by.full_name,
                    },
                    "status": "accepted",
                },
            ],
        )
        
        if appointment.description:
            fhir_appointment.comment = appointment.description
        
        if appointment.location:
            fhir_appointment.participant.append({
                "actor": {
                    "display": appointment.location,
                },
                "status": "accepted",
            })
        
        return fhir_appointment
    
    def fhir_to_patient(self, fhir_patient: FHIRPatient) -> Dict[str, Any]:
        """Convert a FHIR Patient resource to a Patient model dictionary."""
        patient_data = {
            "fhir_id": fhir_patient.id,
            "fhir_resource_type": "Patient",
        }
        
        # Extract basic information
        if hasattr(fhir_patient, "name") and fhir_patient.name:
            for name in fhir_patient.name:
                if name.use == "official" or not patient_data.get("first_name"):
                    if hasattr(name, "given") and name.given:
                        patient_data["first_name"] = name.given[0]
                    if hasattr(name, "family"):
                        patient_data["last_name"] = name.family
        
        if hasattr(fhir_patient, "birthDate"):
            patient_data["date_of_birth"] = fhir_patient.birthDate
        
        if hasattr(fhir_patient, "gender"):
            patient_data["gender"] = fhir_patient.gender
        
        if hasattr(fhir_patient, "active"):
            patient_data["is_active"] = fhir_patient.active
        
        # Extract identifiers
        if hasattr(fhir_patient, "identifier") and fhir_patient.identifier:
            for identifier in fhir_patient.identifier:
                if identifier.system == "http://eira.clinical/mrn":
                    patient_data["medical_record_number"] = identifier.value
        
        # Extract contact information
        if hasattr(fhir_patient, "telecom") and fhir_patient.telecom:
            for telecom in fhir_patient.telecom:
                if telecom.system == "phone":
                    patient_data["phone"] = telecom.value
                elif telecom.system == "email":
                    patient_data["email"] = telecom.value
        
        # Extract address
        if hasattr(fhir_patient, "address") and fhir_patient.address:
            for address in fhir_patient.address:
                if address.use == "home" or not patient_data.get("address"):
                    if hasattr(address, "text"):
                        patient_data["address"] = address.text
        
        # Extract emergency contact
        if hasattr(fhir_patient, "contact") and fhir_patient.contact:
            for contact in fhir_patient.contact:
                if hasattr(contact, "relationship"):
                    for relationship in contact.relationship:
                        if relationship.text == "Emergency Contact":
                            if hasattr(contact, "name") and hasattr(contact.name, "text"):
                                patient_data["emergency_contact_name"] = contact.name.text
                            if hasattr(contact, "telecom") and contact.telecom:
                                for telecom in contact.telecom:
                                    if telecom.system == "phone":
                                        patient_data["emergency_contact_phone"] = telecom.value
        
        return patient_data


# Create a singleton instance
fhir_service = FHIRService()