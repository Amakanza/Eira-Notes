import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

from .database import DB_PATH


def authenticate(username: str, password: str):
    """Return user dict if credentials are valid."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, password_hash, first_name, last_name FROM users WHERE username = ?",
        (username,),
    )
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user[1], password):
        return {"id": user[0], "first_name": user[2], "last_name": user[3]}
    return None


def register_user(username: str, email: str, password: str, first_name: str, last_name: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            (username, email, password_hash, first_name, last_name),
        )
        conn.commit()
        return {"success": True, "message": "User registered successfully"}
    except sqlite3.IntegrityError as e:
        conn.rollback()
        msg = "Registration error"
        if "username" in str(e):
            msg = "Username already exists"
        elif "email" in str(e):
            msg = "Email already exists"
        return {"success": False, "message": msg}
    finally:
        conn.close()
