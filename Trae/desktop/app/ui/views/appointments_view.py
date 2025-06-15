import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from app.app import EiraApp

logger = logging.getLogger(__name__)


class AppointmentForm(ctk.CTkFrame):
    """Form for creating and editing appointments."""

    def __init__(
        self,
        master,
        app: EiraApp,
        on_save: Callable[[Dict[str, Any]], None],
        on_cancel: Callable[[], None],
        appointment_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(master)
        self.master = master
        self.app = app
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.appointment_data = appointment_data or {}
        self.is_edit_mode = bool(appointment_data)
        self.patients = []

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Form title
        title_text = "Edit Appointment" if self.is_edit_mode else "New Appointment"
        self.title_label = ctk.CTkLabel(
            self,
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        # Load patients for dropdown
        self._load_patients()

        # Form fields
        self.fields = {}
        row = 1

        # Patient selection
        patient_frame = ctk.CTkFrame(self, fg_color="transparent")
        patient_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        patient_label = ctk.CTkLabel(
            patient_frame,
            text="Patient",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        patient_label.pack(anchor="w", padx=5, pady=(0, 5))

        # Create patient dropdown
        self.patient_var = tk.StringVar()
        self.fields["patient"] = ctk.CTkOptionMenu(
            patient_frame,
            values=self._get_patient_display_names(),
            variable=self.patient_var,
            width=300,
            dynamic_resizing=False,
        )
        self.fields["patient"].pack(anchor="w", padx=5, fill="x")

        # Set selected patient if editing
        if self.is_edit_mode and "patient_id" in self.appointment_data:
            self._set_selected_patient(self.appointment_data["patient_id"])

        row += 1

        # Date
        self.fields["date"] = self._create_field(
            "Date (YYYY-MM-DD)",
            row,
            0,
            self.appointment_data.get("date", self._get_today_date()),
        )

        # Time
        time_frame = ctk.CTkFrame(self, fg_color="transparent")
        time_frame.grid(row=row, column=1, padx=10, pady=10, sticky="ew")

        time_label = ctk.CTkLabel(
            time_frame,
            text="Time",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        time_label.pack(anchor="w", padx=5, pady=(0, 5))

        # Create time dropdown with common appointment times
        times = self._generate_appointment_times()
        self.time_var = tk.StringVar()
        self.fields["time"] = ctk.CTkOptionMenu(
            time_frame,
            values=times,
            variable=self.time_var,
            width=200,
        )
        self.fields["time"].pack(anchor="w", padx=5)

        # Set selected time if editing
        if self.is_edit_mode and "time" in self.appointment_data:
            self.time_var.set(self.appointment_data["time"])
        else:
            self.time_var.set("09:00")

        row += 1

        # Duration
        duration_frame = ctk.CTkFrame(self, fg_color="transparent")
        duration_frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")

        duration_label = ctk.CTkLabel(
            duration_frame,
            text="Duration (minutes)",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        duration_label.pack(anchor="w", padx=5, pady=(0, 5))

        # Create duration dropdown
        durations = ["15", "30", "45", "60", "90", "120"]
        self.duration_var = tk.StringVar()
        self.fields["duration"] = ctk.CTkOptionMenu(
            duration_frame,
            values=durations,
            variable=self.duration_var,
            width=200,
        )
        self.fields["duration"].pack(anchor="w", padx=5)

        # Set selected duration if editing
        if self.is_edit_mode and "duration" in self.appointment_data:
            self.duration_var.set(str(self.appointment_data["duration"]))
        else:
            self.duration_var.set("30")

        # Appointment type
        type_frame = ctk.CTkFrame(self, fg_color="transparent")
        type_frame.grid(row=row, column=1, padx=10, pady=10, sticky="ew")

        type_label = ctk.CTkLabel(
            type_frame,
            text="Appointment Type",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        type_label.pack(anchor="w", padx=5, pady=(0, 5))

        # Create type dropdown
        types = ["Initial Consultation", "Follow-up", "Procedure", "Review", "Other"]
        self.type_var = tk.StringVar()
        self.fields["type"] = ctk.CTkOptionMenu(
            type_frame,
            values=types,
            variable=self.type_var,
            width=200,
        )
        self.fields["type"].pack(anchor="w", padx=5)

        # Set selected type if editing
        if self.is_edit_mode and "type" in self.appointment_data:
            self.type_var.set(self.appointment_data["type"])
        else:
            self.type_var.set("Initial Consultation")

        row += 1

        # Notes
        notes_frame = ctk.CTkFrame(self, fg_color="transparent")
        notes_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        notes_label = ctk.CTkLabel(
            notes_frame,
            text="Notes",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        notes_label.pack(anchor="w", padx=5, pady=(0, 5))

        self.fields["notes"] = ctk.CTkTextbox(
            notes_frame,
            height=100,
            width=400,
        )
        self.fields["notes"].pack(fill="x", padx=5)

        if self.is_edit_mode and "notes" in self.appointment_data:
            self.fields["notes"].insert("0.0", self.appointment_data["notes"])

        row += 1

        # Status
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")

        status_label = ctk.CTkLabel(
            status_frame,
            text="Status",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        status_label.pack(anchor="w", padx=5, pady=(0, 5))

        # Create status dropdown
        statuses = ["Scheduled", "Confirmed", "Completed", "Cancelled", "No-show"]
        self.status_var = tk.StringVar()
        self.fields["status"] = ctk.CTkOptionMenu(
            status_frame,
            values=statuses,
            variable=self.status_var,
            width=200,
        )
        self.fields["status"].pack(anchor="w", padx=5)

        # Set selected status if editing
        if self.is_edit_mode and "status" in self.appointment_data:
            self.status_var.set(self.appointment_data["status"])
        else:
            self.status_var.set("Scheduled")

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

    def _load_patients(self):
        """Load patients for dropdown."""
        try:
            self.patients = self.app.db.get_patients()
        except Exception as e:
            logger.error(f"Error loading patients: {e}")
            self.patients = []

    def _get_patient_display_names(self) -> List[str]:
        """Get patient display names for dropdown."""
        if not self.patients:
            return ["No patients available"]

        return [
            f"{p.get('first_name', '')} {p.get('last_name', '')} (ID: {p.get('id', '')})" 
            for p in self.patients
        ]

    def _set_selected_patient(self, patient_id: str):
        """Set the selected patient in the dropdown."""
        for i, patient in enumerate(self.patients):
            if patient.get("id") == patient_id:
                display_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')} (ID: {patient.get('id', '')})" 
                self.patient_var.set(display_name)
                return

    def _get_patient_id_from_selection(self) -> Optional[str]:
        """Extract patient ID from the selected dropdown value."""
        selection = self.patient_var.get()
        if "ID:" not in selection:
            return None

        try:
            # Extract ID from format "Name (ID: XXX)"
            id_part = selection.split("ID:")[-1].strip()
            return id_part.rstrip(")")
        except Exception:
            return None

    def _generate_appointment_times(self) -> List[str]:
        """Generate list of appointment times in 15-minute increments."""
        times = []
        start = datetime.strptime("08:00", "%H:%M")
        end = datetime.strptime("18:00", "%H:%M")
        delta = timedelta(minutes=15)

        current = start
        while current <= end:
            times.append(current.strftime("%H:%M"))
            current += delta

        return times

    def _get_today_date(self) -> str:
        """Get today's date in YYYY-MM-DD format."""
        return datetime.now().strftime("%Y-%m-%d")

    def _on_save_click(self):
        """Handle save button click."""
        # Validate form
        if not self._validate_form():
            return

        # Collect form data
        appointment_data = {
            "patient_id": self._get_patient_id_from_selection(),
            "date": self.fields["date"].get(),
            "time": self.time_var.get(),
            "duration": int(self.duration_var.get()),
            "type": self.type_var.get(),
            "status": self.status_var.get(),
            "notes": self.fields["notes"].get("0.0", "end").strip(),
        }

        # If editing, include the appointment ID
        if self.is_edit_mode and "id" in self.appointment_data:
            appointment_data["id"] = self.appointment_data["id"]

        # Call save callback
        self.on_save(appointment_data)

    def _validate_form(self) -> bool:
        """Validate form fields."""
        # Check patient selection
        patient_id = self._get_patient_id_from_selection()
        if not patient_id:
            messagebox.showerror("Validation Error", "Please select a patient")
            return False

        # Check date format
        date_str = self.fields["date"].get()
        if not date_str or not self._is_valid_date(date_str):
            messagebox.showerror(
                "Validation Error", "Date must be in YYYY-MM-DD format"
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


class AppointmentsView(ctk.CTkFrame):
    """Appointments view for the Eira desktop application."""

    def __init__(self, master, app: EiraApp):
        super().__init__(master)
        self.master = master
        self.app = app
        self.current_form = None
        self.current_date = datetime.now().date()

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create top bar with date navigation and add button
        self._create_top_bar()

        # Create appointments list
        self._create_appointments_list()

        # Load appointments for current date
        self.refresh_appointments()

    def _create_top_bar(self):
        """Create top bar with date navigation and add button."""
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        top_bar.grid_columnconfigure(1, weight=1)

        # Date navigation
        date_nav_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        date_nav_frame.grid(row=0, column=0, sticky="w")

        prev_day_button = ctk.CTkButton(
            date_nav_frame,
            text="<",
            width=30,
            command=self._on_prev_day,
        )
        prev_day_button.pack(side="left", padx=(0, 5))

        self.date_label = ctk.CTkLabel(
            date_nav_frame,
            text=self._format_date(self.current_date),
            font=ctk.CTkFont(size=16, weight="bold"),
            width=200,
        )
        self.date_label.pack(side="left")

        next_day_button = ctk.CTkButton(
            date_nav_frame,
            text=">",
            width=30,
            command=self._on_next_day,
        )
        next_day_button.pack(side="left", padx=(5, 0))

        today_button = ctk.CTkButton(
            date_nav_frame,
            text="Today",
            width=80,
            command=self._on_today,
        )
        today_button.pack(side="left", padx=(10, 0))

        # View options
        view_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        view_frame.grid(row=0, column=1, sticky="e")

        # View options (day, week, month)
        self.view_var = tk.StringVar(value="Day")
        view_options = ["Day", "Week", "Month"]
        view_selector = ctk.CTkSegmentedButton(
            view_frame,
            values=view_options,
            variable=self.view_var,
            command=self._on_view_change,
        )
        view_selector.pack(side="left", padx=(0, 10))

        # Add button
        add_button = ctk.CTkButton(
            view_frame,
            text="+ Add Appointment",
            width=150,
            command=self._on_add_appointment,
        )
        add_button.pack(side="left")

    def _create_appointments_list(self):
        """Create appointments list."""
        # Container frame for list or form
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Appointments list frame
        self.appointments_list_frame = ctk.CTkScrollableFrame(self.content_frame)
        self.appointments_list_frame.grid(row=0, column=0, sticky="nsew")

    def refresh_appointments(self):
        """Refresh appointments list for the current date/view."""
        # Clear existing list
        for widget in self.appointments_list_frame.winfo_children():
            widget.destroy()

        try:
            # Get date range based on current view
            date_range = self._get_date_range()
            start_date, end_date = date_range

            # Get appointments from database
            filters = {
                "date_gte": start_date.isoformat(),
                "date_lt": end_date.isoformat(),
            }

            appointments = self.app.db.get_appointments(
                filters=filters, order_by="date,time"
            )

            if not appointments:
                no_data_label = ctk.CTkLabel(
                    self.appointments_list_frame,
                    text=f"No appointments found for {self._get_view_description()}",
                    font=ctk.CTkFont(size=14),
                    text_color="gray",
                )
                no_data_label.pack(pady=20)
                return

            # Group appointments by date if in week or month view
            current_view = self.view_var.get()
            if current_view in ["Week", "Month"]:
                self._display_grouped_appointments(appointments)
            else:
                self._display_day_appointments(appointments)

        except Exception as e:
            logger.error(f"Error loading appointments: {e}")
            error_label = ctk.CTkLabel(
                self.appointments_list_frame,
                text=f"Error loading appointments: {str(e)}",
                font=ctk.CTkFont(size=14),
                text_color="red",
            )
            error_label.pack(pady=20)

    def _display_day_appointments(self, appointments: List[Dict[str, Any]]):
        """Display appointments for a single day."""
        # Create header row
        header_frame = ctk.CTkFrame(self.appointments_list_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(5, 10))

        headers = ["Time", "Patient", "Type", "Duration", "Status", "Actions"]
        widths = [80, 200, 150, 80, 100, 150]

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
        separator = ctk.CTkFrame(self.appointments_list_frame, height=1, fg_color="gray")
        separator.pack(fill="x", padx=10, pady=5)

        # Add appointment rows
        for appointment in appointments:
            self._add_appointment_row(appointment)

    def _display_grouped_appointments(self, appointments: List[Dict[str, Any]]):
        """Display appointments grouped by date for week or month view."""
        # Group appointments by date
        grouped = {}
        for appointment in appointments:
            date_str = appointment.get("date", "")
            if date_str not in grouped:
                grouped[date_str] = []
            grouped[date_str].append(appointment)

        # Display each date group
        for date_str in sorted(grouped.keys()):
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                date_display = self._format_date(date_obj)

                # Date header
                date_header = ctk.CTkFrame(self.appointments_list_frame, fg_color="transparent")
                date_header.pack(fill="x", padx=10, pady=(15, 5))

                date_label = ctk.CTkLabel(
                    date_header,
                    text=date_display,
                    font=ctk.CTkFont(size=16, weight="bold"),
                    anchor="w",
                )
                date_label.pack(side="left")

                # Add separator
                separator = ctk.CTkFrame(self.appointments_list_frame, height=1, fg_color="gray")
                separator.pack(fill="x", padx=10, pady=5)

                # Add appointments for this date
                for appointment in grouped[date_str]:
                    self._add_appointment_row(appointment)

            except Exception as e:
                logger.error(f"Error displaying date group {date_str}: {e}")

    def _add_appointment_row(self, appointment: Dict[str, Any]):
        """Add an appointment row to the list."""
        row_frame = ctk.CTkFrame(self.appointments_list_frame, fg_color="transparent")
        row_frame.pack(fill="x", padx=10, pady=5)

        # Time
        time_label = ctk.CTkLabel(
            row_frame,
            text=appointment.get("time", "N/A"),
            font=ctk.CTkFont(size=14),
            width=80,
            anchor="w",
        )
        time_label.pack(side="left", padx=5)

        # Get patient info
        patient_id = appointment.get("patient_id")
        patient_name = "Unknown Patient"
        try:
            if patient_id:
                patient = self.app.db.get_patient(patient_id)
                if patient:
                    patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}"
        except Exception as e:
            logger.error(f"Error getting patient for appointment: {e}")

        # Patient name
        patient_label = ctk.CTkLabel(
            row_frame,
            text=patient_name,
            font=ctk.CTkFont(size=14),
            width=200,
            anchor="w",
        )
        patient_label.pack(side="left", padx=5)

        # Type
        type_label = ctk.CTkLabel(
            row_frame,
            text=appointment.get("type", "N/A"),
            font=ctk.CTkFont(size=14),
            width=150,
            anchor="w",
        )
        type_label.pack(side="left", padx=5)

        # Duration
        duration_label = ctk.CTkLabel(
            row_frame,
            text=f"{appointment.get('duration', 'N/A')} min",
            font=ctk.CTkFont(size=14),
            width=80,
            anchor="w",
        )
        duration_label.pack(side="left", padx=5)

        # Status
        status = appointment.get("status", "Scheduled")
        status_color = "gray"
        if status == "Confirmed":
            status_color = "blue"
        elif status == "Completed":
            status_color = "green"
        elif status == "Cancelled" or status == "No-show":
            status_color = "red"

        status_label = ctk.CTkLabel(
            row_frame,
            text=status,
            font=ctk.CTkFont(size=14),
            text_color=status_color,
            width=100,
            anchor="w",
        )
        status_label.pack(side="left", padx=5)

        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=150)
        actions_frame.pack(side="left", padx=5)

        edit_button = ctk.CTkButton(
            actions_frame,
            text="Edit",
            width=60,
            height=24,
            font=ctk.CTkFont(size=12),
            command=lambda a=appointment: self._on_edit_appointment(a),
        )
        edit_button.pack(side="left", padx=(0, 5))

        cancel_button = ctk.CTkButton(
            actions_frame,
            text="Cancel",
            width=60,
            height=24,
            font=ctk.CTkFont(size=12),
            fg_color="red",
            command=lambda a=appointment: self._on_cancel_appointment(a),
        )
        cancel_button.pack(side="left")

    def _format_date(self, date_obj: datetime.date) -> str:
        """Format date for display."""
        return date_obj.strftime("%A, %B %d, %Y")

    def _get_date_range(self) -> tuple:
        """Get date range based on current view."""
        current_view = self.view_var.get()
        start_date = self.current_date
        end_date = self.current_date + timedelta(days=1)

        if current_view == "Week":
            # Start from Monday of the current week
            start_date = self.current_date - timedelta(days=self.current_date.weekday())
            end_date = start_date + timedelta(days=7)
        elif current_view == "Month":
            # Start from the 1st of the current month
            start_date = self.current_date.replace(day=1)
            # End on the 1st of the next month
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1)

        return start_date, end_date

    def _get_view_description(self) -> str:
        """Get description of current view for display."""
        current_view = self.view_var.get()
        if current_view == "Day":
            return self._format_date(self.current_date)
        elif current_view == "Week":
            start_date, end_date = self._get_date_range()
            return f"Week of {start_date.strftime('%B %d, %Y')}"
        elif current_view == "Month":
            return self.current_date.strftime("%B %Y")
        return ""

    def _on_prev_day(self):
        """Handle previous day button click."""
        current_view = self.view_var.get()
        if current_view == "Day":
            self.current_date -= timedelta(days=1)
        elif current_view == "Week":
            self.current_date -= timedelta(days=7)
        elif current_view == "Month":
            # Go to previous month
            year = self.current_date.year
            month = self.current_date.month - 1
            if month == 0:
                year -= 1
                month = 12
            self.current_date = self.current_date.replace(year=year, month=month)

        self.date_label.configure(text=self._get_view_description())
        self.refresh_appointments()

    def _on_next_day(self):
        """Handle next day button click."""
        current_view = self.view_var.get()
        if current_view == "Day":
            self.current_date += timedelta(days=1)
        elif current_view == "Week":
            self.current_date += timedelta(days=7)
        elif current_view == "Month":
            # Go to next month
            year = self.current_date.year
            month = self.current_date.month + 1
            if month == 13:
                year += 1
                month = 1
            self.current_date = self.current_date.replace(year=year, month=month)

        self.date_label.configure(text=self._get_view_description())
        self.refresh_appointments()

    def _on_today(self):
        """Handle today button click."""
        self.current_date = datetime.now().date()
        self.date_label.configure(text=self._get_view_description())
        self.refresh_appointments()

    def _on_view_change(self, value):
        """Handle view change."""
        self.date_label.configure(text=self._get_view_description())
        self.refresh_appointments()

    def _on_add_appointment(self):
        """Handle add appointment button click."""
        # Hide appointments list
        self.appointments_list_frame.grid_forget()

        # Create and show appointment form
        self.current_form = AppointmentForm(
            self.content_frame,
            self.app,
            on_save=self._on_save_appointment,
            on_cancel=self._on_cancel_form,
        )
        self.current_form.grid(row=0, column=0, sticky="nsew")

    def _on_edit_appointment(self, appointment: Dict[str, Any]):
        """Handle edit appointment button click."""
        # Hide appointments list
        self.appointments_list_frame.grid_forget()

        # Create and show appointment form with appointment data
        self.current_form = AppointmentForm(
            self.content_frame,
            self.app,
            on_save=self._on_save_appointment,
            on_cancel=self._on_cancel_form,
            appointment_data=appointment,
        )
        self.current_form.grid(row=0, column=0, sticky="nsew")

    def _on_cancel_appointment(self, appointment: Dict[str, Any]):
        """Handle cancel appointment button click."""
        appointment_id = appointment.get("id")
        if not appointment_id:
            return

        # Confirm cancellation
        confirm = messagebox.askyesno(
            "Confirm Cancellation",
            "Are you sure you want to cancel this appointment?",
        )
        if not confirm:
            return

        try:
            # Update appointment status to cancelled
            self.app.db.update_appointment(
                appointment_id, {"status": "Cancelled"}
            )
            messagebox.showinfo("Success", "Appointment cancelled successfully")
            self.refresh_appointments()
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            messagebox.showerror("Error", f"Error cancelling appointment: {str(e)}")

    def _on_save_appointment(self, appointment_data: Dict[str, Any]):
        """Handle save appointment from form."""
        try:
            # Determine if creating or updating
            if "id" in appointment_data:
                # Update existing appointment
                appointment_id = appointment_data["id"]
                self.app.db.update_appointment(appointment_id, appointment_data)
                messagebox.showinfo("Success", "Appointment updated successfully")
            else:
                # Create new appointment
                self.app.db.create_appointment(appointment_data)
                messagebox.showinfo("Success", "Appointment created successfully")

            # Close form and refresh list
            self._on_cancel_form()
            self.refresh_appointments()

        except Exception as e:
            logger.error(f"Error saving appointment: {e}")
            messagebox.showerror("Error", f"Error saving appointment: {str(e)}")

    def _on_cancel_form(self):
        """Handle cancel button click on form."""
        # Remove form
        if self.current_form:
            self.current_form.destroy()
            self.current_form = None

        # Show appointments list again
        self.appointments_list_frame.grid(row=0, column=0, sticky="nsew")