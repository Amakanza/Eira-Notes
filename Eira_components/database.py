import os
import sqlite3
from werkzeug.security import generate_password_hash
import customtkinter as ctk

# Set up the database
DB_PATH = "data/eira_notes.db"

def init_db():
    # Connect to the database (will create it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create User table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'physiotherapist', 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Add role column to existing databases if missing
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    if 'role' not in existing_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'physiotherapist'")
        cursor.execute("UPDATE users SET role = 'physiotherapist' WHERE role IS NULL")

    
    # Create Patient table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        id_number TEXT,
        date_of_birth DATE NOT NULL,
        gender TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        medical_aid_name TEXT,
        medical_aid_number TEXT,
        medical_history TEXT,
        diagnosis TEXT NOT NULL,
        icd_code TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    try:
        cursor.execute("ALTER TABLE patients ADD COLUMN icd_code TEXT")
    except sqlite3.OperationalError:
        pass

    # Create SOAP Note table
    cursor.execute('''
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
    ''')
    
    # Create Appointment table
    cursor.execute('''
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
    ''')

    # Ensure id_number column exists in patients table
    cursor.execute("PRAGMA table_info(patients)")
    patient_columns = [col[1] for col in cursor.fetchall()]
    if 'id_number' not in patient_columns:
        cursor.execute("ALTER TABLE patients ADD COLUMN id_number TEXT")
    
    # Create a default admin user if it doesn't exist
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash("admin123")
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, first_name, last_name, role) VALUES (?, ?, ?, ?, ?, ?)",
            (
                "admin",
                "admin@example.com",
                password_hash,
                "Admin",
                "User",
                "administrator",
            ),
        )
    
    conn.commit()
    conn.close()
