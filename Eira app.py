#!/usr/bin/env python
# coding: utf-8

import os
import sys
import customtkinter as ctk
from Eira_components import auth, patients, soap_notes, appointments, reports, database

# Set appearance mode and default color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Initialize the database
database.init_db()

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
        ctk.CTkButton(
            quick_actions_frame,
            text="Add New Patient",
            command=self.show_add_patient
        ).grid(row=0, column=0, padx=10, pady=10)

        # View patients button
        ctk.CTkButton(
            quick_actions_frame,
            text="View All Patients",
            command=self.show_patients
        ).grid(row=0, column=1, padx=10, pady=10)

        # Manage appointments button
        ctk.CTkButton(
            quick_actions_frame,
            text="Manage Appointments",
            command=self.show_appointments
        ).grid(row=0, column=2, padx=10, pady=10)

        # Fetch today's appointments
        today_appts = appointments.get_appointments(self.current_user['id'], filter_type='today')

        # Today's appointments section
        appts_label = ctk.CTkLabel(
            home_frame,
            text="Today's Appointments",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        appts_label.grid(row=3, column=0, padx=20, pady=(20, 10), sticky="w")

        appointments_frame = ctk.CTkFrame(home_frame)
        appointments_frame.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        appointments_frame.grid_columnconfigure(0, weight=1)

        if today_appts:
            # Headers
            hdr = ctk.CTkFrame(appts_frame)
            hdr.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            hdr.grid_columnconfigure((0,1,2,3), weight=1)
            for idx, txt in enumerate(["Time","Patient","Duration","Status"]):
                ctk.CTkLabel(hdr, text=txt, font=ctk.CTkFont(weight="bold")).grid(row=0, column=idx, padx=5, pady=5, sticky="w")

            # Appointment rows
            for i, appt in enumerate(today_appts, start=1):
                row_frame = ctk.CTkFrame(appts_frame)
                row_frame.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
                row_frame.grid_columnconfigure((0,1,2,3), weight=1)

                time_str = datetime.datetime.strptime(appt['time'], "%H:%M:%S").strftime("%I:%M %p")
                ctk.CTkLabel(row_frame, text=time_str).grid(row=0, column=0, padx=5, pady=5, sticky="w")
                ctk.CTkLabel(row_frame, text=appt['patient_name']).grid(row=0, column=1, padx=5, pady=5, sticky="w")
                ctk.CTkLabel(row_frame, text=f"{appt['duration']} min").grid(row=0, column=2, padx=5, pady=5, sticky="w")
                ctk.CTkLabel(row_frame, text=appt['status'].capitalize()).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        else:
            ctk.CTkLabel(appts_frame, text="No appointments scheduled for today").grid(row=0, column=0, padx=20, pady=20)
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.current_frame = None

    def create_sidebar(self):
        for button in self.sidebar_buttons:
            button.destroy()
        self.sidebar_buttons = []

        row = 1

        self.home_button = ctk.CTkButton(self.sidebar_frame, text="Home", command=self.show_home)
        self.home_button.grid(row=row, column=0, padx=20, pady=10)
        self.sidebar_buttons.append(self.home_button)
        row += 1

        if self.current_user["role"] in ("admin", "physiotherapist"):
            self.patients_button = ctk.CTkButton(self.sidebar_frame, text="Patients", command=self.show_patients)
            self.patients_button.grid(row=row, column=0, padx=20, pady=10)
            self.sidebar_buttons.append(self.patients_button)
        row += 1

        self.appointments_button = ctk.CTkButton(self.sidebar_frame, text="Appointments", command=self.show_appointments)
        self.appointments_button.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_buttons.append(self.appointments_button)

        row += 1

        if self.current_user["role"] in ("admin", "receptionist"):
            self.billing_button = ctk.CTkButton(self.sidebar_frame, text="Billing", command=self.show_billing)
            self.billing_button.grid(row=row, column=0, padx=20, pady=10)
            self.sidebar_buttons.append(self.billing_button)
        row += 1

        if self.current_user["role"] == "admin":
            self.user_mgmt_button = ctk.CTkButton(self.sidebar_frame, text="User Management", command=self.show_user_management)
            self.user_mgmt_button.grid(row=row, column=0, padx=20, pady=10)
            self.sidebar_buttons.append(self.user_mgmt_button)
        row += 1

        self.reports_button = ctk.CTkButton(self.sidebar_frame, text="Reports", command=self.show_reports)
        self.reports_button.grid(row=4, column=0, padx=20, pady=10)
        self.sidebar_buttons.append(self.reports_button)

        self.billing_button = ctk.CTkButton(self.sidebar_frame, text="Billing", command=self.show_billing)
        self.billing_button.grid(row=5, column=0, padx=20, pady=10)
        self.sidebar_buttons.append(self.billing_button)

        # Spacer
        self.sidebar_frame.grid_rowconfigure(row, weight=1)

        # User info and logout
        user_name = f"{self.current_user['first_name']} {self.current_user['last_name']}"
        self.user_label = ctk.CTkLabel(self.sidebar_frame, text=user_name, font=ctk.CTkFont(size=12))
        self.user_label.grid(row=row, column=0, padx=20, pady=(10, 0))
        self.sidebar_buttons.append(self.user_label)

        row += 1

        self.logout_button = ctk.CTkButton(self.sidebar_frame, text="Logout", fg_color="transparent", command=self.logout)
        self.logout_button.grid(row=row, column=0, padx=20, pady=10)
        self.sidebar_buttons.append(self.logout_button)

    def show_login(self):
        self.clear_content()
        auth.show_login(self)

    def show_register(self):
        self.clear_content()
        auth.show_register(self)

    def logout(self):
        self.current_user = None
        for button in self.sidebar_buttons:
            button.destroy()
        self.sidebar_buttons = []
        self.show_login()

    def show_home(self):
        self.clear_content()
        # Show home screen implementation

    def show_patients(self):
        self.clear_content()
        patients.show_patients(self)

    def show_add_patient(self):
        self.clear_content()
        patients.show_add_patient(self)

    def show_patient_details(self, patient_id):
        self.clear_content()
        patients.show_patient_details(self, patient_id)

    def show_edit_patient(self, patient_id):
        self.clear_content()
        patients.show_edit_patient(self, patient_id)

    def delete_patient_confirm(self, patient_id):
        patients.delete_patient_confirm(self, patient_id)

    def show_add_soap_note(self, patient_id):
        self.clear_content()
        soap_notes.show_add_soap_note(self, patient_id)

    def show_soap_note_details(self, note_id, patient_id):
        self.clear_content()
        soap_notes.show_soap_note_details(self, note_id, patient_id)

    def show_edit_soap_note(self, note_id, patient_id):
        self.clear_content()
        soap_notes.show_edit_soap_note(self, note_id, patient_id)

    def delete_soap_note_confirm(self, note_id, patient_id):
        soap_notes.delete_soap_note_confirm(self, note_id, patient_id)

    def show_appointments(self):
        self.clear_content()
        appointments.show_appointments(self)

    def show_add_appointment(self, patient_id):
        self.clear_content()
        appointments.show_add_appointment(self, patient_id)

    def show_edit_appointment(self, appointment_id, patient_id):
        self.clear_content()
        appointments.show_edit_appointment(self, appointment_id, patient_id)

    def delete_appointment_confirm(self, appointment_id, patient_id):
        appointments.delete_appointment_confirm(self, appointment_id, patient_id)

    def show_reports(self):
        self.clear_content()
        reports.show_reports(self)

    def show_billing(self):
        self.clear_content()
        # Show billing screen implementation

    def show_user_management(self):
        self.clear_content()
        # Show user management implementation

if __name__ == "__main__":
    app = EiraNotesApp()
    app.mainloop()
