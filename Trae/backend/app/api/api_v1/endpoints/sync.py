from datetime import datetime, timezone
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user
from app.db.init_db import get_db
from app.db.models.user import User
from app.schemas.sync import SyncPushRequest, SyncPushResponse, SyncPullResponse, SyncEntityChange
from app.services import sync as sync_service

router = APIRouter()

@router.post("/push", response_model=SyncPushResponse)
async def push_changes(
    request: SyncPushRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Push changes from client to server.
    
    This endpoint receives a list of entity changes from the client and processes them.
    For each change, it will:
    1. Create, update, or delete the entity as specified
    2. Track the change in the sync outbox for other clients to pull
    3. Return the result of each operation
    """
    results = []
    
    for change in request.changes:
        # Process the entity change
        result = await sync_service.process_entity_change(db, change, current_user)
        
        # If successful, track the change in the outbox for other clients
        if result["status"] == "success":
            # Only track successful changes
            await sync_service.track_entity_change(
                db, 
                change.entity_type, 
                result["entity_id"],  # Use the possibly updated entity ID
                change.operation, 
                change.payload
            )
        
        results.append(result)
    
    return SyncPushResponse(status="success", results=results)

@router.get("/pull", response_model=SyncPullResponse)
async def pull_changes(
    since: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Pull changes from server to client.
    
    This endpoint returns all changes that have occurred since the given timestamp.
    The client can use this to synchronize its local database with the server.
    
    Args:
        since: ISO8601 timestamp of the last sync
    """
    try:
        # Parse the timestamp
        since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
        
        # Get all changes since the timestamp
        changes = await sync_service.get_changes_since(db, since_dt)
        
        return SyncPullResponse(status="success", changes=changes)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid timestamp format. Use ISO8601 format (e.g., 2023-01-01T00:00:00Z)"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error pulling changes: {str(e)}"
        )