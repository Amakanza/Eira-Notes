import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from app.app import EiraApp

logger = logging.getLogger(__name__)


class ReportForm(ctk.CTkFrame):
    """Form for generating reports."""

    def __init__(
        self,
        master,
        app: EiraApp,
        on_generate: Callable[[Dict[str, Any]], None],
        on_cancel: Callable[[], None],
        report_type: str = "clinical_note",
    ):
        super().__init__(master)
        self.master = master
        self.app = app
        self.on_generate = on_generate
        self.on_cancel = on_cancel
        self.report_type = report_type
        self.patients = []
        self.clinical_notes = []

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Form title
        title_text = self._get_title_for_report_type()
        self.title_label = ctk.CTkLabel(
            self,
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        # Load data for dropdowns
        self._load_data()

        # Create form fields based on report type
        self._create_form_fields()

    def _get_title_for_report_type(self) -> str:
        """Get title based on report type."""
        titles = {
            "clinical_note": "Generate Clinical Note Report",
            "patient_summary": "Generate Patient Summary Report",
            "appointment_schedule": "Generate Appointment Schedule Report",
            "custom": "Generate Custom Report",
        }
        return titles.get(self.report_type, "Generate Report")

    def _load_data(self):
        """Load data for dropdowns."""
        try:
            # Load patients
            self.patients = self.app.db.get_patients()

            # Load clinical notes if needed
            if self.report_type == "clinical_note":
                self.clinical_notes = self.app.db.get_clinical_notes(limit=100)
        except Exception as e:
            logger.error(f"Error loading data for report form: {e}")

    def _create_form_fields(self):
        """Create form fields based on report type."""
        self.fields = {}
        row = 1

        if self.report_type == "clinical_note":
            self._create_clinical_note_fields(row)
        elif self.report_type == "patient_summary":
            self._create_patient_summary_fields(row)
        elif self.report_type == "appointment_schedule":
            self._create_appointment_schedule_fields(row)
        elif self.report_type == "custom":
            self._create_custom_report_fields(row)

    def _create_clinical_note_fields(self, start_row: int):
        """Create fields for clinical note report."""
        row = start_row

        # Clinical note selection
        note_frame = ctk.CTkFrame(self, fg_color="transparent")
        note_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        note_label = ctk.CTkLabel(
            note_frame,
            text="Clinical Note",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        note_label.pack(anchor="w", padx=5, pady=(0, 5))

        # Create note dropdown
        self.note_var = tk.StringVar()
        self.fields["note"] = ctk.CTkOptionMenu(
            note_frame,
            values=self._get_note_display_names(),
            variable=self.note_var,
            width=400,
            dynamic_resizing=False,
        )
        self.fields["note"].pack(anchor="w", padx=5, fill="x")

        row += 1

        # Format selection
        format_frame = ctk.CTkFrame(self, fg_color="transparent")
        format_frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")

        format_label = ctk.CTkLabel(
            format_frame,
            text="Output Format",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        format_label.pack(anchor="w", padx=5, pady=(0, 5))

        # Create format dropdown
        formats = ["PDF", "DOCX", "HTML"]
        self.format_var = tk.StringVar(value="PDF")
        self.fields["format"] = ctk.CTkOptionMenu(
            format_frame,
            values=formats,
            variable=self.format_var,
            width=200,
        )
        self.fields["format"].pack(anchor="w", padx=5)

        # Template selection
        template_frame = ctk.CTkFrame(self, fg_color="transparent")
        template_frame.grid(row=row, column=1, padx=10, pady=10, sticky="ew")

        template_label = ctk.CTkLabel(
            template_frame,
            text="Template",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        template_label.pack(anchor="w", padx=5, pady=(0, 5))

        # Create template dropdown
        templates = ["Standard", "Detailed", "Minimal"]
        self.template_var = tk.StringVar(value="Standard")
        self.fields["template"] = ctk.CTkOptionMenu(
            template_frame,
            values=templates,
            variable=self.template_var,
            width=200,
        )
        self.fields["template"].pack(anchor="w", padx=5)

        row += 1

        # Include signature checkbox
        signature_frame = ctk.CTkFrame(self, fg_color="transparent")
        signature_frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")

        self.signature_var = tk.BooleanVar(value=True)
        self.fields["include_signature"] = ctk.CTkCheckBox(
            signature_frame,
            text="Include Digital Signature",
            variable=self.signature_var,
            onvalue=True,
            offvalue=False,
        )
        self.fields["include_signature"].pack(anchor="w", padx=5)

        # Include letterhead checkbox
        letterhead_frame = ctk.CTkFrame(self, fg_color="transparent")
        letterhead_frame.grid(row=row, column=1, padx=10, pady=10, sticky="ew")

        self.letterhead_var = tk.BooleanVar(value=True)
        self.fields["include_letterhead"] = ctk.CTkCheckBox(
            letterhead_frame,
            text="Include Letterhead",
            variable=self.letterhead_var,
            onvalue=True,
            offvalue=False,
        )
        self.fields["include_letterhead"].pack(anchor="w", padx=5)

        row += 1

        # Buttons
        self._add_buttons(row)

    def _create_patient_summary_fields(self, start_row: int):
        """Create fields for patient summary report."""
        row = start_row

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
            width=400,
            dynamic_resizing=False,
        )
        self.fields["patient"].pack(anchor="w", padx=5, fill="x")

        row += 1

        # Date range
        date_range_frame = ctk.CTkFrame(self, fg_color="transparent")
        date_range_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        date_range_label = ctk.CTkLabel(
            date_range_frame,
            text="Date Range",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        date_range_label.pack(anchor="w", padx=5, pady=(0, 5))

        date_range_inner_frame = ctk.CTkFrame(date_range_frame, fg_color="transparent")
        date_range_inner_frame.pack(fill="x", padx=5)

        # Start date
        start_date_label = ctk.CTkLabel(
            date_range_inner_frame,
            text="From:",
            width=50,
        )
        start_date_label.pack(side="left")

        self.fields["start_date"] = ctk.CTkEntry(date_range_inner_frame, width=120)
        self.fields["start_date"].pack(side="left", padx=(0, 20))
        # Set default to 1 year ago
        one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        self.fields["start_date"].insert(0, one_year_ago)

        # End date
        end_date_label = ctk.CTkLabel(
            date_range_inner_frame,
            text="To:",
            width=30,
        )
        end_date_label.pack(side="left")

        self.fields["end_date"] = ctk.CTkEntry(date_range_inner_frame, width=120)
        self.fields["end_date"].pack(side="left")
        # Set default to today
        today = datetime.now().strftime("%Y-%m-%d")
        self.fields["end_date"].insert(0, today)

        row += 1

        # Include sections
        sections_frame = ctk.CTkFrame(self, fg_color="transparent")
        sections_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        sections_label = ctk.CTkLabel(
            sections_frame,
            text="Include Sections",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        sections_label.pack(anchor="w", padx=5, pady=(0, 5))

        sections_inner_frame = ctk.CTkFrame(sections_frame, fg_color="transparent")
        sections_inner_frame.pack(fill="x", padx=5)

        # Checkboxes for sections
        self.demographics_var = tk.BooleanVar(value=True)
        self.fields["include_demographics"] = ctk.CTkCheckBox(
            sections_inner_frame,
            text="Demographics",
            variable=self.demographics_var,
            onvalue=True,
            offvalue=False,
        )
        self.fields["include_demographics"].pack(side="left", padx=(0, 10))

        self.medical_history_var = tk.BooleanVar(value=True)
        self.fields["include_medical_history"] = ctk.CTkCheckBox(
            sections_inner_frame,
            text="Medical History",
            variable=self.medical_history_var,
            onvalue=True,
            offvalue=False,
        )
        self.fields["include_medical_history"].pack(side="left", padx=10)

        self.appointments_var = tk.BooleanVar(value=True)
        self.fields["include_appointments"] = ctk.CTkCheckBox(
            sections_inner_frame,
            text="Appointments",
            variable=self.appointments_var,
            onvalue=True,
            offvalue=False,
        )
        self.fields["include_appointments"].pack(side="left", padx=10)

        self.notes_var = tk.BooleanVar(value=True)
        self.fields["include_notes"] = ctk.CTkCheckBox(
            sections_inner_frame,
            text="Clinical Notes",
            variable=self.notes_var,
            onvalue=True,
            offvalue=False,
        )
        self.fields["include_notes"].pack(side="left", padx=10)

        row += 1

        # Format selection
        format_frame = ctk.CTkFrame(self, fg_color="transparent")
        format_frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")

        format_label = ctk.CTkLabel(
            format_frame,
            text="Output Format",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        format_label.pack(anchor="w", padx=5, pady=(0, 5))

        # Create format dropdown
        formats = ["PDF", "DOCX", "HTML"]
        self.format_var = tk.StringVar(value="PDF")
        self.fields["format"] = ctk.CTkOptionMenu(
            format_frame,
            values=formats,
            variable=self.format_var,
            width=200,
        )
        self.fields["format"].pack(anchor="w", padx=5)

        row += 1

        # Buttons
        self._add_buttons(row)

    def _create_appointment_schedule_fields(self, start_row: int):
        """Create fields for appointment schedule report."""
        row = start_row

        # Date range
        date_range_frame = ctk.CTkFrame(self, fg_color="transparent")
        date_range_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        date_range_label = ctk.CTkLabel(
            date_range_frame,
            text="Date Range",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        date_range_label.pack(anchor="w", padx=5, pady=(0, 5))

        date_range_inner_frame = ctk.CTkFrame(date_range_frame, fg_color="transparent")
        date_range_inner_frame.pack(fill="x", padx=5)

        # Start date
        start_date_label = ctk.CTkLabel(
            date_range_inner_frame,
            text="From:",
            width=50,
        )
        start_date_label.pack(side="left")

        self.fields["start_date"] = ctk.CTkEntry(date_range_inner_frame, width=120)
        self.fields["start_date"].pack(side="left", padx=(0, 20))
        # Set default to today
        today = datetime.now().strftime("%Y-%m-%d")
        self.fields["start_date"].insert(0, today)

        # End date
        end_date_label = ctk.CTkLabel(
            date_range_inner_frame,
            text="To:",
            width=30,
        )
        end_date_label.pack(side="left")

        self.fields["end_date"] = ctk.CTkEntry(date_range_inner_frame, width=120)
        self.fields["end_date"].pack(side="left")
        # Set default to 1 week from today
        one_week_later = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        self.fields["end_date"].insert(0, one_week_later)

        row += 1

        # Group by options
        group_frame = ctk.CTkFrame(self, fg_color="transparent")
        group_frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")

        group_label = ctk.CTkLabel(
            group_frame,
            text="Group By",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        group_label.pack(anchor="w", padx=5, pady=(0, 5))

        # Create group dropdown
        groups = ["Day", "Week", "Patient", "Type"]
        self.group_var = tk.StringVar(value="Day")
        self.fields["group_by"] = ctk.CTkOptionMenu(
            group_frame,
            values=groups,
            variable=self.group_var,
            width=200,
        )
        self.fields["group_by"].pack(anchor="w", padx=5)

        # Filter options
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.grid(row=row, column=1, padx=10, pady=10, sticky="ew")

        filter_label = ctk.CTkLabel(
            filter_frame,
            text="Filter Status",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        filter_label.pack(anchor="w", padx=5, pady=(0, 5))

        # Create filter dropdown
        filters = ["All", "Scheduled", "Confirmed", "Completed", "Cancelled"]
        self.filter_var = tk.StringVar(value="All")
        self.fields["status_filter"] = ctk.CTkOptionMenu(
            filter_frame,
            values=filters,
            variable=self.filter_var,
            width=200,
        )
        self.fields["status_filter"].pack(anchor="w", padx=5)

        row += 1

        # Format selection
        format_frame = ctk.CTkFrame(self, fg_color="transparent")
        format_frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")

        format_label = ctk.CTkLabel(
            format_frame,
            text="Output Format",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        format_label.pack(anchor="w", padx=5, pady=(0, 5))

        # Create format dropdown
        formats = ["PDF", "DOCX", "HTML", "CSV"]
        self.format_var = tk.StringVar(value="PDF")
        self.fields["format"] = ctk.CTkOptionMenu(
            format_frame,
            values=formats,
            variable=self.format_var,
            width=200,
        )
        self.fields["format"].pack(anchor="w", padx=5)

        row += 1

        # Buttons
        self._add_buttons(row)

    def _create_custom_report_fields(self, start_row: int):
        """Create fields for custom report."""
        row = start_row

        # Report title
        self.fields["title"] = self._create_field(
            "Report Title", row, 0, "Custom Report", columnspan=2
        )
        row += 1

        # Report description
        description_frame = ctk.CTkFrame(self, fg_color="transparent")
        description_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        description_label = ctk.CTkLabel(
            description_frame,
            text="Report Description",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        description_label.pack(anchor="w", padx=5, pady=(0, 5))

        self.fields["description"] = ctk.CTkTextbox(
            description_frame,
            height=60,
            width=400,
        )
        self.fields["description"].pack(fill="x", padx=5)

        row += 1

        # Data selection
        data_frame = ctk.CTkFrame(self, fg_color="transparent")
        data_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        data_label = ctk.CTkLabel(
            data_frame,
            text="Include Data",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        data_label.pack(anchor="w", padx=5, pady=(0, 5))

        data_inner_frame = ctk.CTkFrame(data_frame, fg_color="transparent")
        data_inner_frame.pack(fill="x", padx=5)

        # Checkboxes for data types
        self.patients_var = tk.BooleanVar(value=True)
        self.fields["include_patients"] = ctk.CTkCheckBox(
            data_inner_frame,
            text="Patients",
            variable=self.patients_var,
            onvalue=True,
            offvalue=False,
        )
        self.fields["include_patients"].pack(side="left", padx=(0, 10))

        self.appointments_var = tk.BooleanVar(value=True)
        self.fields["include_appointments"] = ctk.CTkCheckBox(
            data_inner_frame,
            text="Appointments",
            variable=self.appointments_var,
            onvalue=True,
            offvalue=False,
        )
        self.fields["include_appointments"].pack(side="left", padx=10)

        self.notes_var = tk.BooleanVar(value=True)
        self.fields["include_notes"] = ctk.CTkCheckBox(
            data_inner_frame,
            text="Clinical Notes",
            variable=self.notes_var,
            onvalue=True,
            offvalue=False,
        )
        self.fields["include_notes"].pack(side="left", padx=10)

        row += 1

        # Date range
        date_range_frame = ctk.CTkFrame(self, fg_color="transparent")
        date_range_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        date_range_label = ctk.CTkLabel(
            date_range_frame,
            text="Date Range",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        date_range_label.pack(anchor="w", padx=5, pady=(0, 5))

        date_range_inner_frame = ctk.CTkFrame(date_range_frame, fg_color="transparent")
        date_range_inner_frame.pack(fill="x", padx=5)

        # Start date
        start_date_label = ctk.CTkLabel(
            date_range_inner_frame,
            text="From:",
            width=50,
        )
        start_date_label.pack(side="left")

        self.fields["start_date"] = ctk.CTkEntry(date_range_inner_frame, width=120)
        self.fields["start_date"].pack(side="left", padx=(0, 20))
        # Set default to 1 month ago
        one_month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        self.fields["start_date"].insert(0, one_month_ago)

        # End date
        end_date_label = ctk.CTkLabel(
            date_range_inner_frame,
            text="To:",
            width=30,
        )
        end_date_label.pack(side="left")

        self.fields["end_date"] = ctk.CTkEntry(date_range_inner_frame, width=120)
        self.fields["end_date"].pack(side="left")
        # Set default to today
        today = datetime.now().strftime("%Y-%m-%d")
        self.fields["end_date"].insert(0, today)

        row += 1

        # Format selection
        format_frame = ctk.CTkFrame(self, fg_color="transparent")
        format_frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")

        format_label = ctk.CTkLabel(
            format_frame,
            text="Output Format",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        format_label.pack(anchor="w", padx=5, pady=(0, 5))

        # Create format dropdown
        formats = ["PDF", "DOCX", "HTML", "CSV", "Excel"]
        self.format_var = tk.StringVar(value="PDF")
        self.fields["format"] = ctk.CTkOptionMenu(
            format_frame,
            values=formats,
            variable=self.format_var,
            width=200,
        )
        self.fields["format"].pack(anchor="w", padx=5)

        row += 1

        # Buttons
        self._add_buttons(row)

    def _add_buttons(self, row: int):
        """Add form buttons."""
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

        generate_button = ctk.CTkButton(
            buttons_frame,
            text="Generate Report",
            command=self._on_generate_click,
            width=150,
        )
        generate_button.pack(side="left", padx=5)

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

    def _get_patient_display_names(self) -> List[str]:
        """Get patient display names for dropdown."""
        if not self.patients:
            return ["No patients available"]

        return [
            f"{p.get('first_name', '')} {p.get('last_name', '')} (ID: {p.get('id', '')})" 
            for p in self.patients
        ]

    def _get_note_display_names(self) -> List[str]:
        """Get clinical note display names for dropdown."""
        if not self.clinical_notes:
            return ["No clinical notes available"]

        result = []
        for note in self.clinical_notes:
            # Try to get patient name
            patient_name = "Unknown Patient"
            patient_id = note.get("patient_id")
            if patient_id:
                for patient in self.patients:
                    if patient.get("id") == patient_id:
                        patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}"
                        break

            # Format date if available
            date_str = note.get("created_at", "")
            if date_str:
                try:
                    date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    date_display = date_obj.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    date_display = date_str
            else:
                date_display = "Unknown date"

            # Create display name
            display_name = f"{date_display} - {patient_name} - {note.get('title', 'No title')} (ID: {note.get('id', '')})" 
            result.append(display_name)

        return result

    def _get_patient_id_from_selection(self) -> Optional[str]:
        """Extract patient ID from the selected dropdown value."""
        selection = self.patient_var.get() if hasattr(self, "patient_var") else ""
        if "ID:" not in selection:
            return None

        try:
            # Extract ID from format "Name (ID: XXX)"
            id_part = selection.split("ID:")[-1].strip()
            return id_part.rstrip(")")
        except Exception:
            return None

    def _get_note_id_from_selection(self) -> Optional[str]:
        """Extract note ID from the selected dropdown value."""
        selection = self.note_var.get() if hasattr(self, "note_var") else ""
        if "ID:" not in selection:
            return None

        try:
            # Extract ID from format "Date - Patient - Title (ID: XXX)"
            id_part = selection.split("ID:")[-1].strip()
            return id_part.rstrip(")")
        except Exception:
            return None

    def _on_generate_click(self):
        """Handle generate button click."""
        # Validate form
        if not self._validate_form():
            return

        # Collect form data based on report type
        report_data = {"type": self.report_type}

        if self.report_type == "clinical_note":
            report_data.update({
                "note_id": self._get_note_id_from_selection(),
                "format": self.format_var.get(),
                "template": self.template_var.get(),
                "include_signature": self.signature_var.get(),
                "include_letterhead": self.letterhead_var.get(),
            })
        elif self.report_type == "patient_summary":
            report_data.update({
                "patient_id": self._get_patient_id_from_selection(),
                "start_date": self.fields["start_date"].get(),
                "end_date": self.fields["end_date"].get(),
                "format": self.format_var.get(),
                "include_demographics": self.demographics_var.get(),
                "include_medical_history": self.medical_history_var.get(),
                "include_appointments": self.appointments_var.get(),
                "include_notes": self.notes_var.get(),
            })
        elif self.report_type == "appointment_schedule":
            report_data.update({
                "start_date": self.fields["start_date"].get(),
                "end_date": self.fields["end_date"].get(),
                "format": self.format_var.get(),
                "group_by": self.group_var.get(),
                "status_filter": self.filter_var.get(),
            })
        elif self.report_type == "custom":
            report_data.update({
                "title": self.fields["title"].get(),
                "description": self.fields["description"].get("0.0", "end").strip(),
                "start_date": self.fields["start_date"].get(),
                "end_date": self.fields["end_date"].get(),
                "format": self.format_var.get(),
                "include_patients": self.patients_var.get(),
                "include_appointments": self.appointments_var.get(),
                "include_notes": self.notes_var.get(),
            })

        # Call generate callback
        self.on_generate(report_data)

    def _validate_form(self) -> bool:
        """Validate form fields."""
        if self.report_type == "clinical_note":
            # Check note selection
            note_id = self._get_note_id_from_selection()
            if not note_id:
                messagebox.showerror("Validation Error", "Please select a clinical note")
                return False

        elif self.report_type == "patient_summary":
            # Check patient selection
            patient_id = self._get_patient_id_from_selection()
            if not patient_id:
                messagebox.showerror("Validation Error", "Please select a patient")
                return False

            # Check date format
            if not self._validate_date_range():
                return False

        elif self.report_type == "appointment_schedule" or self.report_type == "custom":
            # Check date format
            if not self._validate_date_range():
                return False

        return True

    def _validate_date_range(self) -> bool:
        """Validate date range fields."""
        # Check start date format
        start_date = self.fields["start_date"].get()
        if not start_date or not self._is_valid_date(start_date):
            messagebox.showerror(
                "Validation Error", "Start date must be in YYYY-MM-DD format"
            )
            return False

        # Check end date format
        end_date = self.fields["end_date"].get()
        if not end_date or not self._is_valid_date(end_date):
            messagebox.showerror(
                "Validation Error", "End date must be in YYYY-MM-DD format"
            )
            return False

        # Check that end date is after start date
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            if end < start:
                messagebox.showerror(
                    "Validation Error", "End date must be after start date"
                )
                return False
        except ValueError:
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


class ReportsView(ctk.CTkFrame):
    """Reports view for the Eira desktop application."""

    def __init__(self, master, app: EiraApp):
        super().__init__(master)
        self.master = master
        self.app = app
        self.current_form = None
        self.current_report_type = "clinical_note"

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create top bar with report type selection
        self._create_top_bar()

        # Create reports list
        self._create_reports_list()

        # Load reports
        self.refresh_reports()

    def _create_top_bar(self):
        """Create top bar with report type selection and generate button."""
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        top_bar.grid_columnconfigure(0, weight=1)

        # Report type selection
        report_type_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        report_type_frame.pack(side="left", fill="x", expand=True)

        report_type_label = ctk.CTkLabel(
            report_type_frame,
            text="Report Type:",
            font=ctk.CTkFont(size=14),
        )
        report_type_label.pack(side="left", padx=(0, 10))

        # Create report type dropdown
        report_types = [
            "Clinical Note",
            "Patient Summary",
            "Appointment Schedule",
            "Custom Report",
        ]
        self.report_type_var = tk.StringVar(value="Clinical Note")
        report_type_dropdown = ctk.CTkOptionMenu(
            report_type_frame,
            values=report_types,
            variable=self.report_type_var,
            command=self._on_report_type_change,
            width=200,
        )
        report_type_dropdown.pack(side="left")

        # Generate button
        generate_button = ctk.CTkButton(
            top_bar,
            text="+ Generate Report",
            width=150,
            command=self._on_generate_report,
        )
        generate_button.pack(side="right")

    def _create_reports_list(self):
        """Create reports list."""
        # Container frame for list or form
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Reports list frame
        self.reports_list_frame = ctk.CTkScrollableFrame(self.content_frame)
        self.reports_list_frame.grid(row=0, column=0, sticky="nsew")

    def refresh_reports(self):
        """Refresh reports list."""
        # Clear existing list
        for widget in self.reports_list_frame.winfo_children():
            widget.destroy()

        try:
            # Map report type selection to API filter
            report_type_map = {
                "Clinical Note": "clinical_note",
                "Patient Summary": "patient_summary",
                "Appointment Schedule": "appointment_schedule",
                "Custom Report": "custom",
            }
            report_type = report_type_map.get(self.report_type_var.get(), "")
            self.current_report_type = report_type

            # Get reports from database
            filters = {}
            if report_type:
                filters["type"] = report_type

            reports = self.app.db.get_reports(filters=filters, order_by="-created_at")

            if not reports:
                no_data_label = ctk.CTkLabel(
                    self.reports_list_frame,
                    text=f"No {self.report_type_var.get()} reports found",
                    font=ctk.CTkFont(size=14),
                    text_color="gray",
                )
                no_data_label.pack(pady=20)
                return

            # Create header row
            header_frame = ctk.CTkFrame(self.reports_list_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=(5, 10))

            headers = ["Date", "Title", "Format", "Status", "Actions"]
            widths = [150, 300, 80, 100, 150]

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
            separator = ctk.CTkFrame(self.reports_list_frame, height=1, fg_color="gray")
            separator.pack(fill="x", padx=10, pady=5)

            # Add report rows
            for report in reports:
                self._add_report_row(report)

        except Exception as e:
            logger.error(f"Error loading reports: {e}")
            error_label = ctk.CTkLabel(
                self.reports_list_frame,
                text=f"Error loading reports: {str(e)}",
                font=ctk.CTkFont(size=14),
                text_color="red",
            )
            error_label.pack(pady=20)

    def _add_report_row(self, report: Dict[str, Any]):
        """Add a report row to the list."""
        row_frame = ctk.CTkFrame(self.reports_list_frame, fg_color="transparent")
        row_frame.pack(fill="x", padx=10, pady=5)

        # Date
        date_str = report.get("created_at", "")
        date_display = "Unknown"
        if date_str:
            try:
                date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                date_display = date_obj.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                date_display = date_str

        date_label = ctk.CTkLabel(
            row_frame,
            text=date_display,
            font=ctk.CTkFont(size=14),
            width=150,
            anchor="w",
        )
        date_label.pack(side="left", padx=5)

        # Title
        title = report.get("title", "Untitled Report")
        title_label = ctk.CTkLabel(
            row_frame,
            text=title,
            font=ctk.CTkFont(size=14),
            width=300,
            anchor="w",
        )
        title_label.pack(side="left", padx=5)

        # Format
        format_label = ctk.CTkLabel(
            row_frame,
            text=report.get("format", "PDF").upper(),
            font=ctk.CTkFont(size=14),
            width=80,
            anchor="w",
        )
        format_label.pack(side="left", padx=5)

        # Status
        status = report.get("status", "completed")
        status_color = "green" if status == "completed" else "orange"
        status_label = ctk.CTkLabel(
            row_frame,
            text=status.capitalize(),
            font=ctk.CTkFont(size=14),
            text_color=status_color,
            width=100,
            anchor="w",
        )
        status_label.pack(side="left", padx=5)

        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=150)
        actions_frame.pack(side="left", padx=5)

        download_button = ctk.CTkButton(
            actions_frame,
            text="Download",
            width=80,
            height=24,
            font=ctk.CTkFont(size=12),
            command=lambda r=report: self._on_download_report(r),
        )
        download_button.pack(side="left", padx=(0, 5))

        delete_button = ctk.CTkButton(
            actions_frame,
            text="Delete",
            width=60,
            height=24,
            font=ctk.CTkFont(size=12),
            fg_color="red",
            command=lambda r=report: self._on_delete_report(r),
        )
        delete_button.pack(side="left")

    def _on_report_type_change(self, value):
        """Handle report type change."""
        self.refresh_reports()

    def _on_generate_report(self):
        """Handle generate report button click."""
        # Hide reports list
        self.reports_list_frame.grid_forget()

        # Map report type selection to API filter
        report_type_map = {
            "Clinical Note": "clinical_note",
            "Patient Summary": "patient_summary",
            "Appointment Schedule": "appointment_schedule",
            "Custom Report": "custom",
        }
        report_type = report_type_map.get(self.report_type_var.get(), "clinical_note")

        # Create and show report form
        self.current_form = ReportForm(
            self.content_frame,
            self.app,
            on_generate=self._on_save_report,
            on_cancel=self._on_cancel_form,
            report_type=report_type,
        )
        self.current_form.grid(row=0, column=0, sticky="nsew")

    def _on_download_report(self, report: Dict[str, Any]):
        """Handle download report button click."""
        report_id = report.get("id")
        if not report_id:
            return

        try:
            # Get download URL from API
            download_url = self.app.api_client.get_report_download_url(report_id)

            if download_url:
                # Open download URL in browser
                import webbrowser
                webbrowser.open(download_url)
                messagebox.showinfo("Success", "Report download started in your browser")
            else:
                messagebox.showerror("Error", "Could not get download URL for report")

        except Exception as e:
            logger.error(f"Error downloading report: {e}")
            messagebox.showerror("Error", f"Error downloading report: {str(e)}")

    def _on_delete_report(self, report: Dict[str, Any]):
        """Handle delete report button click."""
        report_id = report.get("id")
        if not report_id:
            return

        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to delete this report?",
        )
        if not confirm:
            return

        try:
            # Delete report
            self.app.db.delete_report(report_id)
            messagebox.showinfo("Success", "Report deleted successfully")
            self.refresh_reports()
        except Exception as e:
            logger.error(f"Error deleting report: {e}")
            messagebox.showerror("Error", f"Error deleting report: {str(e)}")

    def _on_save_report(self, report_data: Dict[str, Any]):
        """Handle save report from form."""
        try:
            # Generate report
            result = self.app.api_client.generate_report(report_data)

            if result and result.get("id"):
                messagebox.showinfo(
                    "Success",
                    "Report generation started. It will appear in the list when complete.",
                )
            else:
                messagebox.showwarning(
                    "Warning",
                    "Report request submitted, but no confirmation received.",
                )

            # Close form and refresh list
            self._on_cancel_form()
            self.refresh_reports()

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            messagebox.showerror("Error", f"Error generating report: {str(e)}")

    def _on_cancel_form(self):
        """Handle cancel button click on form."""
        # Remove form
        if self.current_form:
            self.current_form.destroy()
            self.current_form = None

        # Show reports list again
        self.reports_list_frame.grid(row=0, column=0, sticky="nsew")


from datetime import timedelta  # Import needed for date calculations