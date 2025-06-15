import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

import customtkinter as ctk
import tkinter as tk

from app.app import EiraApp

logger = logging.getLogger(__name__)


class DashboardView(ctk.CTkFrame):
    """Dashboard view for the Eira desktop application."""

    def __init__(self, master, app: EiraApp):
        super().__init__(master)
        self.master = master
        self.app = app

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create dashboard widgets
        self._create_stats_cards()
        self._create_recent_patients()
        self._create_upcoming_appointments()

        # Load data
        self.refresh_data()

    def _create_stats_cards(self):
        """Create statistics cards."""
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.grid(
            row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew"
        )
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Patients card
        self.patients_card = self._create_stat_card(
            self.stats_frame, "Total Patients", "0", 0
        )

        # Appointments card
        self.appointments_card = self._create_stat_card(
            self.stats_frame, "Today's Appointments", "0", 1
        )

        # Notes card
        self.notes_card = self._create_stat_card(
            self.stats_frame, "Recent Notes", "0", 2
        )

        # Pending sync card
        self.sync_card = self._create_stat_card(
            self.stats_frame, "Pending Sync", "0", 3
        )

    def _create_stat_card(self, parent, title: str, value: str, column: int):
        """Create a single statistic card."""
        card = ctk.CTkFrame(parent)
        card.grid(row=0, column=column, padx=10, pady=10, sticky="ew")

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14),
        )
        title_label.pack(padx=10, pady=(10, 5))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        value_label.pack(padx=10, pady=(0, 10))

        return {"frame": card, "title": title_label, "value": value_label}

    def _create_recent_patients(self):
        """Create recent patients list."""
        self.patients_frame = ctk.CTkFrame(self)
        self.patients_frame.grid(
            row=1, column=0, padx=20, pady=(0, 20), sticky="nsew"
        )

        # Title
        patients_title = ctk.CTkLabel(
            self.patients_frame,
            text="Recent Patients",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        patients_title.pack(padx=15, pady=15, fill="x")

        # Patients list
        self.patients_list = ctk.CTkScrollableFrame(self.patients_frame)
        self.patients_list.pack(padx=15, pady=(0, 15), fill="both", expand=True)

        # Add "View All" button
        view_all_patients = ctk.CTkButton(
            self.patients_frame,
            text="View All Patients",
            command=self._on_view_all_patients,
        )
        view_all_patients.pack(padx=15, pady=(0, 15), fill="x")

    def _create_upcoming_appointments(self):
        """Create upcoming appointments list."""
        self.appointments_frame = ctk.CTkFrame(self)
        self.appointments_frame.grid(
            row=1, column=1, padx=20, pady=(0, 20), sticky="nsew"
        )

        # Title
        appointments_title = ctk.CTkLabel(
            self.appointments_frame,
            text="Upcoming Appointments",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        appointments_title.pack(padx=15, pady=15, fill="x")

        # Appointments list
        self.appointments_list = ctk.CTkScrollableFrame(self.appointments_frame)
        self.appointments_list.pack(padx=15, pady=(0, 15), fill="both", expand=True)

        # Add "View All" button
        view_all_appointments = ctk.CTkButton(
            self.appointments_frame,
            text="View All Appointments",
            command=self._on_view_all_appointments,
        )
        view_all_appointments.pack(padx=15, pady=(0, 15), fill="x")

    def refresh_data(self):
        """Refresh all dashboard data."""
        try:
            # Update statistics
            self._update_statistics()

            # Update recent patients
            self._update_recent_patients()

            # Update upcoming appointments
            self._update_upcoming_appointments()

        except Exception as e:
            logger.error(f"Error refreshing dashboard data: {e}")

    def _update_statistics(self):
        """Update statistics cards with current data."""
        try:
            # Get total patients count
            patients_count = len(self.app.db.get_patients())
            self.patients_card["value"].configure(text=str(patients_count))

            # Get today's appointments count
            today = datetime.now().date()
            today_str = today.isoformat()
            tomorrow_str = (today + timedelta(days=1)).isoformat()
            appointments = self.app.db.get_appointments(
                filters={"date_gte": today_str, "date_lt": tomorrow_str}
            )
            self.appointments_card["value"].configure(text=str(len(appointments)))

            # Get recent notes count (last 7 days)
            week_ago_str = (today - timedelta(days=7)).isoformat()
            notes = self.app.db.get_clinical_notes(
                filters={"created_at_gte": week_ago_str}
            )
            self.notes_card["value"].configure(text=str(len(notes)))

            # Get pending sync count
            pending_changes = self.app.db.get_pending_changes()
            self.sync_card["value"].configure(text=str(len(pending_changes)))

        except Exception as e:
            logger.error(f"Error updating statistics: {e}")

    def _update_recent_patients(self):
        """Update recent patients list."""
        try:
            # Clear existing items
            for widget in self.patients_list.winfo_children():
                widget.destroy()

            # Get recent patients (limit to 10)
            patients = self.app.db.get_patients(limit=10, order_by="-updated_at")

            if not patients:
                no_data_label = ctk.CTkLabel(
                    self.patients_list,
                    text="No patients found",
                    font=ctk.CTkFont(size=12),
                    text_color="gray",
                )
                no_data_label.pack(pady=10)
                return

            # Add patient items
            for patient in patients:
                self._add_patient_item(patient)

        except Exception as e:
            logger.error(f"Error updating recent patients: {e}")
            error_label = ctk.CTkLabel(
                self.patients_list,
                text=f"Error loading patients: {str(e)}",
                font=ctk.CTkFont(size=12),
                text_color="red",
            )
            error_label.pack(pady=10)

    def _add_patient_item(self, patient: Dict[str, Any]):
        """Add a patient item to the recent patients list."""
        item_frame = ctk.CTkFrame(self.patients_list, fg_color="transparent")
        item_frame.pack(fill="x", pady=5)

        # Patient name
        name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}"
        name_label = ctk.CTkLabel(
            item_frame,
            text=name,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        name_label.pack(side="left", padx=5, fill="x", expand=True)

        # Patient ID
        id_label = ctk.CTkLabel(
            item_frame,
            text=f"ID: {patient.get('id', 'N/A')}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        id_label.pack(side="left", padx=5)

        # View button
        view_button = ctk.CTkButton(
            item_frame,
            text="View",
            width=60,
            height=24,
            font=ctk.CTkFont(size=12),
            command=lambda p=patient: self._on_view_patient(p),
        )
        view_button.pack(side="right", padx=5)

    def _update_upcoming_appointments(self):
        """Update upcoming appointments list."""
        try:
            # Clear existing items
            for widget in self.appointments_list.winfo_children():
                widget.destroy()

            # Get upcoming appointments (limit to 10)
            today = datetime.now().date().isoformat()
            appointments = self.app.db.get_appointments(
                filters={"date_gte": today},
                limit=10,
                order_by="date",
            )

            if not appointments:
                no_data_label = ctk.CTkLabel(
                    self.appointments_list,
                    text="No upcoming appointments",
                    font=ctk.CTkFont(size=12),
                    text_color="gray",
                )
                no_data_label.pack(pady=10)
                return

            # Add appointment items
            for appointment in appointments:
                self._add_appointment_item(appointment)

        except Exception as e:
            logger.error(f"Error updating upcoming appointments: {e}")
            error_label = ctk.CTkLabel(
                self.appointments_list,
                text=f"Error loading appointments: {str(e)}",
                font=ctk.CTkFont(size=12),
                text_color="red",
            )
            error_label.pack(pady=10)

    def _add_appointment_item(self, appointment: Dict[str, Any]):
        """Add an appointment item to the upcoming appointments list."""
        item_frame = ctk.CTkFrame(self.appointments_list, fg_color="transparent")
        item_frame.pack(fill="x", pady=5)

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

        # Date and time
        date_str = appointment.get("date", "")
        time_str = appointment.get("time", "")
        date_time = f"{date_str} {time_str}"

        # Date/time label
        date_label = ctk.CTkLabel(
            item_frame,
            text=date_time,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100,
            anchor="w",
        )
        date_label.pack(side="left", padx=5)

        # Patient name
        name_label = ctk.CTkLabel(
            item_frame,
            text=patient_name,
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        name_label.pack(side="left", padx=5, fill="x", expand=True)

        # View button
        view_button = ctk.CTkButton(
            item_frame,
            text="View",
            width=60,
            height=24,
            font=ctk.CTkFont(size=12),
            command=lambda a=appointment: self._on_view_appointment(a),
        )
        view_button.pack(side="right", padx=5)

    def _on_view_patient(self, patient: Dict[str, Any]):
        """Handle view patient button click."""
        # This would be implemented to navigate to patient detail view
        logger.info(f"View patient: {patient.get('id')}")
        # Placeholder for navigation to patient detail
        # self.master.show_patient_detail(patient.get('id'))

    def _on_view_appointment(self, appointment: Dict[str, Any]):
        """Handle view appointment button click."""
        # This would be implemented to navigate to appointment detail view
        logger.info(f"View appointment: {appointment.get('id')}")
        # Placeholder for navigation to appointment detail
        # self.master.show_appointment_detail(appointment.get('id'))

    def _on_view_all_patients(self):
        """Handle view all patients button click."""
        # This would be implemented to navigate to patients list view
        logger.info("View all patients")
        # Placeholder for navigation to patients list
        # self.master.show_view('patients')

    def _on_view_all_appointments(self):
        """Handle view all appointments button click."""
        # This would be implemented to navigate to appointments list view
        logger.info("View all appointments")
        # Placeholder for navigation to appointments list
        # self.master.show_view('appointments')