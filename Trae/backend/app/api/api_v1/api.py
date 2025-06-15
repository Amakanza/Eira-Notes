from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    appointments,
    auth,
    clinical_notes,
    fhir,
    patients,
    reports,
    users,
    sync,  # <-- add sync import
)

api_router = APIRouter()

# Include all endpoint routers with appropriate prefixes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(clinical_notes.router, prefix="/clinical-notes", tags=["clinical-notes"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(fhir.router, prefix="/fhir", tags=["fhir"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])  # <-- register sync router