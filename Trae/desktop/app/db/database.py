import asyncio
import json
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from app.core.config import settings
from app.sync.sync_manager import OperationType, SyncManager

logger = logging.getLogger(__name__)


class Database:
    """Database wrapper that handles local SQLite operations with sync capabilities."""

    def __init__(self, db_path: str = None, api_url: str = None, auth_token: str = None, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.loop = loop
        self.db_path = db_path or settings.DB_PATH
        self.api_url = api_url or settings.API_URL
        
        # Ensure the database directory exists
        Path(os.path.dirname(self.db_path)).mkdir(parents=True, exist_ok=True)
        
        # Initialize the database
        self._init_db()
        
        # Initialize the sync manager
        self.sync_manager = SyncManager(
            db_path=self.db_path,
            api_url=self.api_url,
            auth_token=auth_token,
            auto_sync_interval=settings.AUTO_SYNC_INTERVAL,
            loop=self.loop,
        )

    def _init_db(self) -> None:
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create users table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                full_name TEXT,
                role TEXT NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_synced_at TEXT
            )
            """
        )

        # Create patients table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                gender TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                email TEXT,
                insurance_provider TEXT,
                insurance_id TEXT,
                medical_history TEXT,
                allergies TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_synced_at TEXT
            )
            """
        )

        # Create clinical_notes table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clinical_notes (
                id INTEGER PRIMARY KEY,
                patient_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                visit_date TEXT NOT NULL,
                chief_complaint TEXT,
                history_of_present_illness TEXT,
                review_of_systems TEXT,
                physical_examination TEXT,
                assessment TEXT,
                plan TEXT,
                signature_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_synced_at TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )

        # Create appointments table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY,
                patient_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                appointment_type TEXT NOT NULL,
                status TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_synced_at TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )

        # Create files table for tracking uploaded files
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                uploaded BOOLEAN NOT NULL DEFAULT 0,
                remote_url TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_synced_at TEXT
            )
            """
        )

        conn.commit()
        conn.close()

    def set_auth_token(self, token: str) -> None:
        """Set the authentication token for API requests."""
        self.sync_manager.set_auth_token(token)

    def set_online_status(self, is_online: bool) -> None:
        """Set the online status and trigger sync if coming online."""
        self.sync_manager.set_online_status(is_online)

    def start_auto_sync(self) -> None:
        """Start automatic background synchronization."""
        self.sync_manager.start_auto_sync()

    def stop_auto_sync(self) -> None:
        """Stop automatic background synchronization."""
        self.sync_manager.stop_auto_sync()

    async def sync(self) -> Dict[str, Any]:
        """Perform a full sync operation."""
        return await self.sync_manager.sync()

    # User operations
    def get_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of users."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users ORDER BY last_name, first_name LIMIT ? OFFSET ?",
            (limit, skip),
        )
        users = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return users

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        conn.close()
        return dict(user) if user else None

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        user_data["created_at"] = now
        user_data["updated_at"] = now

        # Extract fields from user_data
        fields = [
            "username",
            "email",
            "full_name",
            "role",
            "is_active",
            "created_at",
            "updated_at",
        ]
        values = [user_data.get(field) for field in fields]
        placeholders = ", ".join(["?" for _ in fields])
        fields_str = ", ".join(fields)

        cursor.execute(
            f"INSERT INTO users ({fields_str}) VALUES ({placeholders})", values
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Queue for sync
        user_data["id"] = user_id
        self.sync_manager.queue_change(
            "users", OperationType.CREATE, user_id, user_data
        )

        return {**user_data, "id": user_id}

    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current user data
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        current_user = cursor.fetchone()
        if not current_user:
            conn.close()
            raise ValueError(f"User with ID {user_id} not found")

        # Update user data
        user_data["updated_at"] = datetime.now().isoformat()
        set_clause = ", ".join([f"{key} = ?" for key in user_data.keys()])
        values = list(user_data.values()) + [user_id]

        cursor.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()

        # Queue for sync
        self.sync_manager.queue_change(
            "users", OperationType.UPDATE, user_id, user_data
        )

        return {**user_data, "id": user_id}

    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if deleted:
            # Queue for sync
            self.sync_manager.queue_change("users", OperationType.DELETE, user_id)

        return deleted

    # Patient operations
    def get_patients(
        self, skip: int = 0, limit: int = 100, search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get list of patients with optional search."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM patients"
        params = []

        if search:
            query += " WHERE first_name LIKE ? OR last_name LIKE ? OR phone LIKE ? OR email LIKE ?"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])

        query += " ORDER BY last_name, first_name LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        cursor.execute(query, params)
        patients = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return patients

    def get_patient(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """Get patient by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient = cursor.fetchone()

        conn.close()
        return dict(patient) if patient else None

    def create_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new patient."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        patient_data["created_at"] = now
        patient_data["updated_at"] = now

        # Extract fields from patient_data
        fields = [
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
            "address",
            "phone",
            "email",
            "insurance_provider",
            "insurance_id",
            "medical_history",
            "allergies",
            "created_at",
            "updated_at",
        ]
        values = [patient_data.get(field) for field in fields]
        placeholders = ", ".join(["?" for _ in fields])
        fields_str = ", ".join(fields)

        cursor.execute(
            f"INSERT INTO patients ({fields_str}) VALUES ({placeholders})", values
        )
        patient_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Queue for sync
        patient_data["id"] = patient_id
        self.sync_manager.queue_change(
            "patients", OperationType.CREATE, patient_id, patient_data
        )

        return {**patient_data, "id": patient_id}

    def update_patient(self, patient_id: int, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a patient."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current patient data
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        current_patient = cursor.fetchone()
        if not current_patient:
            conn.close()
            raise ValueError(f"Patient with ID {patient_id} not found")

        # Update patient data
        patient_data["updated_at"] = datetime.now().isoformat()
        set_clause = ", ".join([f"{key} = ?" for key in patient_data.keys()])
        values = list(patient_data.values()) + [patient_id]

        cursor.execute(f"UPDATE patients SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()

        # Queue for sync
        self.sync_manager.queue_change(
            "patients", OperationType.UPDATE, patient_id, patient_data
        )

        return {**patient_data, "id": patient_id}

    def delete_patient(self, patient_id: int) -> bool:
        """Delete a patient."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if deleted:
            # Queue for sync
            self.sync_manager.queue_change("patients", OperationType.DELETE, patient_id)

        return deleted

    # Clinical notes operations
    def get_clinical_notes(
        self, patient_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get list of clinical notes, optionally filtered by patient."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM clinical_notes"
        params = []

        if patient_id:
            query += " WHERE patient_id = ?"
            params.append(patient_id)

        query += " ORDER BY visit_date DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        cursor.execute(query, params)
        notes = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return notes

    def get_clinical_note(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Get clinical note by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM clinical_notes WHERE id = ?", (note_id,))
        note = cursor.fetchone()

        conn.close()
        return dict(note) if note else None

    def create_clinical_note(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new clinical note."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        note_data["created_at"] = now
        note_data["updated_at"] = now

        # Extract fields from note_data
        fields = [
            "patient_id",
            "user_id",
            "visit_date",
            "chief_complaint",
            "history_of_present_illness",
            "review_of_systems",
            "physical_examination",
            "assessment",
            "plan",
            "signature_id",
            "created_at",
            "updated_at",
        ]
        values = [note_data.get(field) for field in fields]
        placeholders = ", ".join(["?" for _ in fields])
        fields_str = ", ".join(fields)

        cursor.execute(
            f"INSERT INTO clinical_notes ({fields_str}) VALUES ({placeholders})", values
        )
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Queue for sync
        note_data["id"] = note_id
        self.sync_manager.queue_change(
            "clinical_notes", OperationType.CREATE, note_id, note_data
        )

        return {**note_data, "id": note_id}

    def update_clinical_note(self, note_id: int, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a clinical note."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current note data
        cursor.execute("SELECT * FROM clinical_notes WHERE id = ?", (note_id,))
        current_note = cursor.fetchone()
        if not current_note:
            conn.close()
            raise ValueError(f"Clinical note with ID {note_id} not found")

        # Update note data
        note_data["updated_at"] = datetime.now().isoformat()
        set_clause = ", ".join([f"{key} = ?" for key in note_data.keys()])
        values = list(note_data.values()) + [note_id]

        cursor.execute(f"UPDATE clinical_notes SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()

        # Queue for sync
        self.sync_manager.queue_change(
            "clinical_notes", OperationType.UPDATE, note_id, note_data
        )

        return {**note_data, "id": note_id}

    def delete_clinical_note(self, note_id: int) -> bool:
        """Delete a clinical note."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM clinical_notes WHERE id = ?", (note_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if deleted:
            # Queue for sync
            self.sync_manager.queue_change(
                "clinical_notes", OperationType.DELETE, note_id
            )

        return deleted

    # Appointment operations
    def get_appointments(
        self,
        patient_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get list of appointments with optional filters."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM appointments"
        params = []
        conditions = []

        if patient_id:
            conditions.append("patient_id = ?")
            params.append(patient_id)

        if start_date:
            conditions.append("start_time >= ?")
            params.append(start_date)

        if end_date:
            conditions.append("end_time <= ?")
            params.append(end_date)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY start_time LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        cursor.execute(query, params)
        appointments = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return appointments

    def get_appointment(self, appointment_id: int) -> Optional[Dict[str, Any]]:
        """Get appointment by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
        appointment = cursor.fetchone()

        conn.close()
        return dict(appointment) if appointment else None

    def create_appointment(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new appointment."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        appointment_data["created_at"] = now
        appointment_data["updated_at"] = now

        # Extract fields from appointment_data
        fields = [
            "patient_id",
            "user_id",
            "start_time",
            "end_time",
            "appointment_type",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        values = [appointment_data.get(field) for field in fields]
        placeholders = ", ".join(["?" for _ in fields])
        fields_str = ", ".join(fields)

        cursor.execute(
            f"INSERT INTO appointments ({fields_str}) VALUES ({placeholders})", values
        )
        appointment_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Queue for sync
        appointment_data["id"] = appointment_id
        self.sync_manager.queue_change(
            "appointments", OperationType.CREATE, appointment_id, appointment_data
        )

        return {**appointment_data, "id": appointment_id}

    def update_appointment(
        self, appointment_id: int, appointment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an appointment."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current appointment data
        cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
        current_appointment = cursor.fetchone()
        if not current_appointment:
            conn.close()
            raise ValueError(f"Appointment with ID {appointment_id} not found")

        # Update appointment data
        appointment_data["updated_at"] = datetime.now().isoformat()
        set_clause = ", ".join([f"{key} = ?" for key in appointment_data.keys()])
        values = list(appointment_data.values()) + [appointment_id]

        cursor.execute(f"UPDATE appointments SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()

        # Queue for sync
        self.sync_manager.queue_change(
            "appointments", OperationType.UPDATE, appointment_id, appointment_data
        )

        return {**appointment_data, "id": appointment_id}

    def delete_appointment(self, appointment_id: int) -> bool:
        """Delete an appointment."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if deleted:
            # Queue for sync
            self.sync_manager.queue_change(
                "appointments", OperationType.DELETE, appointment_id
            )

        return deleted

    # File operations
    def register_file(
        self,
        file_path: str,
        file_type: str,
        entity_type: str,
        entity_id: int,
    ) -> Dict[str, Any]:
        """Register a file in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        file_id = os.path.basename(file_path)
        now = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT INTO files (
                id, file_path, file_type, entity_type, entity_id,
                uploaded, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (file_id, file_path, file_type, entity_type, entity_id, False, now, now),
        )
        conn.commit()
        conn.close()

        # Queue for sync - will be handled by a separate file upload process
        file_data = {
            "id": file_id,
            "file_path": file_path,
            "file_type": file_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "created_at": now,
            "updated_at": now,
        }

        return file_data

    def get_files_for_entity(self, entity_type: str, entity_id: int) -> List[Dict[str, Any]]:
        """Get files associated with an entity."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM files WHERE entity_type = ? AND entity_id = ?",
            (entity_type, entity_id),
        )
        files = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return files

    def mark_file_uploaded(self, file_id: str, remote_url: str) -> bool:
        """Mark a file as uploaded and store its remote URL."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute(
            "UPDATE files SET uploaded = ?, remote_url = ?, updated_at = ?, last_synced_at = ? WHERE id = ?",
            (True, remote_url, now, now, file_id),
        )
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return updated

    # Sync status operations
    def get_pending_changes(self) -> List[Dict[str, Any]]:
        """Get all pending changes that haven't been synced."""
        return self.sync_manager.get_pending_changes()

    def get_conflicts(self) -> List[Dict[str, Any]]:
        """Get all changes that resulted in conflicts."""
        return self.sync_manager.get_conflicts()

    def resolve_conflict(
        self, change_id: str, resolution: str, updated_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Resolve a conflict with the given resolution strategy."""
        self.sync_manager.resolve_conflict(change_id, resolution, updated_data)

    def clear_synced_changes(self, older_than_days: int = 7) -> int:
        """Clear successfully synced changes older than the specified days."""
        return self.sync_manager.clear_synced_changes(older_than_days)

    def reset_sync_state(self) -> None:
        """Reset the sync state (for testing or recovery)."""
        self.sync_manager.reset_sync_state()