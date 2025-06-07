import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from PIL import Image, ImageTk

from .auth import authenticate, register_user
from .database import (
    get_patients,
    get_patient,
    add_patient,
    update_patient,
    delete_patient,
    get_soap_notes,
    get_soap_note,
    add_soap_note,
    update_soap_note,
    delete_soap_note,
    get_appointments,
    get_appointment,
    add_appointment,
    update_appointment,
    delete_appointment,
)
from .reports import generate_word_report


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class EiraNotesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Eira Notes - Physiotherapy Management System")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Global state
        self.current_user = None
        self.current_patient = None
        self.current_frame = None
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        
        # App logo/title
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Eira Notes", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Sidebar buttons - they will be created after login
        self.sidebar_buttons = []
        
        # Create main content frame
        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Show login form initially
        self.show_login()
    
    def clear_content(self):
        # Destroy all widgets in the content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Reset current frame
        self.current_frame = None
    
    def create_sidebar(self):
        # Clear existing sidebar buttons
        for button in self.sidebar_buttons:
            button.destroy()
        self.sidebar_buttons = []
        
        # Create navigation buttons
        self.home_button = ctk.CTkButton(self.sidebar_frame, text="Home", command=self.show_home)
        self.home_button.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_buttons.append(self.home_button)
        
        self.patients_button = ctk.CTkButton(self.sidebar_frame, text="Patients", command=self.show_patients)
        self.patients_button.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_buttons.append(self.patients_button)
        
        self.appointments_button = ctk.CTkButton(self.sidebar_frame, text="Appointments", command=self.show_appointments)
        self.appointments_button.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_buttons.append(self.appointments_button)
        
        # Spacer
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        # User info and logout
        user_name = f"{self.current_user['first_name']} {self.current_user['last_name']}"
        self.user_label = ctk.CTkLabel(self.sidebar_frame, text=user_name, font=ctk.CTkFont(size=12))
        self.user_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.sidebar_buttons.append(self.user_label)
        
        self.logout_button = ctk.CTkButton(self.sidebar_frame, text="Logout", fg_color="transparent", command=self.logout)
        self.logout_button.grid(row=6, column=0, padx=20, pady=10)
        self.sidebar_buttons.append(self.logout_button)
    
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
        
        # Create register frame
        register_frame = ctk.CTkFrame(self.content_frame)
        register_frame.grid(row=0, column=0, sticky="", padx=20, pady=20)
        self.current_frame = register_frame
        
        # Title
        title_label = ctk.CTkLabel(register_frame, text="Register New Account", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 30))
        
        # Username
        username_label = ctk.CTkLabel(register_frame, text="Username:")
        username_label.grid(row=1, column=0, sticky="e", padx=(20, 10), pady=10)
        username_entry = ctk.CTkEntry(register_frame, width=200)
        username_entry.grid(row=1, column=1, sticky="w", padx=(10, 20), pady=10)
        
        # Email
        email_label = ctk.CTkLabel(register_frame, text="Email:")
        email_label.grid(row=2, column=0, sticky="e", padx=(20, 10), pady=10)
        email_entry = ctk.CTkEntry(register_frame, width=200)
        email_entry.grid(row=2, column=1, sticky="w", padx=(10, 20), pady=10)
        
        # First name
        first_name_label = ctk.CTkLabel(register_frame, text="First Name:")
        first_name_label.grid(row=3, column=0, sticky="e", padx=(20, 10), pady=10)
        first_name_entry = ctk.CTkEntry(register_frame, width=200)
        first_name_entry.grid(row=3, column=1, sticky="w", padx=(10, 20), pady=10)
        
        # Last name
        last_name_label = ctk.CTkLabel(register_frame, text="Last Name:")
        last_name_label.grid(row=4, column=0, sticky="e", padx=(20, 10), pady=10)
        last_name_entry = ctk.CTkEntry(register_frame, width=200)
        last_name_entry.grid(row=4, column=1, sticky="w", padx=(10, 20), pady=10)
        
        # Password
        password_label = ctk.CTkLabel(register_frame, text="Password:")
        password_label.grid(row=5, column=0, sticky="e", padx=(20, 10), pady=10)
        password_entry = ctk.CTkEntry(register_frame, width=200, show="•")
        password_entry.grid(row=5, column=1, sticky="w", padx=(10, 20), pady=10)
        
        # Confirm password
        confirm_label = ctk.CTkLabel(register_frame, text="Confirm Password:")
        confirm_label.grid(row=6, column=0, sticky="e", padx=(20, 10), pady=10)
        confirm_entry = ctk.CTkEntry(register_frame, width=200, show="•")
        confirm_entry.grid(row=6, column=1, sticky="w", padx=(10, 20), pady=10)
        
        # Error message
        error_label = ctk.CTkLabel(register_frame, text="", text_color="red")
        error_label.grid(row=7, column=0, columnspan=2, padx=20, pady=(10, 0))
        
        # Register button
        def handle_register():
            username = username_entry.get()
            email = email_entry.get()
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            # Simple validation
            if not username or not email or not first_name or not last_name or not password or not confirm:
                error_label.configure(text="All fields are required")
                return
            
            if password != confirm:
                error_label.configure(text="Passwords do not match")
                return
            
            if len(password) < 8:
                error_label.configure(text="Password must be at least 8 characters")
                return
            
            # Register user
            result = register_user(username, email, password, first_name, last_name)
            if result["success"]:
                messagebox.showinfo("Registration Successful", "Your account has been created. You can now log in.")
                self.show_login()
            else:
                error_label.configure(text=result["message"])
        
        register_button = ctk.CTkButton(register_frame, text="Register", command=handle_register)
        register_button.grid(row=8, column=0, columnspan=2, padx=20, pady=(20, 10))
        
        # Back to login
        back_button = ctk.CTkButton(register_frame, text="Back to Login", fg_color="transparent", command=self.show_login)
        back_button.grid(row=9, column=0, columnspan=2, padx=20, pady=(10, 20))
    
    def logout(self):
        self.current_user = None
        
        # Clear sidebar
        for button in self.sidebar_buttons:
            button.destroy()
        self.sidebar_buttons = []
        
        # Show login screen
        self.show_login()
    
    def show_home(self):
        self.clear_content()
        
        # Create home frame
        home_frame = ctk.CTkFrame(self.content_frame)
        home_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        home_frame.grid_columnconfigure(0, weight=1)
        self.current_frame = home_frame
        
        # Welcome message
        welcome_label = ctk.CTkLabel(
            home_frame, 
            text=f"Welcome, {self.current_user['first_name']}!",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        welcome_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        subtitle_label = ctk.CTkLabel(
            home_frame,
            text="Eira Notes - Physiotherapy Practice Management",
            font=ctk.CTkFont(size=16)
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # Quick actions frame
        quick_actions_frame = ctk.CTkFrame(home_frame)
        quick_actions_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        quick_actions_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Add patient button
        add_patient_button = ctk.CTkButton(
            quick_actions_frame,
            text="Add New Patient",
            command=self.show_add_patient
        )
        add_patient_button.grid(row=0, column=0, padx=10, pady=10)
        
        # View patients button
        view_patients_button = ctk.CTkButton(
            quick_actions_frame,
            text="View All Patients",
            command=self.show_patients
        )
        view_patients_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Manage appointments button
        manage_appts_button = ctk.CTkButton(
            quick_actions_frame,
            text="Manage Appointments",
            command=self.show_appointments
        )
        manage_appts_button.grid(row=0, column=2, padx=10, pady=10)
        
        # Get today's appointments
        appointments = get_appointments(self.current_user["id"], filter_type="today")
        
        # Today's appointments section
        appts_label = ctk.CTkLabel(
            home_frame,
            text="Today's Appointments",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        appts_label.grid(row=3, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Appointments list
        appointments_frame = ctk.CTkFrame(home_frame)
        appointments_frame.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        appointments_frame.grid_columnconfigure(0, weight=1)
        
        if appointments:
            # Create headers
            headers_frame = ctk.CTkFrame(appointments_frame)
            headers_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            headers_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
            
            time_header = ctk.CTkLabel(headers_frame, text="Time", font=ctk.CTkFont(weight="bold"))
            time_header.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            
            patient_header = ctk.CTkLabel(headers_frame, text="Patient", font=ctk.CTkFont(weight="bold"))
            patient_header.grid(row=0, column=1, padx=5, pady=5, sticky="w")
            
            duration_header = ctk.CTkLabel(headers_frame, text="Duration", font=ctk.CTkFont(weight="bold"))
            duration_header.grid(row=0, column=2, padx=5, pady=5, sticky="w")
            
            status_header = ctk.CTkLabel(headers_frame, text="Status", font=ctk.CTkFont(weight="bold"))
            status_header.grid(row=0, column=3, padx=5, pady=5, sticky="w")
            
            # Add appointments
            for i, appointment in enumerate(appointments):
                appt_frame = ctk.CTkFrame(appointments_frame)
                appt_frame.grid(row=i+1, column=0, padx=5, pady=2, sticky="ew")
                appt_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
                
                time_str = datetime.datetime.strptime(appointment["time"], "%H:%M:%S").strftime("%I:%M %p")
                time_label = ctk.CTkLabel(appt_frame, text=time_str)
                time_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
                
                patient_label = ctk.CTkLabel(appt_frame, text=appointment["patient_name"])
                patient_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
                
                duration_label = ctk.CTkLabel(appt_frame, text=f"{appointment['duration']} min")
                duration_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
                
                status_label = ctk.CTkLabel(appt_frame, text=appointment["status"].capitalize())
                status_label.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        else:
            no_appt_label = ctk.CTkLabel(appointments_frame, text="No appointments scheduled for today")
            no_appt_label.grid(row=0, column=0, padx=20, pady=20)
    
    def show_patients(self):
        self.clear_content()
        
        # Create patients frame
        patients_frame = ctk.CTkFrame(self.content_frame)
        patients_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        patients_frame.grid_columnconfigure(0, weight=1)
        self.current_frame = patients_frame
        
        # Title and Add button
        header_frame = ctk.CTkFrame(patients_frame)
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Patients",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        add_button = ctk.CTkButton(
            header_frame,
            text="Add New Patient",
            command=self.show_add_patient
        )
        add_button.grid(row=0, column=1, padx=20, pady=10)
        
        # Get patients
        patients = get_patients(self.current_user["id"])
        
        # Patients list
        patients_list_frame = ctk.CTkFrame(patients_frame)
        patients_list_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        patients_list_frame.grid_columnconfigure(0, weight=1)
        
        # Create a scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(patients_list_frame, width=800, height=400)
        scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        if patients:
            # Create headers
            headers_frame = ctk.CTkFrame(scrollable_frame)
            headers_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            headers_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
            
            name_header = ctk.CTkLabel(headers_frame, text="Patient Name", font=ctk.CTkFont(weight="bold"))
            name_header.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            
            dob_header = ctk.CTkLabel(headers_frame, text="Date of Birth", font=ctk.CTkFont(weight="bold"))
            dob_header.grid(row=0, column=1, padx=5, pady=5, sticky="w")
            
            diagnosis_header = ctk.CTkLabel(headers_frame, text="Diagnosis", font=ctk.CTkFont(weight="bold"))
            diagnosis_header.grid(row=0, column=2, padx=5, pady=5, sticky="w")
            
            actions_header = ctk.CTkLabel(headers_frame, text="Actions", font=ctk.CTkFont(weight="bold"))
            actions_header.grid(row=0, column=3, padx=5, pady=5, sticky="w")
            
            # Add patients
            for i, patient in enumerate(patients):
                patient_frame = ctk.CTkFrame(scrollable_frame)
                patient_frame.grid(row=i+1, column=0, padx=5, pady=2, sticky="ew")
                patient_frame.grid_columnconfigure((0, 1, 2), weight=1)
                
                full_name = f"{patient['first_name']} {patient['last_name']}"
                name_label = ctk.CTkLabel(patient_frame, text=full_name)
                name_label.grid(row=0, column=0, padx=5, pady=10, sticky="w")
                
                dob = datetime.datetime.strptime(patient["date_of_birth"], "%Y-%m-%d").strftime("%d/%m/%Y")
                dob_label = ctk.CTkLabel(patient_frame, text=dob)
                dob_label.grid(row=0, column=1, padx=5, pady=10, sticky="w")
                
                diag_label = ctk.CTkLabel(patient_frame, text=patient["diagnosis"])
                diag_label.grid(row=0, column=2, padx=5, pady=10, sticky="w")
                
                # Actions frame
                actions_frame = ctk.CTkFrame(patient_frame)
                actions_frame.grid(row=0, column=3, padx=5, pady=5)
                
                view_button = ctk.CTkButton(
                    actions_frame, 
                    text="View",
                    width=70,
                    command=lambda p=patient: self.show_patient_details(p["id"])
                )
                view_button.grid(row=0, column=0, padx=5, pady=5)
                
                edit_button = ctk.CTkButton(
                    actions_frame, 
                    text="Edit",
                    width=70,
                    command=lambda p=patient: self.show_edit_patient(p["id"])
                )
                edit_button.grid(row=0, column=1, padx=5, pady=5)
        else:
            no_patients_label = ctk.CTkLabel(scrollable_frame, text="No patients found. Add your first patient to get started.")
            no_patients_label.grid(row=0, column=0, padx=20, pady=20)
    
    def show_add_patient(self):
        self.clear_content()
        
        # Create add patient frame
        add_patient_frame = ctk.CTkFrame(self.content_frame)
        add_patient_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        add_patient_frame.grid_columnconfigure(0, weight=1)
        self.current_frame = add_patient_frame
        
        # Title
        title_label = ctk.CTkLabel(
            add_patient_frame, 
            text="Add New Patient",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Form
        form_frame = ctk.CTkFrame(add_patient_frame)
        form_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        form_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Create a scrollable frame for the form
        scrollable_frame = ctk.CTkScrollableFrame(form_frame, width=800, height=400)
        scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        scrollable_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Personal Information Section
        personal_label = ctk.CTkLabel(
            scrollable_frame, 
            text="Personal Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        personal_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")
        
        # First Name
        first_name_label = ctk.CTkLabel(scrollable_frame, text="First Name:")
        first_name_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        first_name_entry = ctk.CTkEntry(scrollable_frame, width=250)
        first_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Last Name
        last_name_label = ctk.CTkLabel(scrollable_frame, text="Last Name:")
        last_name_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        last_name_entry = ctk.CTkEntry(scrollable_frame, width=250)
        last_name_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Date of Birth
        dob_label = ctk.CTkLabel(scrollable_frame, text="Date of Birth:")
        dob_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        
        dob_frame = ctk.CTkFrame(scrollable_frame)
        dob_frame.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        # Create dropdown for day, month, year
        day_var = tk.StringVar()
        day_dropdown = ctk.CTkOptionMenu(dob_frame, variable=day_var, values=[str(i).zfill(2) for i in range(1, 32)])
        day_dropdown.grid(row=0, column=0, padx=2)
        day_dropdown.set("01")
        
        month_var = tk.StringVar()
        month_dropdown = ctk.CTkOptionMenu(dob_frame, variable=month_var, values=[str(i).zfill(2) for i in range(1, 13)])
        month_dropdown.grid(row=0, column=1, padx=2)
        month_dropdown.set("01")
        
        current_year = datetime.datetime.now().year
        year_var = tk.StringVar()
        year_dropdown = ctk.CTkOptionMenu(dob_frame, variable=year_var, values=[str(i) for i in range(current_year-100, current_year+1)])
        year_dropdown.grid(row=0, column=2, padx=2)
        year_dropdown.set(str(current_year-30))  # Default to 30 years ago
        
        # Gender
        gender_label = ctk.CTkLabel(scrollable_frame, text="Gender:")
        gender_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        
        gender_var = tk.StringVar()
        gender_dropdown = ctk.CTkOptionMenu(scrollable_frame, variable=gender_var, values=["male", "female", "other"])
        gender_dropdown.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        gender_dropdown.set("Select Gender")
        
        # Contact Information Section
        contact_label = ctk.CTkLabel(
            scrollable_frame, 
            text="Contact Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        contact_label.grid(row=5, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="w")
        
        # Phone
        phone_label = ctk.CTkLabel(scrollable_frame, text="Phone Number:")
        phone_label.grid(row=6, column=0, padx=10, pady=5, sticky="e")
        phone_entry = ctk.CTkEntry(scrollable_frame, width=250)
        phone_entry.grid(row=6, column=1, padx=10, pady=5, sticky="w")
        
        # Email
        email_label = ctk.CTkLabel(scrollable_frame, text="Email:")
        email_label.grid(row=7, column=0, padx=10, pady=5, sticky="e")
        email_entry = ctk.CTkEntry(scrollable_frame, width=250)
        email_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")
        
        # Address
        address_label = ctk.CTkLabel(scrollable_frame, text="Address:")
        address_label.grid(row=8, column=0, padx=10, pady=5, sticky="e")
        address_entry = ctk.CTkEntry(scrollable_frame, width=250)
        address_entry.grid(row=8, column=1, padx=10, pady=5, sticky="w")
        
        # Medical Information Section
        medical_label = ctk.CTkLabel(
            scrollable_frame, 
            text="Medical Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        medical_label.grid(row=9, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="w")
        
        # Medical Aid
        med_aid_label = ctk.CTkLabel(scrollable_frame, text="Medical Aid Provider:")
        med_aid_label.grid(row=10, column=0, padx=10, pady=5, sticky="e")
        med_aid_entry = ctk.CTkEntry(scrollable_frame, width=250)
        med_aid_entry.grid(row=10, column=1, padx=10, pady=5, sticky="w")
        
        # Medical Aid Number
        med_num_label = ctk.CTkLabel(scrollable_frame, text="Medical Aid Number:")
        med_num_label.grid(row=11, column=0, padx=10, pady=5, sticky="e")
        med_num_entry = ctk.CTkEntry(scrollable_frame, width=250)
        med_num_entry.grid(row=11, column=1, padx=10, pady=5, sticky="w")
        
        # Medical History
        history_label = ctk.CTkLabel(scrollable_frame, text="Medical History:")
        history_label.grid(row=12, column=0, padx=10, pady=5, sticky="ne")
        history_entry = ctk.CTkTextbox(scrollable_frame, width=250, height=100)
        history_entry.grid(row=12, column=1, padx=10, pady=5, sticky="w")
        
        # Diagnosis
        diagnosis_label = ctk.CTkLabel(scrollable_frame, text="Diagnosis:")
        diagnosis_label.grid(row=13, column=0, padx=10, pady=5, sticky="e")
        diagnosis_entry = ctk.CTkEntry(scrollable_frame, width=250)
        diagnosis_entry.grid(row=13, column=1, padx=10, pady=5, sticky="w")
        
        # Error message
        error_label = ctk.CTkLabel(scrollable_frame, text="", text_color="red")
        error_label.grid(row=14, column=0, columnspan=2, padx=10, pady=(10, 0))
        
        # Save and Cancel buttons
        button_frame = ctk.CTkFrame(scrollable_frame)
        button_frame.grid(row=15, column=0, columnspan=2, padx=10, pady=20)
        
        def handle_save():
            # Get form data
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            date_of_birth = f"{year_var.get()}-{month_var.get()}-{day_var.get()}"
            gender = gender_var.get() if gender_var.get() != "Select Gender" else ""
            
            # Validate required fields
            if not first_name or not last_name or gender == "Select Gender":
                error_label.configure(text="First name, last name, and gender are required")
                return
            
            try:
                datetime.datetime.strptime(date_of_birth, "%Y-%m-%d")
            except ValueError:
                error_label.configure(text="Invalid date of birth")
                return
            
            if not diagnosis_entry.get():
                error_label.configure(text="Diagnosis is required")
                return
            
            # Collect all data
            patient_data = {
                "first_name": first_name,
                "last_name": last_name,
                "date_of_birth": date_of_birth,
                "gender": gender,
                "phone": phone_entry.get(),
                "email": email_entry.get(),
                "address": address_entry.get(),
                "medical_aid_name": med_aid_entry.get(),
                "medical_aid_number": med_num_entry.get(),
                "medical_history": history_entry.get("1.0", "end-1c"),
                "diagnosis": diagnosis_entry.get()
            }
            
            # Add patient
            result = add_patient(patient_data, self.current_user["id"])
            if result["success"]:
                messagebox.showinfo("Success", result["message"])
                self.show_patients()
            else:
                error_label.configure(text=result["message"])
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Save Patient",
            command=handle_save
        )
        save_button.grid(row=0, column=0, padx=10, pady=10)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color="transparent",
            command=self.show_patients
        )
        cancel_button.grid(row=0, column=1, padx=10, pady=10)
    
    def show_patient_details(self, patient_id):
        self.clear_content()
        
        # Get patient data
        patient = get_patient(patient_id)
        
        # Get patient age
        dob = datetime.datetime.strptime(patient['date_of_birth'], '%Y-%m-%d').date()
        today = datetime.date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        # Create patient details frame
        details_frame = ctk.CTkFrame(self.content_frame)
        details_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        details_frame.grid_columnconfigure(0, weight=1)
        self.current_frame = details_frame
        
        # Header with patient name and action buttons
        header_frame = ctk.CTkFrame(details_frame)
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        name = f"{patient['first_name']} {patient['last_name']}"
        title_label = ctk.CTkLabel(
            header_frame, 
            text=name,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Buttons for actions
        buttons_frame = ctk.CTkFrame(header_frame)
        buttons_frame.grid(row=0, column=1, padx=20, pady=10)
        
        edit_button = ctk.CTkButton(
            buttons_frame,
            text="Edit Patient",
            command=lambda: self.show_edit_patient(patient_id)
        )
        edit_button.grid(row=0, column=0, padx=5, pady=5)
        
        delete_button = ctk.CTkButton(
            buttons_frame,
            text="Delete Patient",
            fg_color="red",
            hover_color="#990000",
            command=lambda: self.delete_patient_confirm(patient_id)
        )
        delete_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Create tabview for different sections
        tabview = ctk.CTkTabview(details_frame)
        tabview.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        # Add tabs
        info_tab = tabview.add("Patient Info")
        notes_tab = tabview.add("SOAP Notes")
        appointments_tab = tabview.add("Appointments")
        
        # Configure tab grids
        info_tab.grid_columnconfigure(0, weight=1)
        notes_tab.grid_columnconfigure(0, weight=1)
        appointments_tab.grid_columnconfigure(0, weight=1)
        
        # Patient Info Tab
        info_frame = ctk.CTkFrame(info_tab)
        info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        info_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Personal info section
        personal_label = ctk.CTkLabel(
            info_frame, 
            text="Personal Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        personal_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")
        
        # Create two columns for info
        left_info = ctk.CTkFrame(info_frame)
        left_info.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        right_info = ctk.CTkFrame(info_frame)
        right_info.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        
        # Left column info
        dob_str = datetime.datetime.strptime(patient['date_of_birth'], '%Y-%m-%d').strftime('%d %B %Y')
        
        ctk.CTkLabel(left_info, text="Age:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(left_info, text=str(age)).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(left_info, text="Date of Birth:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(left_info, text=dob_str).grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(left_info, text="Gender:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(left_info, text=patient['gender'].capitalize() if patient['gender'] else "Not specified").grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Contact info
        ctk.CTkLabel(right_info, text="Phone:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(right_info, text=patient['phone'] or "Not provided").grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(right_info, text="Email:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(right_info, text=patient['email'] or "Not provided").grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(right_info, text="Address:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(right_info, text=patient['address'] or "Not provided").grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Medical info section
        medical_label = ctk.CTkLabel(
            info_frame, 
            text="Medical Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        medical_label.grid(row=2, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="w")
        
        med_info = ctk.CTkFrame(info_frame)
        med_info.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        
        ctk.CTkLabel(med_info, text="Medical Aid:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(med_info, text=patient['medical_aid_name'] or "Not provided").grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(med_info, text="Medical Aid Number:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(med_info, text=patient['medical_aid_number'] or "Not provided").grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(med_info, text="Diagnosis:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(med_info, text=patient['diagnosis']).grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Medical history
        history_label = ctk.CTkLabel(
            info_frame, 
            text="Medical History",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        history_label.grid(row=4, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="w")
        
        history_text = ctk.CTkTextbox(info_frame, height=100, wrap="word")
        history_text.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        history_text.insert("1.0", patient['medical_history'] or "No medical history recorded.")
        history_text.configure(state="disabled")  # Make read-only
        
        # Generate Report button
        report_button = ctk.CTkButton(
            info_frame,
            text="Generate Progress Report",
            command=lambda: generate_word_report(patient_id, self.current_user["id"])
        )
        report_button.grid(row=6, column=0, columnspan=2, padx=10, pady=20)
        
        # SOAP Notes Tab
        notes_container = ctk.CTkFrame(notes_tab)
        notes_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        notes_container.grid_columnconfigure(0, weight=1)
        
        # Header with add button
        notes_header = ctk.CTkFrame(notes_container)
        notes_header.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        notes_header.grid_columnconfigure(0, weight=1)
        
        notes_title = ctk.CTkLabel(
            notes_header, 
            text="SOAP Notes",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        notes_title.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        add_note_button = ctk.CTkButton(
            notes_header,
            text="Add New SOAP Note",
            command=lambda: self.show_add_soap_note(patient_id)
        )
        add_note_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Get soap notes
        soap_notes = get_soap_notes(patient_id)
        
        # Notes list in scrollable frame
        notes_scrollable = ctk.CTkScrollableFrame(notes_container, height=300)
        notes_scrollable.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        notes_scrollable.grid_columnconfigure(0, weight=1)
        
        if soap_notes:
            for i, note in enumerate(soap_notes):
                note_frame = ctk.CTkFrame(notes_scrollable)
                note_frame.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
                note_frame.grid_columnconfigure(1, weight=1)
                
                date_str = datetime.datetime.strptime(note['date'], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y')
                
                date_label = ctk.CTkLabel(note_frame, text=date_str, font=ctk.CTkFont(weight="bold"))
                date_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
                
                # Add a brief excerpt of the subjective field
                excerpt = note['subjective'][:50] + "..." if len(note['subjective']) > 50 else note['subjective']
                excerpt_label = ctk.CTkLabel(note_frame, text=excerpt)
                excerpt_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
                
                view_button = ctk.CTkButton(
                    note_frame,
                    text="View",
                    width=70,
                    command=lambda n=note: self.show_soap_note_details(n['id'], patient_id)
                )
                view_button.grid(row=0, column=2, padx=10, pady=10)
        else:
            no_notes_label = ctk.CTkLabel(notes_scrollable, text="No SOAP notes recorded for this patient.")
            no_notes_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Appointments Tab
        appts_container = ctk.CTkFrame(appointments_tab)
        appts_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        appts_container.grid_columnconfigure(0, weight=1)
        
        # Header with add button
        appts_header = ctk.CTkFrame(appts_container)
        appts_header.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        appts_header.grid_columnconfigure(0, weight=1)
        
        appts_title = ctk.CTkLabel(
            appts_header, 
            text="Appointments",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        appts_title.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        add_appt_button = ctk.CTkButton(
            appts_header,
            text="Schedule New Appointment",
            command=lambda: self.show_add_appointment(patient_id)
        )
        add_appt_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Get appointments for this patient
        cursor.execute(
            """SELECT * FROM appointments 
            WHERE patient_id = ? 
            ORDER BY date DESC, time DESC""",
            (patient_id,)
        )
        appointments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Appointments list in scrollable frame
        appts_scrollable = ctk.CTkScrollableFrame(appts_container, height=300)
        appts_scrollable.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        appts_scrollable.grid_columnconfigure(0, weight=1)
        
        if appointments:
            # Table headers
            headers_frame = ctk.CTkFrame(appts_scrollable)
            headers_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            headers_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
            
            date_header = ctk.CTkLabel(headers_frame, text="Date", font=ctk.CTkFont(weight="bold"))
            date_header.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            
            time_header = ctk.CTkLabel(headers_frame, text="Time", font=ctk.CTkFont(weight="bold"))
            time_header.grid(row=0, column=1, padx=5, pady=5, sticky="w")
            
            duration_header = ctk.CTkLabel(headers_frame, text="Duration", font=ctk.CTkFont(weight="bold"))
            duration_header.grid(row=0, column=2, padx=5, pady=5, sticky="w")
            
            status_header = ctk.CTkLabel(headers_frame, text="Status", font=ctk.CTkFont(weight="bold"))
            status_header.grid(row=0, column=3, padx=5, pady=5, sticky="w")
            
            actions_header = ctk.CTkLabel(headers_frame, text="Actions", font=ctk.CTkFont(weight="bold"))
            actions_header.grid(row=0, column=4, padx=5, pady=5, sticky="w")
            
            # List appointments
            for i, appt in enumerate(appointments):
                appt_frame = ctk.CTkFrame(appts_scrollable)
                appt_frame.grid(row=i+1, column=0, padx=5, pady=2, sticky="ew")
                appt_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
                
                date_str = datetime.datetime.strptime(appt['date'], '%Y-%m-%d').strftime('%d/%m/%Y')
                date_label = ctk.CTkLabel(appt_frame, text=date_str)
                date_label.grid(row=0, column=0, padx=5, pady=10, sticky="w")
                
                time_str = datetime.datetime.strptime(appt['time'], '%H:%M:%S').strftime('%I:%M %p')
                time_label = ctk.CTkLabel(appt_frame, text=time_str)
                time_label.grid(row=0, column=1, padx=5, pady=10, sticky="w")
                
                duration_label = ctk.CTkLabel(appt_frame, text=f"{appt['duration']} min")
                duration_label.grid(row=0, column=2, padx=5, pady=10, sticky="w")
                
                status_label = ctk.CTkLabel(appt_frame, text=appt['status'].capitalize())
                status_label.grid(row=0, column=3, padx=5, pady=10, sticky="w")
                
                # Action buttons
                action_frame = ctk.CTkFrame(appt_frame)
                action_frame.grid(row=0, column=4, padx=5, pady=5)
                
                edit_appt_button = ctk.CTkButton(
                    action_frame,
                    text="Edit",
                    width=70,
                    command=lambda a=appt: self.show_edit_appointment(a['id'], patient_id)
                )
                edit_appt_button.grid(row=0, column=0, padx=5, pady=5)
                
                delete_appt_button = ctk.CTkButton(
                    action_frame,
                    text="Cancel",
                    width=70,
                    fg_color="red",
                    hover_color="#990000",
                    command=lambda a=appt: self.delete_appointment_confirm(a['id'], patient_id)
                )
                delete_appt_button.grid(row=0, column=1, padx=5, pady=5)
        else:
            no_appts_label = ctk.CTkLabel(appts_scrollable, text="No appointments scheduled for this patient.")
            no_appts_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Back button at the bottom
        back_button = ctk.CTkButton(
            details_frame,
            text="Back to Patients",
            command=self.show_patients
        )
        back_button.grid(row=2, column=0, padx=20, pady=20)
    
    def delete_patient_confirm(self, patient_id):
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patient? This will also delete all associated SOAP notes and appointments.\n\nThis action cannot be undone."):
            result = delete_patient(patient_id)
            if result["success"]:
                messagebox.showinfo("Success", result["message"])
                self.show_patients()
            else:
                messagebox.showerror("Error", result["message"])
    
    def show_add_soap_note(self, patient_id):
        self.clear_content()
        
        # Get patient info
        patient = get_patient(patient_id)
        
        # Create soap note frame
        soap_frame = ctk.CTkFrame(self.content_frame)
        soap_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        soap_frame.grid_columnconfigure(0, weight=1)
        self.current_frame = soap_frame
        
        # Header
        title_label = ctk.CTkLabel(
            soap_frame, 
            text=f"New SOAP Note for {patient['first_name']} {patient['last_name']}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Form in scrollable frame
        form_frame = ctk.CTkScrollableFrame(soap_frame, height=500)
        form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        form_frame.grid_columnconfigure(0, weight=1)
        
        # Date field
        date_frame = ctk.CTkFrame(form_frame)
        date_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        date_frame.grid_columnconfigure(1, weight=1)
        
        date_label = ctk.CTkLabel(date_frame, text="Date:")
        date_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        date_picker_frame = ctk.CTkFrame(date_frame)
        date_picker_frame.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        today = datetime.datetime.now()
        
        # Create dropdown for day, month, year
        day_var = tk.StringVar(value=today.strftime("%d"))
        day_dropdown = ctk.CTkOptionMenu(date_picker_frame, variable=day_var, values=[str(i).zfill(2) for i in range(1, 32)])
        day_dropdown.grid(row=0, column=0, padx=2)
        
        month_var = tk.StringVar(value=today.strftime("%m"))
        month_dropdown = ctk.CTkOptionMenu(date_picker_frame, variable=month_var, values=[str(i).zfill(2) for i in range(1, 13)])
        month_dropdown.grid(row=0, column=1, padx=2)
        
        year_var = tk.StringVar(value=today.strftime("%Y"))
        year_dropdown = ctk.CTkOptionMenu(date_picker_frame, variable=year_var, values=[str(i) for i in range(today.year-5, today.year+1)])
        year_dropdown.grid(row=0, column=2, padx=2)
        
        # SOAP components
        soap_components = [
            {"label": "Subjective (Patient Report)", "field": "subjective", "placeholder": "Patient's self-reported symptoms, concerns, progress, etc."},
            {"label": "Objective (Measurements & Observations)", "field": "objective", "placeholder": "Clinical observations, measurements, test results, etc."},
            {"label": "Action (Treatment/Management)", "field": "action", "placeholder": "Treatment provided, management performed, therapeutic interventions, etc."},
            {"label": "Plan (Treatment Plan)", "field": "plan", "placeholder": "Treatment plan, goals, recommended exercises, follow-up schedule, etc."}
        ]
        
        soap_textboxes = {}
        
        for i, component in enumerate(soap_components):
            component_frame = ctk.CTkFrame(form_frame)
            component_frame.grid(row=i+1, column=0, padx=10, pady=10, sticky="ew")
            component_frame.grid_columnconfigure(0, weight=1)
            
            label = ctk.CTkLabel(component_frame, text=component["label"], font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            textbox = ctk.CTkTextbox(component_frame, height=100, width=600)
            textbox.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
            textbox.insert("1.0", component["placeholder"])
            textbox.bind("<FocusIn>", lambda e, tb=textbox, ph=component["placeholder"]: self.clear_placeholder(tb, ph))
            textbox.bind("<FocusOut>", lambda e, tb=textbox, ph=component["placeholder"]: self.restore_placeholder(tb, ph))
            
            soap_textboxes[component["field"]] = textbox
        
        # Additional fields
        additional_components = [
            {"label": "Treatment Provided", "field": "treatment_provided", "placeholder": "Specific treatments delivered during this session"},
            {"label": "Patient Response", "field": "patient_response", "placeholder": "How the patient responded to treatment"},
            {"label": "Goals & Progress", "field": "goals_progress", "placeholder": "Progress toward established goals, new goals set"}
        ]
        
        additional_textboxes = {}
        
        for i, component in enumerate(additional_components):
            component_frame = ctk.CTkFrame(form_frame)
            component_frame.grid(row=i+len(soap_components)+1, column=0, padx=10, pady=10, sticky="ew")
            component_frame.grid_columnconfigure(0, weight=1)
            
            label = ctk.CTkLabel(component_frame, text=component["label"], font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            textbox = ctk.CTkTextbox(component_frame, height=80, width=600)
            textbox.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
            textbox.insert("1.0", component["placeholder"])
            textbox.bind("<FocusIn>", lambda e, tb=textbox, ph=component["placeholder"]: self.clear_placeholder(tb, ph))
            textbox.bind("<FocusOut>", lambda e, tb=textbox, ph=component["placeholder"]: self.restore_placeholder(tb, ph))
            
            additional_textboxes[component["field"]] = textbox
        
        # Error message
        error_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        error_label.grid(row=len(soap_components)+len(additional_components)+1, column=0, padx=10, pady=(10, 0))
        
        # Save and Cancel buttons
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.grid(row=len(soap_components)+len(additional_components)+2, column=0, padx=10, pady=20)
        
        def handle_save():
            # Validate required fields
            for field, textbox in soap_textboxes.items():
                text = textbox.get("1.0", "end-1c")
                if text == "" or text == soap_components[next(i for i, c in enumerate(soap_components) if c["field"] == field)]["placeholder"]:
                    error_label.configure(text=f"Please complete the {field.capitalize()} field")
                    return
            
            # Get form data
            date_str = f"{year_var.get()}-{month_var.get()}-{day_var.get()}"
            
            soap_data = {
                "date": date_str,
                "subjective": soap_textboxes["subjective"].get("1.0", "end-1c"),
                "objective": soap_textboxes["objective"].get("1.0", "end-1c"),
                "action": soap_textboxes["action"].get("1.0", "end-1c"),
                "plan": soap_textboxes["plan"].get("1.0", "end-1c")
            }
            
            # Add additional fields if they're not placeholders
            for field, textbox in additional_textboxes.items():
                text = textbox.get("1.0", "end-1c")
                placeholder = next(c["placeholder"] for c in additional_components if c["field"] == field)
                if text != placeholder:
                    soap_data[field] = text
            
            # Add SOAP note
            result = add_soap_note(soap_data, patient_id, self.current_user["id"])
            if result["success"]:
                messagebox.showinfo("Success", result["message"])
                self.show_patient_details(patient_id)
            else:
                error_label.configure(text=result["message"])
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Save SOAP Note",
            command=handle_save
        )
        save_button.grid(row=0, column=0, padx=10, pady=10)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color="transparent",
            command=lambda: self.show_patient_details(patient_id)
        )
        cancel_button.grid(row=0, column=1, padx=10, pady=10)
    
    def clear_placeholder(self, textbox, placeholder):
        if textbox.get("1.0", "end-1c") == placeholder:
            textbox.delete("1.0", "end")
    
    def restore_placeholder(self, textbox, placeholder):
        if textbox.get("1.0", "end-1c").strip() == "":
            textbox.delete("1.0", "end")
            textbox.insert("1.0", placeholder)
    
    def show_soap_note_details(self, note_id, patient_id):
        self.clear_content()
        
        # Get note data
        note = get_soap_note(note_id)
        patient = get_patient(patient_id)
        
        # Create note details frame
        note_frame = ctk.CTkFrame(self.content_frame)
        note_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        note_frame.grid_columnconfigure(0, weight=1)
        self.current_frame = note_frame
        
        # Header with date and action buttons
        header_frame = ctk.CTkFrame(note_frame)
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        date_str = datetime.datetime.strptime(note['date'], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y')
        title_label = ctk.CTkLabel(
            header_frame, 
            text=f"SOAP Note: {date_str}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text=f"Patient: {patient['first_name']} {patient['last_name']}",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Buttons for actions
        buttons_frame = ctk.CTkFrame(header_frame)
        buttons_frame.grid(row=0, column=1, rowspan=2, padx=20, pady=10)
        
        edit_button = ctk.CTkButton(
            buttons_frame,
            text="Edit Note",
            command=lambda: self.show_edit_soap_note(note_id, patient_id)
        )
        edit_button.grid(row=0, column=0, padx=5, pady=5)
        
        delete_button = ctk.CTkButton(
            buttons_frame,
            text="Delete Note",
            fg_color="red",
            hover_color="#990000",
            command=lambda: self.delete_soap_note_confirm(note_id, patient_id)
        )
        delete_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Create scrollable frame for note content
        note_content = ctk.CTkScrollableFrame(note_frame, height=400)
        note_content.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        note_content.grid_columnconfigure(0, weight=1)
        
        # SOAP Components
        soap_components = [
            {"label": "Subjective", "field": "subjective", "color": "#3B8ED0"},  # Blue
            {"label": "Objective", "field": "objective", "color": "#1F6AA5"},     # Darker blue
            {"label": "Action", "field": "action", "color": "#2FA572"},          # Green
            {"label": "Plan", "field": "plan", "color": "#F0B86E"}               # Yellow/orange
        ]
        
        # Display SOAP components in a 2x2 grid
        grid_frame = ctk.CTkFrame(note_content)
        grid_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        grid_frame.grid_columnconfigure((0, 1), weight=1)
        
        for i, component in enumerate(soap_components):
            row, col = divmod(i, 2)
            
            component_frame = ctk.CTkFrame(grid_frame)
            component_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            component_frame.grid_columnconfigure(0, weight=1)
            component_frame.grid_rowconfigure(1, weight=1)
            
            header = ctk.CTkFrame(component_frame, fg_color=component["color"])
            header.grid(row=0, column=0, sticky="ew")
            
            label = ctk.CTkLabel(header, text=component["label"], font=ctk.CTkFont(weight="bold"), text_color="white")
            label.grid(row=0, column=0, padx=10, pady=5)
            
            text_box = ctk.CTkTextbox(component_frame, height=150, wrap="word", state="normal")
            text_box.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
            text_box.insert("1.0", note[component["field"]])
            text_box.configure(state="disabled")  # Make read-only
        
        # Additional fields if they exist
        additional_fields = [
            {"label": "Treatment Provided", "field": "treatment_provided"},
            {"label": "Patient Response", "field": "patient_response"},
            {"label": "Goals & Progress", "field": "goals_progress"}
        ]
        
        # Check if any additional fields have content
        has_additional = any(note.get(field["field"]) for field in additional_fields)
        
        if has_additional:
            additional_label = ctk.CTkLabel(
                note_content, 
                text="Additional Information",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            additional_label.grid(row=1, column=0, padx=10, pady=(20, 10), sticky="w")
            
            additional_frame = ctk.CTkFrame(note_content)
            additional_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
            additional_frame.grid_columnconfigure(0, weight=1)
            
            row = 0
            for field in additional_fields:
                if note.get(field["field"]):
                    field_frame = ctk.CTkFrame(additional_frame)
                    field_frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
                    field_frame.grid_columnconfigure(0, weight=1)
                    
                    field_label = ctk.CTkLabel(field_frame, text=field["label"], font=ctk.CTkFont(weight="bold"))
                    field_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
                    
                    field_text = ctk.CTkTextbox(field_frame, height=80, wrap="word", state="normal")
                    field_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
                    field_text.insert("1.0", note[field["field"]])
                    field_text.configure(state="disabled")  # Make read-only
                    
                    row += 1
        
        # Back button
        back_button = ctk.CTkButton(
            note_frame,
            text="Back to Patient",
            command=lambda: self.show_patient_details(patient_id)
        )
        back_button.grid(row=2, column=0, padx=20, pady=20)
    
    def delete_soap_note_confirm(self, note_id, patient_id):
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this SOAP note?\n\nThis action cannot be undone."):
            result = delete_soap_note(note_id)
            if result["success"]:
                messagebox.showinfo("Success", result["message"])
                self.show_patient_details(patient_id)
            else:
                messagebox.showerror("Error", result["message"])
    
    def show_add_appointment(self, patient_id):
        self.clear_content()
        
        # Get patient info
        patient = get_patient(patient_id)
        
        # Create appointment frame
        appt_frame = ctk.CTkFrame(self.content_frame)
        appt_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        appt_frame.grid_columnconfigure(0, weight=1)
        self.current_frame = appt_frame
        
        # Header
        title_label = ctk.CTkLabel(
            appt_frame, 
            text=f"Schedule Appointment for {patient['first_name']} {patient['last_name']}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Form
        form_frame = ctk.CTkFrame(appt_frame)
        form_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        form_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Date
        date_label = ctk.CTkLabel(form_frame, text="Date:")
        date_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        date_picker_frame = ctk.CTkFrame(form_frame)
        date_picker_frame.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        today = datetime.datetime.now()
        
        # Create dropdown for day, month, year
        day_var = tk.StringVar(value=today.strftime("%d"))
        day_dropdown = ctk.CTkOptionMenu(date_picker_frame, variable=day_var, values=[str(i).zfill(2) for i in range(1, 32)])
        day_dropdown.grid(row=0, column=0, padx=2)
        
        month_var = tk.StringVar(value=today.strftime("%m"))
        month_dropdown = ctk.CTkOptionMenu(date_picker_frame, variable=month_var, values=[str(i).zfill(2) for i in range(1, 13)])
        month_dropdown.grid(row=0, column=1, padx=2)
        
        year_var = tk.StringVar(value=today.strftime("%Y"))
        year_dropdown = ctk.CTkOptionMenu(date_picker_frame, variable=year_var, values=[str(i) for i in range(today.year, today.year+3)])
        year_dropdown.grid(row=0, column=2, padx=2)
        
        # Time
        time_label = ctk.CTkLabel(form_frame, text="Time:")
        time_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        
        time_picker_frame = ctk.CTkFrame(form_frame)
        time_picker_frame.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Create dropdown for hour and minute
        hour_var = tk.StringVar(value="09")
        hour_dropdown = ctk.CTkOptionMenu(time_picker_frame, variable=hour_var, values=[str(i).zfill(2) for i in range(0, 24)])
        hour_dropdown.grid(row=0, column=0, padx=2)
        
        minute_var = tk.StringVar(value="00")
        minute_dropdown = ctk.CTkOptionMenu(time_picker_frame, variable=minute_var, values=["00", "15", "30", "45"])
        minute_dropdown.grid(row=0, column=1, padx=2)
        
        # Duration
        duration_label = ctk.CTkLabel(form_frame, text="Duration (minutes):")
        duration_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        
        duration_var = tk.StringVar(value="60")
        duration_dropdown = ctk.CTkOptionMenu(form_frame, variable=duration_var, values=["15", "30", "45", "60", "90", "120"])
        duration_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # Status
        status_label = ctk.CTkLabel(form_frame, text="Status:")
        status_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")
        
        status_var = tk.StringVar(value="scheduled")
        status_dropdown = ctk.CTkOptionMenu(form_frame, variable=status_var, values=["scheduled", "completed", "cancelled"])
        status_dropdown.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        # Notes
        notes_label = ctk.CTkLabel(form_frame, text="Notes:")
        notes_label.grid(row=4, column=0, padx=10, pady=10, sticky="ne")
        
        notes_textbox = ctk.CTkTextbox(form_frame, height=100, width=300)
        notes_textbox.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        
        # Error message
        error_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        error_label.grid(row=5, column=0, columnspan=2, padx=10, pady=(10, 0))
        
        # Buttons
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=20)
        
        def handle_save():
            try:
                # Validate date
                date_str = f"{year_var.get()}-{month_var.get()}-{day_var.get()}"
                datetime.datetime.strptime(date_str, "%Y-%m-%d")
                
                # Create time string
                time_str = f"{hour_var.get()}:{minute_var.get()}:00"
                
                # Validate duration
                duration = int(duration_var.get())
                
                # Create appointment data
                appt_data = {
                    "date": date_str,
                    "time": time_str,
                    "duration": duration,
                    "status": status_var.get(),
                    "notes": notes_textbox.get("1.0", "end-1c") if notes_textbox.get("1.0", "end-1c").strip() else None
                }
                
                # Add appointment
                result = add_appointment(appt_data, patient_id, self.current_user["id"])
                if result["success"]:
                    messagebox.showinfo("Success", result["message"])
                    self.show_patient_details(patient_id)
                else:
                    error_label.configure(text=result["message"])
            except ValueError:
                error_label.configure(text="Invalid date format")
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Save Appointment",
            command=handle_save
        )
        save_button.grid(row=0, column=0, padx=10, pady=10)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color="transparent",
            command=lambda: self.show_patient_details(patient_id)
        )
        cancel_button.grid(row=0, column=1, padx=10, pady=10)
    
    def delete_appointment_confirm(self, appointment_id, patient_id):
        # Confirm deletion
        if messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel this appointment?\n\nThis action cannot be undone."):
            result = delete_appointment(appointment_id)
            if result["success"]:
                messagebox.showinfo("Success", result["message"])
                self.show_patient_details(patient_id)
            else:
                messagebox.showerror("Error", result["message"])
    
    def show_appointments(self):
        self.clear_content()
        
        # Create appointments frame
        appointments_frame = ctk.CTkFrame(self.content_frame)
        appointments_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        appointments_frame.grid_columnconfigure(0, weight=1)
        self.current_frame = appointments_frame
        
        # Title 
        title_label = ctk.CTkLabel(
            appointments_frame, 
            text="Appointments",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Filter options
        filter_frame = ctk.CTkFrame(appointments_frame)
        filter_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        filter_label = ctk.CTkLabel(filter_frame, text="Filter:")
        filter_label.grid(row=0, column=0, padx=10, pady=10)
        
        # Create filter buttons that act like tabs
        filter_options = [
            {"value": None, "text": "All Appointments"},
            {"value": "today", "text": "Today"},
            {"value": "upcoming", "text": "Upcoming"}
        ]
        
        filter_buttons = []
        current_filter = [None]  # Use a list to create a mutable reference
        
        for i, option in enumerate(filter_options):
            button = ctk.CTkButton(
                filter_frame,
                text=option["text"],
                fg_color="transparent" if option["value"] != current_filter[0] else None,
                command=lambda val=option["value"], btn_idx=i: self.filter_appointments(val, btn_idx, filter_buttons, current_filter)
            )
            button.grid(row=0, column=i+1, padx=10, pady=10)
            filter_buttons.append(button)
        
        # Appointments container
        self.appointments_container = ctk.CTkFrame(appointments_frame)
        self.appointments_container.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.appointments_container.grid_columnconfigure(0, weight=1)
        
        # Load initial appointments (all)
        self.load_appointments(None)
    
    def filter_appointments(self, filter_value, button_idx, filter_buttons, current_filter):
        # Update button styles
        for i, button in enumerate(filter_buttons):
            if i == button_idx:
                button.configure(fg_color=("gray75", "gray25"))  # Selected
            else:
                button.configure(fg_color="transparent")  # Unselected
        
        # Update current filter
        current_filter[0] = filter_value
        
        # Load appointments with the selected filter
        self.load_appointments(filter_value)
    
    def load_appointments(self, filter_value):
        # Clear existing appointments
        for widget in self.appointments_container.winfo_children():
            widget.destroy()
        
        # Get appointments based on filter
        appointments = get_appointments(self.current_user["id"], filter_type=filter_value)
        
        if appointments:
            # Create a scrollable frame for the appointments
            scrollable_frame = ctk.CTkScrollableFrame(self.appointments_container, height=400)
            scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            scrollable_frame.grid_columnconfigure(0, weight=1)
            
            # Table headers
            headers_frame = ctk.CTkFrame(scrollable_frame)
            headers_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            headers_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
            
            date_header = ctk.CTkLabel(headers_frame, text="Date", font=ctk.CTkFont(weight="bold"))
            date_header.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            
            time_header = ctk.CTkLabel(headers_frame, text="Time", font=ctk.CTkFont(weight="bold"))
            time_header.grid(row=0, column=1, padx=5, pady=5, sticky="w")
            
            patient_header = ctk.CTkLabel(headers_frame, text="Patient", font=ctk.CTkFont(weight="bold"))
            patient_header.grid(row=0, column=2, padx=5, pady=5, sticky="w")
            
            duration_header = ctk.CTkLabel(headers_frame, text="Duration", font=ctk.CTkFont(weight="bold"))
            duration_header.grid(row=0, column=3, padx=5, pady=5, sticky="w")
            
            status_header = ctk.CTkLabel(headers_frame, text="Status", font=ctk.CTkFont(weight="bold"))
            status_header.grid(row=0, column=4, padx=5, pady=5, sticky="w")
            
            # List appointments
            for i, appt in enumerate(appointments):
                appt_frame = ctk.CTkFrame(scrollable_frame)
                appt_frame.grid(row=i+1, column=0, padx=5, pady=2, sticky="ew")
                appt_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
                
                date_str = datetime.datetime.strptime(appt['date'], '%Y-%m-%d').strftime('%d/%m/%Y')
                date_label = ctk.CTkLabel(appt_frame, text=date_str)
                date_label.grid(row=0, column=0, padx=5, pady=10, sticky="w")
                
                time_str = datetime.datetime.strptime(appt['time'], '%H:%M:%S').strftime('%I:%M %p')
                time_label = ctk.CTkLabel(appt_frame, text=time_str)
                time_label.grid(row=0, column=1, padx=5, pady=10, sticky="w")
                
                patient_label = ctk.CTkLabel(appt_frame, text=appt['patient_name'])
                patient_label.grid(row=0, column=2, padx=5, pady=10, sticky="w")
                
                duration_label = ctk.CTkLabel(appt_frame, text=f"{appt['duration']} min")
                duration_label.grid(row=0, column=3, padx=5, pady=10, sticky="w")
                
                status_label = ctk.CTkLabel(appt_frame, text=appt['status'].capitalize())
                status_label.grid(row=0, column=4, padx=5, pady=10, sticky="w")
                
                # View button
                view_button = ctk.CTkButton(
                    appt_frame,
                    text="View Patient",
                    width=100,
                    command=lambda p_id=appt['patient_id']: self.show_patient_details(p_id)
                )
                view_button.grid(row=0, column=5, padx=10, pady=10)
        else:
            no_appts_label = ctk.CTkLabel(
                self.appointments_container, 
                text="No appointments found with the selected filter."
            )
            no_appts_label.grid(row=0, column=0, padx=20, pady=20)

# Main function
