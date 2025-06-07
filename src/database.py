import os
import sqlite3

DB_PATH = "data/eira_notes.db"

# Ensure database directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_db():
    """Create tables and default admin user if needed."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth DATE NOT NULL,
            gender TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            medical_aid_name TEXT,
            medical_aid_number TEXT,
            medical_history TEXT,
            diagnosis TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS soap_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            subjective TEXT NOT NULL,
            objective TEXT NOT NULL,
            action TEXT NOT NULL,
            plan TEXT NOT NULL,
            treatment_provided TEXT,
            patient_response TEXT,
            goals_progress TEXT,
            patient_id INTEGER NOT NULL,
            created_by INTEGER NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            time TIME NOT NULL,
            duration INTEGER DEFAULT 60,
            notes TEXT,
            status TEXT DEFAULT 'scheduled',
            patient_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        '''
    )

    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        from werkzeug.security import generate_password_hash

        password_hash = generate_password_hash("admin123")
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            ("admin", "admin@example.com", password_hash, "Admin", "User"),
        )

    conn.commit()
    conn.close()


# ----------------------- Patient CRUD -----------------------

def get_patients(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE user_id = ? ORDER BY last_name, first_name",
        (user_id,),
    )
    patients = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return patients


def get_patient(patient_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    row = cursor.fetchone()
    patient = dict(row) if row else None
    conn.close()
    return patient


def add_patient(data, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO patients (
                first_name, last_name, date_of_birth, gender, phone, email,
                address, medical_aid_name, medical_aid_number, medical_history, diagnosis, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["first_name"],
                data["last_name"],
                data["date_of_birth"],
                data["gender"],
                data["phone"],
                data["email"],
                data["address"],
                data["medical_aid_name"],
                data["medical_aid_number"],
                data["medical_history"],
                data["diagnosis"],
                user_id,
            ),
        )
        conn.commit()
        patient_id = cursor.lastrowid
        return {"success": True, "message": "Patient added successfully", "patient_id": patient_id}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error adding patient: {e}"}
    finally:
        conn.close()


def update_patient(patient_id, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE patients SET
                first_name = ?, last_name = ?, date_of_birth = ?, gender = ?, phone = ?, email = ?,
                address = ?, medical_aid_name = ?, medical_aid_number = ?, medical_history = ?, diagnosis = ?
            WHERE id = ?
            """,
            (
                data["first_name"],
                data["last_name"],
                data["date_of_birth"],
                data["gender"],
                data["phone"],
                data["email"],
                data["address"],
                data["medical_aid_name"],
                data["medical_aid_number"],
                data["medical_history"],
                data["diagnosis"],
                patient_id,
            ),
        )
        conn.commit()
        return {"success": True, "message": "Patient updated successfully"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error updating patient: {e}"}
    finally:
        conn.close()


def delete_patient(patient_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM soap_notes WHERE patient_id = ?", (patient_id,))
        cursor.execute("DELETE FROM appointments WHERE patient_id = ?", (patient_id,))
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        conn.commit()
        return {"success": True, "message": "Patient and related records deleted"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error deleting patient: {e}"}
    finally:
        conn.close()


# ----------------------- SOAP Note CRUD -----------------------

def get_soap_notes(patient_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT n.*, u.first_name || ' ' || u.last_name as therapist_name
        FROM soap_notes n
        JOIN users u ON n.created_by = u.id
        WHERE n.patient_id = ?
        ORDER BY n.date DESC
        """,
        (patient_id,),
    )
    notes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return notes


def get_soap_note(note_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT n.*, u.first_name || ' ' || u.last_name as therapist_name
        FROM soap_notes n
        JOIN users u ON n.created_by = u.id
        WHERE n.id = ?
        """,
        (note_id,),
    )
    row = cursor.fetchone()
    note = dict(row) if row else None
    conn.close()
    return note


def add_soap_note(data, patient_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO soap_notes (
                date, subjective, objective, action, plan,
                treatment_provided, patient_response, goals_progress,
                patient_id, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["date"],
                data["subjective"],
                data["objective"],
                data["action"],
                data["plan"],
                data.get("treatment_provided"),
                data.get("patient_response"),
                data.get("goals_progress"),
                patient_id,
                user_id,
            ),
        )
        conn.commit()
        note_id = cursor.lastrowid
        return {"success": True, "message": "SOAP note added", "note_id": note_id}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error adding SOAP note: {e}"}
    finally:
        conn.close()


def update_soap_note(note_id, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE soap_notes SET
                date = ?, subjective = ?, objective = ?, action = ?, plan = ?,
                treatment_provided = ?, patient_response = ?, goals_progress = ?
            WHERE id = ?
            """,
            (
                data["date"],
                data["subjective"],
                data["objective"],
                data["action"],
                data["plan"],
                data.get("treatment_provided"),
                data.get("patient_response"),
                data.get("goals_progress"),
                note_id,
            ),
        )
        conn.commit()
        return {"success": True, "message": "SOAP note updated"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error updating SOAP note: {e}"}
    finally:
        conn.close()


def delete_soap_note(note_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM soap_notes WHERE id = ?", (note_id,))
        conn.commit()
        return {"success": True, "message": "SOAP note deleted"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error deleting SOAP note: {e}"}
    finally:
        conn.close()


# ----------------------- Appointment CRUD -----------------------

def get_appointments(user_id, filter_type=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = (
        "SELECT a.*, p.first_name || ' ' || p.last_name as patient_name "
        "FROM appointments a JOIN patients p ON a.patient_id = p.id "
        "WHERE a.user_id = ?"
    )
    params = [user_id]

    if filter_type == "today":
        query += " AND date(a.date) = date('now')"
    elif filter_type == "upcoming":
        query += " AND (date(a.date) >= date('now') AND a.status = 'scheduled')"

    query += " ORDER BY a.date, a.time"
    cursor.execute(query, params)
    appointments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return appointments


def get_appointment(appointment_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a.*, p.first_name || ' ' || p.last_name as patient_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.id = ?
        """,
        (appointment_id,),
    )
    row = cursor.fetchone()
    appointment = dict(row) if row else None
    conn.close()
    return appointment


def add_appointment(data, patient_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO appointments (
                date, time, duration, notes, status, patient_id, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["date"],
                data["time"],
                data["duration"],
                data.get("notes"),
                data["status"],
                patient_id,
                user_id,
            ),
        )
        conn.commit()
        appt_id = cursor.lastrowid
        return {"success": True, "message": "Appointment added", "appointment_id": appt_id}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error adding appointment: {e}"}
    finally:
        conn.close()


def update_appointment(appointment_id, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE appointments SET
                date = ?, time = ?, duration = ?, notes = ?, status = ?
            WHERE id = ?
            """,
            (
                data["date"],
                data["time"],
                data["duration"],
                data.get("notes"),
                data["status"],
                appointment_id,
            ),
        )
        conn.commit()
        return {"success": True, "message": "Appointment updated"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error updating appointment: {e}"}
    finally:
        conn.close()


def delete_appointment(appointment_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        conn.commit()
        return {"success": True, "message": "Appointment deleted"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error deleting appointment: {e}"}
    finally:
        conn.close()
