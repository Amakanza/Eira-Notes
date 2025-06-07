import tkinter as tk
import customtkinter as ctk
import sqlite3
import datetime
from tkinter import messagebox

DB_PATH = "data/eira_notes.db"

class EditPatientMixin:
    def show_edit_patient(self, patient_id):
        self.clear_content()

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient = dict(cursor.fetchone())
        conn.close()

        frame = ctk.CTkFrame(self.content_frame)
        frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        frame.grid_columnconfigure(0, weight=1)
        self.current_frame = frame

        title = ctk.CTkLabel(
            frame,
            text="Edit Patient",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(20,10))

        form = ctk.CTkFrame(frame)
        form.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        form.grid_columnconfigure((0,1), weight=1)
        scroll = ctk.CTkScrollableFrame(form, width=800, height=400)
        scroll.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        scroll.grid_columnconfigure((0,1), weight=1)

        # Personal info
        ctk.CTkLabel(scroll, text="Personal Information", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")

        ctk.CTkLabel(scroll, text="First Name:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        first_name_entry = ctk.CTkEntry(scroll, width=250)
        first_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        first_name_entry.insert(0, patient['first_name'])

        ctk.CTkLabel(scroll, text="Last Name:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        last_name_entry = ctk.CTkEntry(scroll, width=250)
        last_name_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        last_name_entry.insert(0, patient['last_name'])

        # Date of birth fields
        dob_frame = ctk.CTkFrame(scroll)
        dob_frame.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        dob = datetime.datetime.strptime(patient['date_of_birth'], '%Y-%m-%d')
        day_var = tk.StringVar(value=dob.strftime('%d'))
        ctk.CTkOptionMenu(dob_frame, variable=day_var, values=[str(i).zfill(2) for i in range(1,32)]).grid(row=0,column=0,padx=2)
        month_var = tk.StringVar(value=dob.strftime('%m'))
        ctk.CTkOptionMenu(dob_frame, variable=month_var, values=[str(i).zfill(2) for i in range(1,13)]).grid(row=0,column=1,padx=2)
        year_var = tk.StringVar(value=dob.strftime('%Y'))
        current_year = datetime.datetime.now().year
        ctk.CTkOptionMenu(dob_frame, variable=year_var, values=[str(i) for i in range(current_year-100, current_year+1)]).grid(row=0,column=2,padx=2)
        ctk.CTkLabel(scroll, text="Date of Birth:").grid(row=3, column=0, padx=10, pady=5, sticky="e")

        gender_var = tk.StringVar(value=patient['gender'] if patient['gender'] else "Select Gender")
        ctk.CTkLabel(scroll, text="Gender:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        gender_dropdown = ctk.CTkOptionMenu(scroll, variable=gender_var, values=["male","female","other"])
        gender_dropdown.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Contact info
        ctk.CTkLabel(scroll, text="Contact Information", font=ctk.CTkFont(size=16, weight="bold")).grid(row=5, column=0, columnspan=2, padx=10, pady=(20,5), sticky="w")
        ctk.CTkLabel(scroll, text="Phone Number:").grid(row=6, column=0, padx=10, pady=5, sticky="e")
        phone_entry = ctk.CTkEntry(scroll, width=250)
        phone_entry.grid(row=6, column=1, padx=10, pady=5, sticky="w")
        phone_entry.insert(0, patient.get('phone',''))
        ctk.CTkLabel(scroll, text="Email:").grid(row=7, column=0, padx=10, pady=5, sticky="e")
        email_entry = ctk.CTkEntry(scroll, width=250)
        email_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")
        email_entry.insert(0, patient.get('email',''))
        ctk.CTkLabel(scroll, text="Address:").grid(row=8, column=0, padx=10, pady=5, sticky="e")
        address_entry = ctk.CTkEntry(scroll, width=250)
        address_entry.grid(row=8, column=1, padx=10, pady=5, sticky="w")
        address_entry.insert(0, patient.get('address',''))

        # Medical info
        ctk.CTkLabel(scroll, text="Medical Information", font=ctk.CTkFont(size=16, weight="bold")).grid(row=9, column=0, columnspan=2, padx=10, pady=(20,5), sticky="w")
        ctk.CTkLabel(scroll, text="Medical Aid Provider:").grid(row=10, column=0, padx=10, pady=5, sticky="e")
        med_aid_entry = ctk.CTkEntry(scroll, width=250)
        med_aid_entry.grid(row=10, column=1, padx=10, pady=5, sticky="w")
        med_aid_entry.insert(0, patient.get('medical_aid_name',''))
        ctk.CTkLabel(scroll, text="Medical Aid Number:").grid(row=11, column=0, padx=10, pady=5, sticky="e")
        med_num_entry = ctk.CTkEntry(scroll, width=250)
        med_num_entry.grid(row=11, column=1, padx=10, pady=5, sticky="w")
        med_num_entry.insert(0, patient.get('medical_aid_number',''))
        ctk.CTkLabel(scroll, text="Medical History:").grid(row=12, column=0, padx=10, pady=5, sticky="ne")
        history_entry = ctk.CTkTextbox(scroll, width=250, height=100)
        history_entry.grid(row=12, column=1, padx=10, pady=5, sticky="w")
        history_entry.insert("1.0", patient.get('medical_history',''))
        ctk.CTkLabel(scroll, text="Diagnosis:").grid(row=13, column=0, padx=10, pady=5, sticky="e")
        diagnosis_entry = ctk.CTkEntry(scroll, width=250)
        diagnosis_entry.grid(row=13, column=1, padx=10, pady=5, sticky="w")
        diagnosis_entry.insert(0, patient.get('diagnosis',''))

        error_label = ctk.CTkLabel(scroll, text="", text_color="red")
        error_label.grid(row=14, column=0, columnspan=2, padx=10, pady=(10,0))

        button_frame = ctk.CTkFrame(scroll)
        button_frame.grid(row=15, column=0, columnspan=2, padx=10, pady=20)

        def handle_save():
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            gender = gender_var.get() if gender_var.get() != "Select Gender" else ""
            date_of_birth = f"{year_var.get()}-{month_var.get()}-{day_var.get()}"

            if not first_name or not last_name or gender == "":
                error_label.configure(text="First name, last name, and gender are required")
                return
            try:
                datetime.datetime.strptime(date_of_birth, '%Y-%m-%d')
            except ValueError:
                error_label.configure(text="Invalid date of birth")
                return
            if not diagnosis_entry.get():
                error_label.configure(text="Diagnosis is required")
                return

            data = {
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

            result = update_patient(patient_id, data)
            if result["success"]:
                messagebox.showinfo("Success", result["message"])
                self.show_patient_details(patient_id)
            else:
                error_label.configure(text=result["message"])

        save_button = ctk.CTkButton(button_frame, text="Update Patient", command=handle_save)
        save_button.grid(row=0, column=0, padx=10, pady=10)
        cancel_button = ctk.CTkButton(button_frame, text="Cancel", fg_color="transparent", command=lambda: self.show_patient_details(patient_id))
        cancel_button.grid(row=0, column=1, padx=10, pady=10)
