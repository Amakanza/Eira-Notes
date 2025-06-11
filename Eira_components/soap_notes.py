from .database import DB_PATH
import sqlite3

def get_soap_notes(patient_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """SELECT n.*, u.first_name || ' ' || u.last_name as therapist_name 
        FROM soap_notes n
        JOIN users u ON n.created_by = u.id
        WHERE n.patient_id = ?
        ORDER BY n.date DESC""",
        (patient_id,)
    )
    notes = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return notes

def get_soap_note(note_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """SELECT n.*, u.first_name || ' ' || u.last_name as therapist_name 
        FROM soap_notes n
        JOIN users u ON n.created_by = u.id
        WHERE n.id = ?""",
        (note_id,)
    )
    note = dict(cursor.fetchone()) if cursor.fetchone() else None
    conn.close()

    return note

def add_soap_note(data, patient_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """INSERT INTO soap_notes (
                date, subjective, objective, action, plan, 
                treatment_provided, patient_response, goals_progress,
                patient_id, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data["date"], data["subjective"], data["objective"], data["action"], data["plan"],
                data.get("treatment_provided"), data.get("patient_response"), data.get("goals_progress"),
                patient_id, user_id
            )
        )
        conn.commit()
        note_id = cursor.lastrowid
        result = {"success": True, "message": "SOAP note added successfully", "note_id": note_id}
    except Exception as e:
        conn.rollback()
        result = {"success": False, "message": f"Error adding SOAP note: {str(e)}"}
    finally:
        conn.close()

    return result

def update_soap_note(note_id, data, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """UPDATE soap_notes SET
                date = ?, subjective = ?, objective = ?, action = ?, plan = ?,
                treatment_provided = ?, patient_response = ?, goals_progress = ?
            WHERE id = ? AND created_by = ?""",
            (
                data["date"], data["subjective"], data["objective"], data["action"], data["plan"],
                data.get("treatment_provided"), data.get("patient_response"), data.get("goals_progress"),
                note_id, user_id
            )
        )
        conn.commit()
        result = {"success": true, "message": "SOAP note updated successfully"}
    except Exception as e:
        conn.rollback()
        result = {"success": False, "message": f"Error updating SOAP note: {str(e)}"}
    finally:
        conn.close()

    return result

def delete_soap_note(note_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM soap_notes WHERE id = ? AND created_by = ?",
            (note_id, user_id),
        )
        conn.commit()
        result = {"success": True, "message": "SOAP note deleted successfully"}
    except Exception as e:
        conn.rollback()
        result = {"success": False, "message": f"Error deleting SOAP note: {str(e)}"}
    finally:
        conn.close()

    return result
