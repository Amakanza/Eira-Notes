import tkinter as tk
import customtkinter as ctk
import sqlite3
import datetime
from tkinter import messagebox

DB_PATH = "data/eira_notes.db"

class EditSoapNoteMixin:
    def show_edit_soap_note(self, note_id, patient_id):
        self.clear_content()

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM soap_notes WHERE id = ?", (note_id,))
        note = dict(cursor.fetchone())
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient = dict(cursor.fetchone())
        conn.close()

        soap_frame = ctk.CTkFrame(self.content_frame)
        soap_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        soap_frame.grid_columnconfigure(0, weight=1)
        self.current_frame = soap_frame

        title_label = ctk.CTkLabel(
            soap_frame,
            text=f"Edit SOAP Note for {patient['first_name']} {patient['last_name']}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        form_frame = ctk.CTkScrollableFrame(soap_frame, height=500)
        form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        form_frame.grid_columnconfigure(0, weight=1)

        date_frame = ctk.CTkFrame(form_frame)
        date_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        date_frame.grid_columnconfigure(1, weight=1)

        date_label = ctk.CTkLabel(date_frame, text="Date:")
        date_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        date_picker_frame = ctk.CTkFrame(date_frame)
        date_picker_frame.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        note_date = datetime.datetime.strptime(note['date'], '%Y-%m-%d')
        day_var = tk.StringVar(value=note_date.strftime('%d'))
        day_dropdown = ctk.CTkOptionMenu(date_picker_frame, variable=day_var, values=[str(i).zfill(2) for i in range(1, 32)])
        day_dropdown.grid(row=0, column=0, padx=2)

        month_var = tk.StringVar(value=note_date.strftime('%m'))
        month_dropdown = ctk.CTkOptionMenu(date_picker_frame, variable=month_var, values=[str(i).zfill(2) for i in range(1, 13)])
        month_dropdown.grid(row=0, column=1, padx=2)

        year_var = tk.StringVar(value=note_date.strftime('%Y'))
        year_dropdown = ctk.CTkOptionMenu(date_picker_frame, variable=year_var, values=[str(i) for i in range(note_date.year-5, note_date.year+1)])
        year_dropdown.grid(row=0, column=2, padx=2)

        soap_components = [
            {"label": "Subjective (Patient Report)", "field": "subjective"},
            {"label": "Objective (Measurements & Observations)", "field": "objective"},
            {"label": "Action (Treatment/Management)", "field": "action"},
            {"label": "Plan (Treatment Plan)", "field": "plan"}
        ]

        soap_textboxes = {}
        for i, comp in enumerate(soap_components):
            component_frame = ctk.CTkFrame(form_frame)
            component_frame.grid(row=i+1, column=0, padx=10, pady=10, sticky="ew")
            component_frame.grid_columnconfigure(0, weight=1)

            label = ctk.CTkLabel(component_frame, text=comp["label"], font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            textbox = ctk.CTkTextbox(component_frame, height=100, width=600)
            textbox.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
            textbox.insert("1.0", note[comp["field"]] or "")
            soap_textboxes[comp["field"]] = textbox

        additional_components = [
            {"label": "Treatment Provided", "field": "treatment_provided"},
            {"label": "Patient Response", "field": "patient_response"},
            {"label": "Goals & Progress", "field": "goals_progress"}
        ]

        additional_textboxes = {}
        for i, comp in enumerate(additional_components):
            component_frame = ctk.CTkFrame(form_frame)
            component_frame.grid(row=i+len(soap_components)+1, column=0, padx=10, pady=10, sticky="ew")
            component_frame.grid_columnconfigure(0, weight=1)

            label = ctk.CTkLabel(component_frame, text=comp["label"], font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            textbox = ctk.CTkTextbox(component_frame, height=80, width=600)
            textbox.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
            if note.get(comp["field"]):
                textbox.insert("1.0", note[comp["field"]])
            additional_textboxes[comp["field"]] = textbox

        error_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        error_label.grid(row=len(soap_components)+len(additional_components)+1, column=0, padx=10, pady=(10, 0))

        button_frame = ctk.CTkFrame(form_frame)
        button_frame.grid(row=len(soap_components)+len(additional_components)+2, column=0, padx=10, pady=20)

        def handle_save():
            for field, textbox in soap_textboxes.items():
                if textbox.get('1.0', 'end-1c').strip() == '':
                    error_label.configure(text=f"Please complete the {field.capitalize()} field")
                    return

            date_str = f"{year_var.get()}-{month_var.get()}-{day_var.get()}"

            soap_data = {
                'date': date_str,
                'subjective': soap_textboxes['subjective'].get('1.0', 'end-1c'),
                'objective': soap_textboxes['objective'].get('1.0', 'end-1c'),
                'action': soap_textboxes['action'].get('1.0', 'end-1c'),
                'plan': soap_textboxes['plan'].get('1.0', 'end-1c')
            }

            for field, textbox in additional_textboxes.items():
                text = textbox.get('1.0', 'end-1c').strip()
                if text:
                    soap_data[field] = text

            result = update_soap_note(note_id, soap_data)
            if result['success']:
                messagebox.showinfo('Success', result['message'])
                self.show_soap_note_details(note_id, patient_id)
            else:
                error_label.configure(text=result['message'])

        save_button = ctk.CTkButton(button_frame, text="Update SOAP Note", command=handle_save)
        save_button.grid(row=0, column=0, padx=10, pady=10)

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color="transparent",
            command=lambda: self.show_soap_note_details(note_id, patient_id)
        )
        cancel_button.grid(row=0, column=1, padx=10, pady=10)