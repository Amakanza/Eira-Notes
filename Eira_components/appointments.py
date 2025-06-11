from .database import DB_PATH
import sqlite3
import customtkinter as ctk

def get_appointments(user_id, filter_type=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT a.*, p.first_name || ' ' || p.last_name as patient_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.user_id = ?
    """

    params = [user_id]

    if filter_type == "today":
        query += " AND date(a.date) = date('now')"
    elif filter_type == "upcoming":
        query += " AND (date(a.date) >= date('now') AND a.status = 'scheduled')"

    query += " ORDER BY a.date, a.time"

    cursor.execute(query, params)
    appointments = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return appointments

def get_appointment(appointment_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """SELECT a.*, p.first_name || ' ' || p.last_name as patient_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.id = ?""",
        (appointment_id,)
    )
    row = cursor.fetchone()
    appointment = dict(row) if row else None

    return appointment

def add_appointment(data, patient_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """INSERT INTO appointments (
                date, time, duration, notes, status, patient_id, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (data["date"], data["time"], data["duration"], data.get("notes"), data["status"], patient_id, user_id)
        )
        conn.commit()
        appointment_id = cursor.lastrowid
        result = {"success": True, "message": "Appointment added successfully", "appointment_id": appointment_id}
    except Exception as e:
        conn.rollback()
        result = {"success": False, "message": f"Error adding appointment: {str(e)}"}
    finally:
        conn.close()

    return result

def update_appointment(appointment_id, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """UPDATE appointments SET
                date = ?, time = ?, duration = ?, notes = ?, status = ?
            WHERE id = ?""",
            (data["date"], data["time"], data["duration"], data.get("notes"), data["status"], appointment_id)
        )
        conn.commit()
        result = {"success": True, "message": "Appointment updated successfully"}
    except Exception as e:
        conn.rollback()
        result = {"success": False, "message": f"Error updating appointment: {str(e)}"}
    finally:
        conn.close()

    return result

def delete_appointment(appointment_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        conn.commit()
        result = {"success": True, "message": "Appointment deleted successfully"}
    except Exception as e:
        conn.rollback()
        result = {"success": False, "message": f"Error deleting appointment: {str(e)}"}
    finally:
        conn.close()

    return result

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

    def show_edit_appointment(self, appointment_id, patient_id):
        self.clear_content()

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
        appt = dict(cursor.fetchone())
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient = dict(cursor.fetchone())
        conn.close()

        appt_frame = ctk.CTkFrame(self.content_frame)
        appt_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        appt_frame.grid_columnconfigure(0, weight=1)
        self.current_frame = appt_frame

        title_label = ctk.CTkLabel(
            appt_frame,
            text=f"Edit Appointment for {patient['first_name']} {patient['last_name']}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

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

        times = ["09:20", "10:00", "10:40", "11:20", "12:00", "12:40", "13:20", "14:00", "14:40", "15:20", "16:00"]
        time_var = tk.StringVar(value=times[0])
        time_dropdown = ctk.CTkOptionMenu(form_frame, variable=time_var, values=times)
        time_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Duration
        duration_label = ctk.CTkLabel(form_frame, text="Duration (minutes):")
        duration_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        duration_var = tk.StringVar(value="40")
        duration_dropdown = ctk.CTkOptionMenu(form_frame, variable=duration_var, values=["40"])
        duration_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Status
        status_label = ctk.CTkLabel(form_frame, text="Status:")
        status_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")

        status_var = tk.StringVar(value=appt['status'])
        status_dropdown = ctk.CTkOptionMenu(
            form_frame,
            variable=status_var,
            values=["scheduled", "completed", "cancelled"]
        )
        status_dropdown.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        # Notes
        notes_label = ctk.CTkLabel(form_frame, text="Notes:")
        notes_label.grid(row=4, column=0, padx=10, pady=10, sticky="ne")

        notes_textbox = ctk.CTkTextbox(form_frame, height=100, width=300)
        notes_textbox.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        notes_textbox.insert("1.0", appt['notes'] if appt['notes'] else "")

        error_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        error_label.grid(row=17, column=0, columnspan=2, padx=10, pady=(10, 0))

        button_frame = ctk.CTkFrame(form_frame)
        button_frame.grid(row=17, column=0, columnspan=2, padx=10, pady=20)

        def handle_save():
            try:
                date_str = f"{year_var.get()}-{month_var.get()}-{day_var.get()}"
                datetime.datetime.strptime(date_str, '%Y-%m-%d')
                time_str = f"{time_var.get()}:00"
                duration = int(duration_var.get())
                appt_data = {
                    "date": date_str,
                    "time": time_str,
                    "duration": duration,
                    "status": status_var.get(),
                    "notes": notes_textbox.get("1.0", "end-1c").strip() or None
                }
                result = update_appointment(appointment_id, appt_data)
                if result["success"]:
                    messagebox.showinfo("Success", result["message"])
                    self.show_patient_details(patient_id)
                else:
                    error_label.configure(text=result["message"])
            except ValueError:
                error_label.configure(text="Invalid date format")

        save_button = ctk.CTkButton(
            button_frame,
            text="Update Appointment",
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


