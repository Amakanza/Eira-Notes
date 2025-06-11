from werkzeug.security import generate_password_hash, check_password_hash
from .database import DB_PATH
import sqlite3
import customtkinter as ctk
from tkinter import messagebox

# Authentication functions
def authenticate(username, password):
    from werkzeug.security import check_password_hash
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, password_hash, first_name, last_name, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user[1], password):
        return {
            "id": user[0],
            "first_name": user[2],
            "last_name": user[3],
            "role": user[4],
        }
    return None

def register_user(username: str,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    role: str = "physiotherapist",
    ):
    from werkzeug.security import generate_password_hash
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, first_name, last_name, role) VALUES (?, ?, ?, ?, ?, ?)",
            (username, email, password_hash, first_name, last_name, role)
        )
        conn.commit()
        result = {"success": True, "message": "User registered successfully"}
    except sqlite3.IntegrityError as e:
        conn.rollback()
        if "username" in str(e):
            result = {"success": False, "message": "Username already exists"}
        elif "email" in str(e):
            result = {"success": False, "message": "Email already exists"}
        else:
            result = {"success": False, "message": f"Registration error: {str(e)}"}
    finally:
        conn.close()
    
    return result


def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email, first_name, last_name, role FROM users ORDER BY username"
    )
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users


def update_user_role(user_id, role):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
        conn.commit()
        return {"success": True, "message": "Role updated"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error updating role: {e}"}
    finally:
        conn.close()

def show_login(self):
    self.clear_content()
    
    # Create login frame
    login_frame = ctk.CTkFrame(self.content_frame)
    login_frame.grid(row=0, column=0, sticky="", padx=20, pady=20)
    self.current_frame = login_frame
    
    # Title
    title_label = ctk.CTkLabel(login_frame, text="Login to Eira Notes", font=ctk.CTkFont(size=24, weight="bold"))
    title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 30))
    
    # Username
    username_label = ctk.CTkLabel(login_frame, text="Username:")
    username_label.grid(row=1, column=0, sticky="e", padx=(20, 10), pady=10)
    username_entry = ctk.CTkEntry(login_frame, width=200)
    username_entry.grid(row=1, column=1, sticky="w", padx=(10, 20), pady=10)
    username_entry.focus()
    
    # Password
    password_label = ctk.CTkLabel(login_frame, text="Password:")
    password_label.grid(row=2, column=0, sticky="e", padx=(20, 10), pady=10)
    password_entry = ctk.CTkEntry(login_frame, width=200, show="•")
    password_entry.grid(row=2, column=1, sticky="w", padx=(10, 20), pady=10)
    
    # Error message
    error_label = ctk.CTkLabel(login_frame, text="", text_color="red")
    error_label.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 0))
    
    # Login button
    def handle_login():
        username = username_entry.get()
        password = password_entry.get()
        
        if not username or not password:
            error_label.configure(text="Please enter both username and password")
            return
        
        user = authenticate(username, password)
        if user:
            self.current_user = user
            self.create_sidebar()
            self.show_home()
        else:
            error_label.configure(text="Invalid username or password")
    
    login_button = ctk.CTkButton(login_frame, text="Login", command=handle_login)
    login_button.grid(row=4, column=0, columnspan=2, padx=20, pady=(20, 10))
    
    # Register link
    def show_register():
        self.show_register()
    
    register_link = ctk.CTkButton(login_frame, text="Register New Account", fg_color="transparent", command=show_register)
    register_link.grid(row=5, column=0, columnspan=2, padx=20, pady=(10, 20))

def show_register(self):
    self.clear_content()
 
    register_frame = ctk.CTkFrame(self.content_frame)
    register_frame.grid(row=0, column=0, sticky="", padx=20, pady=20)
    self.current_frame = register_frame

    # Title
    title_label = ctk.CTkLabel(register_frame, text="Register New Account", font=ctk.CTkFont(size=24, weight="bold"))
    title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 30))

    # Username
    ctk.CTkLabel(register_frame, text="Username:").grid(row=1, column=0, sticky="e", padx=(20,10), pady=10)
    username_entry = ctk.CTkEntry(register_frame, width=200)
    username_entry.grid(row=1, column=1, sticky="w", padx=(10,20), pady=10)

    # Email
    ctk.CTkLabel(register_frame, text="Email:").grid(row=2, column=0, sticky="e", padx=(20,10), pady=10)
    email_entry = ctk.CTkEntry(register_frame, width=200)
    email_entry.grid(row=2, column=1, sticky="w", padx=(10,20), pady=10)

    # First Name
    ctk.CTkLabel(register_frame, text="First Name:").grid(row=3, column=0, sticky="e", padx=(20,10), pady=10)
    first_name_entry = ctk.CTkEntry(register_frame, width=200)
    first_name_entry.grid(row=3, column=1, sticky="w", padx=(10,20), pady=10)

    # Last Name
    ctk.CTkLabel(register_frame, text="Last Name:").grid(row=4, column=0, sticky="e", padx=(20,10), pady=10)
    last_name_entry = ctk.CTkEntry(register_frame, width=200)
    last_name_entry.grid(row=4, column=1, sticky="w", padx=(10,20), pady=10)

    # Role Selector
    ctk.CTkLabel(register_frame, text="Role:").grid(row=5, column=0, sticky="e", padx=(20,10), pady=10)
    role_var = ctk.StringVar(value="physiotherapist")
    role_dropdown = ctk.CTkOptionMenu(
        register_frame,
        variable=role_var,
        values=["administrator", "physiotherapist", "receptionist"]
    )
    role_dropdown.grid(row=5, column=1, sticky="w", padx=(10,20), pady=10)

    # Password
    ctk.CTkLabel(register_frame, text="Password:").grid(row=6, column=0, sticky="e", padx=(20,10), pady=10)
    password_entry = ctk.CTkEntry(register_frame, width=200, show="•")
    password_entry.grid(row=6, column=1, sticky="w", padx=(10,20), pady=10)

    # Confirm Password
    ctk.CTkLabel(register_frame, text="Confirm Password:").grid(row=7, column=0, sticky="e", padx=(20,10), pady=10)
    confirm_entry = ctk.CTkEntry(register_frame, width=200, show="•")
    confirm_entry.grid(row=7, column=1, sticky="w", padx=(10,20), pady=10)

    # Error message
    error_label = ctk.CTkLabel(register_frame, text="", text_color="red")
    error_label.grid(row=8, column=0, columnspan=2, padx=20, pady=(10,0))

    # Register button handler
    def handle_register():
        username = username_entry.get().strip()
        email = email_entry.get().strip()
        first_name = first_name_entry.get().strip()
        last_name = last_name_entry.get().strip()
        password = password_entry.get()
        confirm = confirm_entry.get()
        role = role_var.get()

        # Validation
        if not all([username, email, first_name, last_name, password, confirm]):
            error_label.configure(text="All fields are required")
            return
        if password != confirm:
            error_label.configure(text="Passwords do not match")
            return
        if len(password) < 8:
            error_label.configure(text="Password must be at least 8 characters")
            return

        # Call register_user with role
        result = register_user(username, email, password, first_name, last_name, role)
        if result["success"]:
            messagebox.showinfo("Registration Successful", "Your account has been created. You can now log in.")
            self.show_login()
        else:
            error_label.configure(text=result["message"])

    ctk.CTkButton(register_frame, text="Register", command=handle_register).grid(row=9, column=0, columnspan=2, padx=20, pady=(20,10))
    ctk.CTkButton(register_frame, text="Back to Login", fg_color="transparent", command=self.show_login).grid(row=10, column=0, columnspan=2, padx=20, pady=(10,20))