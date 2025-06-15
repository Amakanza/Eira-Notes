from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class SyncEntityChange(BaseModel):
    entity_type: str = Field(..., description="Entity type, e.g. user, patient, appointment, clinical_note")
    entity_id: str = Field(..., description="Entity ID as string (int or uuid)")
    operation: str = Field(..., description="Operation: create, update, delete")
    payload: Dict[str, Any] = Field(..., description="Entity data as dict (for create/update)")
    status: Optional[str] = Field(None, description="Sync status (optional)")
    error_message: Optional[str] = Field(None, description="Error message if any (optional)")
    updated_at: Optional[str] = Field(None, description="ISO8601 timestamp of last update")

class SyncPushRequest(BaseModel):
    changes: List[SyncEntityChange]

class SyncPushResponse(BaseModel):
    status: str
    results: List[Dict[str, Any]]

class SyncPullResponse(BaseModel):
    status: str
    changes: List[SyncEntityChange]