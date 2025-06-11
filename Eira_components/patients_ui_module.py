# File: Eira_components/patients.py
import datetime
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

from .database import get_patients as db_get_patients, get_patient as db_get_patient, add_patient as db_add_patient, update_patient as db_update_patient, delete_patient as db_delete_patient

# UI functions for Patients section

def show_patients(app):
    app.clear_content()
    # Create patients frame
    patients_frame = ctk.CTkFrame(app.content_frame)
    patients_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    patients_frame.grid_columnconfigure(0, weight=1)

    # Header with title and Add button
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
        command=lambda: show_add_patient(app)
    )
    add_button.grid(row=0, column=1, padx=20, pady=10)

    # Retrieve and display patients list
    patients = db_get_patients(app.current_user["id"])
    list_frame = ctk.CTkFrame(patients_frame)
    list_frame.grid(row=1, column=0, padx=20, pady=(0,20), sticky="nsew")
    list_frame.grid_columnconfigure(0, weight=1)

    scrollable = ctk.CTkScrollableFrame(list_frame, width=800, height=400)
    scrollable.grid(row=0, column=0, sticky="nsew")
    scrollable.grid_columnconfigure(0, weight=1)

    if patients:
        # Table headers
        hdr = ctk.CTkFrame(scrollable)
        hdr.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        hdr.grid_columnconfigure((0,1,2,3), weight=1)
        for col, text in enumerate(["Name","DOB","Diagnosis","Actions"]):
            ctk.CTkLabel(hdr, text=text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=5, pady=5, sticky="w")
        # Rows
        for i, p in enumerate(patients):
            frame = ctk.CTkFrame(scrollable)
            frame.grid(row=i+1, column=0, padx=5, pady=2, sticky="ew")
            frame.grid_columnconfigure((0,1,2), weight=1)
            # Name
            name = f"{p['first_name']} {p['last_name']}"
            ctk.CTkLabel(frame, text=name).grid(row=0, column=0, padx=5, pady=10, sticky="w")
            # DOB
            dob = datetime.datetime.strptime(p["date_of_birth"], "%Y-%m-%d").strftime("%d/%m/%Y")
            ctk.CTkLabel(frame, text=dob).grid(row=0, column=1, padx=5, pady=10, sticky="w")
            # Diagnosis
            ctk.CTkLabel(frame, text=p["diagnosis"]).grid(row=0, column=2, padx=5, pady=10, sticky="w")
            # Actions
            act = ctk.CTkFrame(frame)
            act.grid(row=0, column=3, padx=5, pady=5)
            ctk.CTkButton(act, text="View", width=70, command=lambda pid=p['id']: show_patient_details(app, pid)).grid(row=0, column=0, padx=5)
            ctk.CTkButton(act, text="Edit", width=70, command=lambda pid=p['id']: show_edit_patient(app, pid)).grid(row=0, column=1, padx=5)
    else:
        ctk.CTkLabel(scrollable, text="No patients found.").grid(row=0, column=0, padx=20, pady=20)
    
    app.current_frame = patients_frame


def show_add_patient(app):
    # Delegate to DB-backed form in gui.py or re-implement similar form here
    from .gui import show_add_patient as gui_show_add
    gui_show_add(app)


def show_patient_details(app, patient_id):
    from .gui import show_patient_details as gui_show_details
    gui_show_details(app, patient_id)


def show_edit_patient(app, patient_id):
    from .gui import show_edit_patient as gui_show_edit
    gui_show_edit(app, patient_id)


def delete_patient_confirm(app, patient_id):
    from .gui import delete_patient_confirm as gui_delete
    gui_delete(app, patient_id)
