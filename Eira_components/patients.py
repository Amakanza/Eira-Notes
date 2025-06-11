from .database import DB_PATH
import sqlite3
from datetime import datetime

def get_patients(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE user_id = ? ORDER BY last_name, first_name", (user_id,))
    patients = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return patients

def show_patients(patient_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = dict(cursor.fetchone()) if cursor.fetchone() else None
    conn.close()

    return patient

def add_patients(data, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """INSERT INTO patients (
                first_name, last_name, id_number, date_of_birth, gender, phone, email,
                address, medical_aid_name, medical_aid_number, medical_history, diagnosis, icd_code, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data["first_name"], data["last_name"], data["id_number"], data["date_of_birth"], data["gender"],
                data["phone"], data["email"], data["address"], data["medical_aid_name"],
                data["medical_aid_number"], data["medical_history"], data["diagnosis"], data["icd_code"], user_id
            )
        )
        conn.commit()
        patient_id = cursor.lastrowid
        result = {"success": True, "message": "Patient added successfully", "patient_id": patient_id}
    except Exception as e:
        conn.rollback()
        result = {"success": False, "message": f"Error adding patient: {str(e)}"}
    finally:
        conn.close()

    return result

def update_patient(patient_id, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """UPDATE patients SET
                first_name = ?, last_name = ?, id_number = ?, date_of_birth = ?, gender = ?, phone = ?, email = ?,
                address = ?, medical_aid_name = ?, medical_aid_number = ?, medical_history = ?, diagnosis = ?, icd_code = ?
            WHERE id = ?""",
            (
                data["first_name"], data["last_name"], data["id_number"], data["date_of_birth"], data["gender"],
                data["phone"], data["email"], data["address"], data["medical_aid_name"],
                data["medical_aid_number"], data["medical_history"], data["diagnosis"], data["icd_code"], patient_id
            )
        )
        conn.commit()
        result = {"success": True, "message": "Patient updated successfully"}
    except Exception as e:
        conn.rollback()
        result = {"success": False, "message": f"Error updating patient: {str(e)}"}
    finally:
        conn.close()

    return result

def delete_patient(patient_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Delete associated records first (due to foreign key constraints)
        cursor.execute("DELETE FROM soap_notes WHERE patient_id = ?", (patient_id,))
        cursor.execute("DELETE FROM appointments WHERE patient_id = ?", (patient_id,))
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        conn.commit()
        result = {"success": True, "message": "Patient and all associated records deleted"}
    except Exception as e:
        conn.rollback()
        result = {"success": False, "message": f"Error deleting patient: {str(e)}"}
    finally:
        conn.close()

    return result

