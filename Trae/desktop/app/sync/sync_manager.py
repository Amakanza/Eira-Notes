import asyncio
import json
import logging
import os
import sqlite3
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import httpx

logger = logging.getLogger(__name__)


class SyncStatus(str, Enum):
    PENDING = "pending"  # Local change waiting to be synced
    SYNCING = "syncing"  # Currently being synced
    SYNCED = "synced"    # Successfully synced with server
    CONFLICT = "conflict"  # Conflict detected
    ERROR = "error"      # Error during sync


class OperationType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class SyncManager:
    """Manages offline synchronization between local SQLite and remote API."""

    def __init__(
        self,
        db_path: str,
        api_url: str,
        auth_token: Optional[str] = None,
        auto_sync_interval: int = 60,  # seconds,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        self.db_path = db_path
        self.api_url = api_url
        self.auth_token = auth_token
        self.auto_sync_interval = auto_sync_interval
        self.loop = loop
        self.is_online = False
        self.sync_task = None
        self._setup_db()

    def _setup_db(self) -> None:
        """Set up the local SQLite database with sync tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create outbox table for tracking local changes
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_outbox (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                operation_type TEXT NOT NULL,
                data TEXT,
                status TEXT NOT NULL,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                retry_count INTEGER DEFAULT 0,
                idempotency_key TEXT NOT NULL
            )
            """
        )

        # Create sync metadata table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_metadata (
                entity_type TEXT NOT NULL,
                last_sync_time TEXT,
                PRIMARY KEY (entity_type)
            )
            """
        )

        # Initialize metadata for entity types
        for entity_type in ["users", "patients", "clinical_notes", "appointments"]:
            cursor.execute(
                "INSERT OR IGNORE INTO sync_metadata (entity_type, last_sync_time) VALUES (?, NULL)",
                (entity_type,),
            )

        conn.commit()
        conn.close()

    def set_auth_token(self, token: str) -> None:
        """Set the authentication token for API requests."""
        self.auth_token = token

    def set_online_status(self, is_online: bool) -> None:
        """Set the online status and trigger sync if coming online."""
        if not self.is_online and is_online:
            logger.info("Device came online, triggering sync")
            if self.loop:
                asyncio.run_coroutine_threadsafe(self.sync(), self.loop)
            else:
                asyncio.create_task(self.sync())
        self.is_online = is_online

    def start_auto_sync(self) -> None:
        """Start automatic background synchronization."""
        if self.sync_task is None or self.sync_task.done():
            if self.loop:
                self.sync_task = asyncio.run_coroutine_threadsafe(
                    self._auto_sync_loop(), self.loop
                )
            else:
                self.sync_task = asyncio.create_task(self._auto_sync_loop())

    def stop_auto_sync(self) -> None:
        """Stop automatic background synchronization."""
        if self.sync_task and not self.sync_task.done():
            self.sync_task.cancel()

    async def _auto_sync_loop(self) -> None:
        """Background task that periodically syncs data."""
        while True:
            try:
                if self.is_online:
                    await self.sync()
            except Exception as e:
                logger.error(f"Error in auto sync: {e}")
            await asyncio.sleep(self.auto_sync_interval)

    async def sync(self) -> Dict[str, Any]:
        """Perform a full sync operation."""
        if not self.is_online:
            return {"status": "offline", "message": "Device is offline"}

        try:
            # First push local changes to server
            push_result = await self._push_changes()

            # Then pull remote changes
            pull_result = await self._pull_changes()

            return {
                "status": "success",
                "pushed": push_result,
                "pulled": pull_result,
            }
        except Exception as e:
            logger.error(f"Sync error: {e}")
            return {"status": "error", "message": str(e)}

    async def _push_changes(self) -> Dict[str, int]:
        """Push local changes to the server using the sync API."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all pending changes
        cursor.execute(
            "SELECT * FROM sync_outbox WHERE status = ? ORDER BY created_at",
            (SyncStatus.PENDING.value,),
        )
        pending_changes = cursor.fetchall()

        results = {"success": 0, "error": 0, "conflict": 0}
        
        if not pending_changes:
            conn.close()
            return results
            
        # Convert pending changes to the format expected by the sync API
        changes_to_push = []
        change_ids = []
        
        for change in pending_changes:
            change_dict = dict(change)
            change_id = change_dict["id"]
            change_ids.append(change_id)
            
            # Mark as syncing
            cursor.execute(
                "UPDATE sync_outbox SET status = ?, updated_at = ? WHERE id = ?",
                (
                    SyncStatus.SYNCING.value,
                    datetime.now().isoformat(),
                    change_id,
                ),
            )
            
            # Prepare change data for API
            entity_type = change_dict["entity_type"]
            operation = change_dict["operation_type"]
            entity_id = change_dict["entity_id"]
            data = json.loads(change_dict["data"] or "{}")
            
            changes_to_push.append({
                "entity_type": entity_type,
                "entity_id": entity_id,
                "operation": operation,
                "data": data
            })
        
        conn.commit()
        
        # Push changes to server using the sync API
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json",
                }
                
                response = await client.post(
                    f"{self.api_url}/api/v1/sync/push",
                    json={"changes": changes_to_push},
                    headers=headers
                )
                
                if response.status_code == 200:
                    result_data = response.json()
                    processed_changes = result_data.get("processed", [])
                    
                    # Update status for each change based on server response
                    for i, change_result in enumerate(processed_changes):
                        if i < len(change_ids):
                            change_id = change_ids[i]
                            success = change_result.get("success", False)
                            error = change_result.get("error")
                            
                            if success:
                                cursor.execute(
                                    "UPDATE sync_outbox SET status = ?, updated_at = ? WHERE id = ?",
                                    (
                                        SyncStatus.SYNCED.value,
                                        datetime.now().isoformat(),
                                        change_id,
                                    ),
                                )
                                results["success"] += 1
                            else:
                                error_message = error or "Unknown error during sync"
                                if "conflict" in error_message.lower():
                                    status = SyncStatus.CONFLICT.value
                                    results["conflict"] += 1
                                else:
                                    status = SyncStatus.ERROR.value
                                    results["error"] += 1
                                    
                                cursor.execute(
                                    "UPDATE sync_outbox SET status = ?, error_message = ?, updated_at = ?, retry_count = retry_count + 1 WHERE id = ?",
                                    (
                                        status,
                                        error_message,
                                        datetime.now().isoformat(),
                                        change_id,
                                    ),
                                )
                else:
                    # If the entire request failed, mark all as error
                    for change_id in change_ids:
                        cursor.execute(
                            "UPDATE sync_outbox SET status = ?, error_message = ?, updated_at = ?, retry_count = retry_count + 1 WHERE id = ?",
                            (
                                SyncStatus.ERROR.value,
                                f"API Error: {response.status_code} - {response.text}",
                                datetime.now().isoformat(),
                                change_id,
                            ),
                        )
                    results["error"] += len(change_ids)
                    
        except Exception as e:
            # If there was an exception, mark all as error
            for change_id in change_ids:
                cursor.execute(
                    "UPDATE sync_outbox SET status = ?, error_message = ?, updated_at = ?, retry_count = retry_count + 1 WHERE id = ?",
                    (
                        SyncStatus.ERROR.value,
                        str(e),
                        datetime.now().isoformat(),
                        change_id,
                    ),
                )
            results["error"] += len(change_ids)
            logger.error(f"Error pushing changes: {e}")

        conn.commit()
        conn.close()
        return results

    async def _pull_changes(self) -> Dict[str, int]:
        """Pull remote changes from the server using the sync API."""
        if not self.auth_token:
            return {"error": "No authentication token"}

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get last sync times for each entity type
        cursor.execute("SELECT * FROM sync_metadata")
        sync_metadata = {row["entity_type"]: row["last_sync_time"] for row in cursor.fetchall()}

        results = {"users": 0, "patients": 0, "clinical_notes": 0, "appointments": 0, "error": 0}

        # Prepare the sync request payload with last sync times
        sync_request = {}
        for entity_type, last_sync_time in sync_metadata.items():
            if last_sync_time:
                sync_request[entity_type] = {"updated_after": last_sync_time}
            else:
                sync_request[entity_type] = {}

        headers = {"Authorization": f"Bearer {self.auth_token}"}
        endpoint = f"{self.api_url}/sync/pull"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, json=sync_request, headers=headers)
                
                if response.status_code == 200:
                    sync_data = response.json()
                    
                    # Process each entity type's data
                    for entity_type, data in sync_data.items():
                        if entity_type in results:
                            count = await self._process_pulled_data(entity_type, data)
                            results[entity_type] = count
                            
                            # Update last sync time
                            cursor.execute(
                                "UPDATE sync_metadata SET last_sync_time = ? WHERE entity_type = ?",
                                (datetime.now().isoformat(), entity_type),
                            )
                    
                    conn.commit()
                else:
                    logger.error(f"Error pulling changes: {response.status_code} - {response.text}")
                    results["error"] = 1
        except Exception as e:
            logger.error(f"Error pulling changes: {e}")
            results["error"] = 1

        conn.close()
        return results

    async def _process_pulled_data(self, entity_type: str, data: List[Dict[str, Any]]) -> int:
        """Process pulled data and update local database."""
        if not data:
            return 0
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        count = 0
        
        try:
            # Get the table name from entity_type (remove trailing 's' if present)
            table_name = entity_type[:-1] if entity_type.endswith('s') else entity_type
            
            for item in data:
                item_id = item.get('id')
                if not item_id:
                    logger.warning(f"Received {entity_type} item without ID, skipping")
                    continue
                    
                # Check if the item already exists
                cursor.execute(f"SELECT id FROM {table_name} WHERE id = ?", (item_id,))
                exists = cursor.fetchone() is not None
                
                # Get the columns for this table
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [row[1] for row in cursor.fetchall() if row[1] != 'id']
                
                # Filter the item data to only include columns that exist in the table
                filtered_data = {k: v for k, v in item.items() if k in columns}
                
                if exists:
                    # Update existing item
                    set_clause = ", ".join([f"{col} = ?" for col in filtered_data.keys()])
                    values = list(filtered_data.values())
                    
                    if set_clause:  # Only update if there are fields to update
                        query = f"UPDATE {table_name} SET {set_clause}, last_synced_at = ? WHERE id = ?"
                        values.append(datetime.now().isoformat())
                        values.append(item_id)
                        cursor.execute(query, values)
                else:
                    # Insert new item
                    columns_str = ", ".join(['id'] + list(filtered_data.keys()) + ['last_synced_at'])
                    placeholders = ", ".join(['?'] * (len(filtered_data) + 2))  # +2 for id and last_synced_at
                    
                    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                    values = [item_id] + list(filtered_data.values()) + [datetime.now().isoformat()]
                    cursor.execute(query, values)
                
                count += 1
                
            conn.commit()
        except Exception as e:
            logger.error(f"Error processing pulled data for {entity_type}: {e}")
            conn.rollback()
        finally:
            conn.close()
            
        return count

    def queue_change(
        self,
        entity_type: str,
        operation_type: OperationType,
        entity_id: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Queue a local change for synchronization."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        change_id = str(uuid.uuid4())
        idempotency_key = str(uuid.uuid4())
        now = datetime.now().isoformat()

        # For create operations, entity_id might be None (server will assign)
        # In this case, use a temporary negative ID
        if operation_type == OperationType.CREATE and entity_id is None:
            # Get the next negative ID to use as a temporary ID
            cursor.execute(
                "SELECT MIN(entity_id) FROM sync_outbox WHERE entity_type = ? AND entity_id < 0",
                (entity_type,),
            )
            result = cursor.fetchone()
            entity_id = -1 if result[0] is None else result[0] - 1

        cursor.execute(
            """
            INSERT INTO sync_outbox (
                id, entity_type, entity_id, operation_type, data, status,
                created_at, updated_at, idempotency_key
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                change_id,
                entity_type,
                entity_id,
                operation_type.value,
                json.dumps(data) if data else None,
                SyncStatus.PENDING.value,
                now,
                now,
                idempotency_key,
            ),
        )

        conn.commit()
        conn.close()

        # If we're online, trigger a sync
        if self.is_online:
            if self.loop:
                asyncio.run_coroutine_threadsafe(self.sync(), self.loop)
            else:
                asyncio.create_task(self.sync())

        return change_id

    def get_pending_changes(self) -> List[Dict[str, Any]]:
        """Get all pending changes that haven't been synced."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM sync_outbox WHERE status IN (?, ?) ORDER BY created_at",
            (SyncStatus.PENDING.value, SyncStatus.ERROR.value),
        )
        changes = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return changes

    def get_conflicts(self) -> List[Dict[str, Any]]:
        """Get all changes that resulted in conflicts."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM sync_outbox WHERE status = ? ORDER BY created_at",
            (SyncStatus.CONFLICT.value,),
        )
        conflicts = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return conflicts

    def resolve_conflict(
        self, change_id: str, resolution: str, updated_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Resolve a conflict with the given resolution strategy."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if resolution == "local_wins":
            # Keep local changes and retry
            cursor.execute(
                "UPDATE sync_outbox SET status = ?, updated_at = ?, data = ? WHERE id = ?",
                (
                    SyncStatus.PENDING.value,
                    datetime.now().isoformat(),
                    json.dumps(updated_data) if updated_data else None,
                    change_id,
                ),
            )
        elif resolution == "server_wins":
            # Accept server version and discard local changes
            cursor.execute(
                "UPDATE sync_outbox SET status = ?, updated_at = ? WHERE id = ?",
                (SyncStatus.SYNCED.value, datetime.now().isoformat(), change_id),
            )
        elif resolution == "merge":
            # Apply merged data
            if not updated_data:
                raise ValueError("Merged data must be provided for merge resolution")
            cursor.execute(
                "UPDATE sync_outbox SET status = ?, updated_at = ?, data = ? WHERE id = ?",
                (
                    SyncStatus.PENDING.value,
                    datetime.now().isoformat(),
                    json.dumps(updated_data),
                    change_id,
                ),
            )

        conn.commit()
        conn.close()

        # If we're online, trigger a sync
        if self.is_online:
            if self.loop:
                asyncio.run_coroutine_threadsafe(self.sync(), self.loop)
            else:
                asyncio.create_task(self.sync())

    def clear_synced_changes(self, older_than_days: int = 7) -> int:
        """Clear successfully synced changes older than the specified days."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Calculate cutoff date
        cutoff_date = (
            datetime.now()
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .timestamp()
            - (older_than_days * 24 * 60 * 60)
        )
        cutoff_date_str = datetime.fromtimestamp(cutoff_date).isoformat()

        cursor.execute(
            "DELETE FROM sync_outbox WHERE status = ? AND updated_at < ?",
            (SyncStatus.SYNCED.value, cutoff_date_str),
        )
        deleted_count = cursor.rowcount

        conn.commit()
        conn.close()

        return deleted_count

    def reset_sync_state(self) -> None:
        """Reset the sync state (for testing or recovery)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clear all sync data
        cursor.execute("DELETE FROM sync_outbox")
        cursor.execute("UPDATE sync_metadata SET last_sync_time = NULL")

        conn.commit()
        conn.close()