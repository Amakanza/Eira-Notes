import json
from typing import Any, Dict, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.sync_outbox import SyncOperationType, SyncOutbox, SyncStatus
from app.db.models.user import User
from app.db.models.patient import Patient
from app.db.models.appointment import Appointment
from app.db.models.clinical_note import ClinicalNote, Attachment


async def track_entity_creation(db: AsyncSession, entity: Any) -> None:
    """Track the creation of an entity in the sync outbox."""
    entity_type = _get_entity_type(entity)
    if not entity_type:
        return  # Unsupported entity type
    
    # Create a new sync outbox entry
    sync_outbox = SyncOutbox(
        entity_type=entity_type,
        entity_id=str(entity.id),
        operation=SyncOperationType.CREATE,
        payload=json.dumps(_entity_to_dict(entity)),
        status=SyncStatus.SYNCED  # Already synced since it was just created
    )
    
    db.add(sync_outbox)
    # No need to commit here as it will be committed with the entity creation


async def track_entity_update(db: AsyncSession, entity: Any, updated_fields: Dict[str, Any]) -> None:
    """Track the update of an entity in the sync outbox."""
    entity_type = _get_entity_type(entity)
    if not entity_type:
        return  # Unsupported entity type
    
    # Create a new sync outbox entry
    sync_outbox = SyncOutbox(
        entity_type=entity_type,
        entity_id=str(entity.id),
        operation=SyncOperationType.UPDATE,
        payload=json.dumps(_entity_to_dict(entity)),
        status=SyncStatus.SYNCED  # Already synced since it was just updated
    )
    
    db.add(sync_outbox)
    # No need to commit here as it will be committed with the entity update


async def track_entity_deletion(db: AsyncSession, entity: Any) -> None:
    """Track the deletion of an entity in the sync outbox."""
    entity_type = _get_entity_type(entity)
    if not entity_type:
        return  # Unsupported entity type
    
    # Create a new sync outbox entry
    sync_outbox = SyncOutbox(
        entity_type=entity_type,
        entity_id=str(entity.id),
        operation=SyncOperationType.DELETE,
        payload=json.dumps({"id": entity.id}),  # Only need the ID for deletion
        status=SyncStatus.SYNCED  # Already synced since it was just deleted
    )
    
    db.add(sync_outbox)
    # No need to commit here as it will be committed with the entity deletion


def _get_entity_type(entity: Any) -> Optional[str]:
    """Get the entity type as a string."""
    if isinstance(entity, Patient):
        return "patient"
    elif isinstance(entity, Appointment):
        return "appointment"
    elif isinstance(entity, ClinicalNote):
        return "clinical_note"
    elif isinstance(entity, Attachment):
        return "attachment"
    elif isinstance(entity, User):
        return "user"
    else:
        return None


def _entity_to_dict(entity: Any) -> Dict[str, Any]:
    """Convert an entity to a dictionary for JSON serialization."""
    result = {}
    
    # Get all attributes that don't start with _ and aren't callables
    for key in dir(entity):
        if not key.startswith('_') and not callable(getattr(entity, key)):
            try:
                value = getattr(entity, key)
                # Skip relationship attributes
                if not hasattr(value, '__table__'):
                    # Handle datetime objects
                    if hasattr(value, 'isoformat'):
                        result[key] = value.isoformat()
                    else:
                        result[key] = value
            except Exception:
                # Skip attributes that can't be serialized
                pass
    
    return result