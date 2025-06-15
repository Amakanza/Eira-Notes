import logging
from typing import Dict, Any, List, Optional, Callable

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from app.app import EiraApp

logger = logging.getLogger(__name__)


class PatientForm(ctk.CTkFrame):
    """Form for creating and editing patients."""

    def __init__(
        self,
        master,
        app: EiraApp,
        on_save: Callable[[Dict[str, Any]], None],
        on_cancel: Callable[[], None],
        patient_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(master)
        self.master = master
        self.app = app
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.patient_data = patient_data or {}
        self.is_edit_mode = bool(patient_data)

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Form title
        title_text = "Edit Patient" if self.is_edit_mode else "New Patient"
        self.title_label = ctk.CTkLabel(
            self,
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        # Form fields
        self.fields = {}
        row = 1

        # First name
        self.fields["first_name"] = self._create_field(
            "First Name", row, 0, self.patient_data.get("first_name", "")
        )
        
        # Last name
        self.fields["last_name"] = self._create_field(
            "Last Name", row, 1, self.patient_data.get("last_name", "")
        )
        row += 1

        # Date of birth
        self.fields["date_of_birth"] = self._create_field(
            "Date of Birth (YYYY-MM-DD)", row, 0, self.patient_data.get("date_of_birth", "")
        )
        
        # Gender
        gender_frame = ctk.CTkFrame(self, fg_color="transparent")
        gender_frame.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
        
        gender_label = ctk.CTkLabel(
            gender_frame,
            text="Gender",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        gender_label.pack(anchor="w", padx=5, pady=(0, 5))
        
        self.gender_var = tk.StringVar(value=self.patient_data.get("gender", ""))
        gender_options = ["Male", "Female", "Other", "Prefer not to say"]
        
        self.fields["gender"] = ctk.CTkOptionMenu(
            gender_frame,
            values=gender_options,
            variable=self.gender_var,
            width=200,
        )
        self.fields["gender"].pack(anchor="w", padx=5)
        row += 1

        # Phone
        self.fields["phone"] = self._create_field(
            "Phone", row, 0, self.patient_data.get("phone", "")
        )
        
        # Email
        self.fields["email"] = self._create_field(
            "Email", row, 1, self.patient_data.get("email", "")
        )
        row += 1

        # Address
        self.fields["address"] = self._create_field(
            "Address", row, 0, self.patient_data.get("address", ""), columnspan=2
        )
        row += 1

        # Medical history
        medical_history_frame = ctk.CTkFrame(self, fg_color="transparent")
        medical_history_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        medical_history_label = ctk.CTkLabel(
            medical_history_frame,
            text="Medical History",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        medical_history_label.pack(anchor="w", padx=5, pady=(0, 5))
        
        self.fields["medical_history"] = ctk.CTkTextbox(
            medical_history_frame,
            height=100,
            width=400,
        )
        self.fields["medical_history"].pack(fill="x", padx=5)
        
        if self.patient_data.get("medical_history"):
            self.fields["medical_history"].insert("0.0", self.patient_data.get("medical_history", ""))
        row += 1

        # Buttons
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="e")

        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.on_cancel,
            fg_color="gray",
            width=100,
        )
        cancel_button.pack(side="left", padx=5)

        save_button = ctk.CTkButton(
            buttons_frame,
            text="Save",
            command=self._on_save_click,
            width=100,
        )
        save_button.pack(side="left", padx=5)

    def _create_field(
        self, label_text: str, row: int, col: int, default_value: str = "", columnspan: int = 1
    ):
        """Create a form field with label."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=row, column=col, columnspan=columnspan, padx=10, pady=10, sticky="ew")

        label = ctk.CTkLabel(
            frame,
            text=label_text,
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        label.pack(anchor="w", padx=5, pady=(0, 5))

        entry = ctk.CTkEntry(frame, width=200)
        entry.pack(anchor="w", padx=5, fill="x" if columnspan > 1 else None)

        if default_value:
            entry.insert(0, default_value)

        return entry

    def _on_save_click(self):
        """Handle save button click."""
        # Validate form
        if not self._validate_form():
            return

        # Collect form data
        patient_data = {}
        for field_name, field_widget in self.fields.items():
            if field_name == "medical_history":
                patient_data[field_name] = field_widget.get("0.0", "end")
            elif field_name == "gender":
                patient_data[field_name] = self.gender_var.get()
            else:
                patient_data[field_name] = field_widget.get()

        # If editing, include the patient ID
        if self.is_edit_mode and "id" in self.patient_data:
            patient_data["id"] = self.patient_data["id"]

        # Call save callback
        self.on_save(patient_data)

    def _validate_form(self) -> bool:
        """Validate form fields."""
        # Check required fields
        required_fields = ["first_name", "last_name", "date_of_birth"]
        for field_name in required_fields:
            if field_name in self.fields and not self.fields[field_name].get():
                messagebox.showerror(
                    "Validation Error", f"{field_name.replace('_', ' ').title()} is required"
                )
                return False

        # Validate date format (simple check)
        dob = self.fields["date_of_birth"].get()
        if dob and not self._is_valid_date(dob):
            messagebox.showerror(
                "Validation Error", "Date of Birth must be in YYYY-MM-DD format"
            )
            return False

        return True

    def _is_valid_date(self, date_str: str) -> bool:
        """Simple validation for date format YYYY-MM-DD."""
        if len(date_str) != 10:
            return False

        try:
            year, month, day = date_str.split("-")
            if not (len(year) == 4 and len(month) == 2 and len(day) == 2):
                return False
            if not (year.isdigit() and month.isdigit() and day.isdigit()):
                return False
            if not (1 <= int(month) <= 12 and 1 <= int(day) <= 31):
                return False
            return True
        except ValueError:
            return False


class PatientsView(ctk.CTkFrame):
    """Patients view for the Eira desktop application."""

    def __init__(self, master, app: EiraApp):
        super().__init__(master)
        self.master = master
        self.app = app
        self.current_form = None

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create top bar with search and add button
        self._create_top_bar()

        # Create patients list
        self._create_patients_list()

        # Load patients
        self.refresh_patients()

    def _create_top_bar(self):
        """Create top bar with search and add button."""
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        top_bar.grid_columnconfigure(0, weight=1)

        # Search frame
        search_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search patients...",
            width=300,
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda event: self._on_search())

        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            width=80,
            command=self._on_search,
        )
        search_button.pack(side="left")

        # Add button
        add_button = ctk.CTkButton(
            top_bar,
            text="+ Add Patient",
            width=120,
            command=self._on_add_patient,
        )
        add_button.pack(side="right")

    def _create_patients_list(self):
        """Create patients list."""
        # Container frame for list or form
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Patients list frame
        self.patients_list_frame = ctk.CTkScrollableFrame(self.content_frame)
        self.patients_list_frame.grid(row=0, column=0, sticky="nsew")

    def refresh_patients(self, search_query: str = ""):
        """Refresh patients list, optionally filtering by search query."""
        # Clear existing list
        for widget in self.patients_list_frame.winfo_children():
            widget.destroy()

        try:
            # Get patients from database
            filters = {}
            if search_query:
                filters["search"] = search_query

            patients = self.app.db.get_patients(filters=filters)

            if not patients:
                no_data_label = ctk.CTkLabel(
                    self.patients_list_frame,
                    text="No patients found",
                    font=ctk.CTkFont(size=14),
                    text_color="gray",
                )
                no_data_label.pack(pady=20)
                return

            # Create header row
            header_frame = ctk.CTkFrame(self.patients_list_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=(5, 10))

            headers = ["Name", "DOB", "Gender", "Phone", "Actions"]
            widths = [250, 100, 100, 150, 150]

            for i, header_text in enumerate(headers):
                header_label = ctk.CTkLabel(
                    header_frame,
                    text=header_text,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    width=widths[i],
                    anchor="w",
                )
                header_label.pack(side="left", padx=5)

            # Add separator
            separator = ctk.CTkFrame(self.patients_list_frame, height=1, fg_color="gray")
            separator.pack(fill="x", padx=10, pady=5)

            # Add patient rows
            for patient in patients:
                self._add_patient_row(patient)

        except Exception as e:
            logger.error(f"Error loading patients: {e}")
            error_label = ctk.CTkLabel(
                self.patients_list_frame,
                text=f"Error loading patients: {str(e)}",
                font=ctk.CTkFont(size=14),
                text_color="red",
            )
            error_label.pack(pady=20)

    def _add_patient_row(self, patient: Dict[str, Any]):
        """Add a patient row to the list."""
        row_frame = ctk.CTkFrame(self.patients_list_frame, fg_color="transparent")
        row_frame.pack(fill="x", padx=10, pady=5)

        # Name
        name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}"
        name_label = ctk.CTkLabel(
            row_frame,
            text=name,
            font=ctk.CTkFont(size=14),
            width=250,
            anchor="w",
        )
        name_label.pack(side="left", padx=5)

        # DOB
        dob_label = ctk.CTkLabel(
            row_frame,
            text=patient.get("date_of_birth", "N/A"),
            font=ctk.CTkFont(size=14),
            width=100,
            anchor="w",
        )
        dob_label.pack(side="left", padx=5)

        # Gender
        gender_label = ctk.CTkLabel(
            row_frame,
            text=patient.get("gender", "N/A"),
            font=ctk.CTkFont(size=14),
            width=100,
            anchor="w",
        )
        gender_label.pack(side="left", padx=5)

        # Phone
        phone_label = ctk.CTkLabel(
            row_frame,
            text=patient.get("phone", "N/A"),
            font=ctk.CTkFont(size=14),
            width=150,
            anchor="w",
        )
        phone_label.pack(side="left", padx=5)

        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=150)
        actions_frame.pack(side="left", padx=5)

        view_button = ctk.CTkButton(
            actions_frame,
            text="View",
            width=60,
            height=24,
            font=ctk.CTkFont(size=12),
            command=lambda p=patient: self._on_view_patient(p),
        )
        view_button.pack(side="left", padx=(0, 5))

        edit_button = ctk.CTkButton(
            actions_frame,
            text="Edit",
            width=60,
            height=24,
            font=ctk.CTkFont(size=12),
            command=lambda p=patient: self._on_edit_patient(p),
        )
        edit_button.pack(side="left")

    def _on_search(self):
        """Handle search button click."""
        search_query = self.search_entry.get()
        self.refresh_patients(search_query)

    def _on_add_patient(self):
        """Handle add patient button click."""
        # Hide patients list
        self.patients_list_frame.grid_forget()

        # Create and show patient form
        self.current_form = PatientForm(
            self.content_frame,
            self.app,
            on_save=self._on_save_patient,
            on_cancel=self._on_cancel_form,
        )
        self.current_form.grid(row=0, column=0, sticky="nsew")

    def _on_edit_patient(self, patient: Dict[str, Any]):
        """Handle edit patient button click."""
        # Hide patients list
        self.patients_list_frame.grid_forget()

        # Create and show patient form with patient data
        self.current_form = PatientForm(
            self.content_frame,
            self.app,
            on_save=self._on_save_patient,
            on_cancel=self._on_cancel_form,
            patient_data=patient,
        )
        self.current_form.grid(row=0, column=0, sticky="nsew")

    def _on_view_patient(self, patient: Dict[str, Any]):
        """Handle view patient button click."""
        # This would be implemented to show patient detail view
        logger.info(f"View patient: {patient.get('id')}")
        messagebox.showinfo(
            "Patient Details",
            f"Viewing details for {patient.get('first_name')} {patient.get('last_name')}\n\n"
            f"ID: {patient.get('id')}\n"
            f"DOB: {patient.get('date_of_birth')}\n"
            f"Gender: {patient.get('gender')}\n"
            f"Phone: {patient.get('phone')}\n"
            f"Email: {patient.get('email')}\n"
            f"Address: {patient.get('address')}\n\n"
            f"Medical History:\n{patient.get('medical_history')}",
        )

    def _on_save_patient(self, patient_data: Dict[str, Any]):
        """Handle save patient from form."""
        try:
            # Determine if creating or updating
            if "id" in patient_data:
                # Update existing patient
                patient_id = patient_data["id"]
                self.app.db.update_patient(patient_id, patient_data)
                messagebox.showinfo("Success", "Patient updated successfully")
            else:
                # Create new patient
                self.app.db.create_patient(patient_data)
                messagebox.showinfo("Success", "Patient created successfully")

            # Close form and refresh list
            self._on_cancel_form()
            self.refresh_patients()

        except Exception as e:
            logger.error(f"Error saving patient: {e}")
            messagebox.showerror("Error", f"Error saving patient: {str(e)}")

    def _on_cancel_form(self):
        """Handle cancel button click on form."""
        # Remove form
        if self.current_form:
            self.current_form.destroy()
            self.current_form = None

        # Show patients list again
        self.patients_list_frame.grid(row=0, column=0, sticky="nsew")