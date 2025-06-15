import asyncio
import logging
import tkinter as tk
from datetime import datetime
from typing import Any, Dict, List, Optional

import customtkinter as ctk

from app.app import EiraApp
from app.core.config import settings
from app.ui.components.navigation import Navigation
from app.ui.components.status_bar import StatusBar
from app.ui.views.appointments_view import AppointmentsView
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.patients_view import PatientsView
from app.ui.views.reports_view import ReportsView
from app.ui.views.settings_view import SettingsView

logger = logging.getLogger(__name__)


class MainWindow(ctk.CTkFrame):
    """Main window for the Eira desktop application."""

    def __init__(self, master, app: EiraApp):
        super().__init__(master)
        self.master = master
        self.app = app

        # Configure grid layout
        self.grid_rowconfigure(1, weight=1)  # Content area expands
        self.grid_columnconfigure(1, weight=1)  # Content area expands

        # Create navigation sidebar
        self.navigation = Navigation(
            self, self.on_navigation_change, self.on_logout
        )
        self.navigation.grid(row=0, column=0, rowspan=2, sticky="nsew")

        # Create header frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=1, sticky="ew", padx=20, pady=(20, 0))

        # Configure header grid
        self.header_frame.grid_columnconfigure(0, weight=1)

        # Add title label to header
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Dashboard",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        # Add user info to header
        self.user_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.user_frame.grid(row=0, column=1, sticky="e")

        # Add user name and role
        user_name = self.app.current_user.get("full_name", "User")
        user_role = self.app.current_user.get("role", "")
        self.user_label = ctk.CTkLabel(
            self.user_frame,
            text=f"{user_name}\n{user_role}",
            font=ctk.CTkFont(size=12),
            justify="right",
        )
        self.user_label.pack(side=tk.RIGHT, padx=(0, 10))

        # Create content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(
            row=1, column=1, sticky="nsew", padx=20, pady=20
        )

        # Configure content grid
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Create status bar
        self.status_bar = StatusBar(self, self.app)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")

        # Initialize views dictionary
        self.views = {}
        self._create_views()

        # Show default view
        self.current_view = "dashboard"
        self.show_view("dashboard")

    def _create_views(self):
        """Create all the application views."""
        # Dashboard view
        self.views["dashboard"] = DashboardView(self.content_frame, self.app)

        # Patients view
        self.views["patients"] = PatientsView(self.content_frame, self.app)

        # Appointments view
        self.views["appointments"] = AppointmentsView(self.content_frame, self.app)

        # Reports view
        self.views["reports"] = ReportsView(self.content_frame, self.app)

        # Settings view
        self.views["settings"] = SettingsView(self.content_frame, self.app)

    def show_view(self, view_name: str):
        """Show the specified view and hide others."""
        # Update title
        title_map = {
            "dashboard": "Dashboard",
            "patients": "Patients",
            "appointments": "Appointments",
            "reports": "Reports",
            "settings": "Settings",
        }
        self.title_label.configure(text=title_map.get(view_name, "Dashboard"))

        # Hide all views
        for name, view in self.views.items():
            view.grid_forget()

        # Show selected view
        if view_name in self.views:
            self.views[view_name].grid(row=0, column=0, sticky="nsew")
            self.current_view = view_name

    def on_navigation_change(self, view_name: str):
        """Handle navigation change."""
        self.show_view(view_name)

    def on_logout(self):
        """Handle logout button click."""
        # Run logout process
        asyncio.run_coroutine_threadsafe(
            self._logout_async(), self.master.loop
        )

    async def _logout_async(self):
        """Asynchronously log out."""
        try:
            await self.app.logout()
            # Show login window
            self.master.show_login_window()
        except Exception as e:
            logger.error(f"Logout error: {e}")
            # Show error message
            # In a real app, you would show a dialog or notification