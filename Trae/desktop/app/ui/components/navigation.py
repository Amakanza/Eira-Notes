import logging
from typing import Callable

import customtkinter as ctk

from app.core.config import settings

logger = logging.getLogger(__name__)


class Navigation(ctk.CTkFrame):
    """Navigation sidebar for the Eira desktop application."""

    def __init__(
        self,
        master,
        on_navigation_change: Callable[[str], None],
        on_logout: Callable[[], None],
    ):
        super().__init__(master, width=200)
        self.master = master
        self.on_navigation_change = on_navigation_change
        self.on_logout = on_logout

        # Configure grid layout
        self.grid_rowconfigure(6, weight=1)  # Empty row expands
        self.grid_columnconfigure(0, weight=1)

        # Add logo or app name
        self.logo_label = ctk.CTkLabel(
            self,
            text=settings.APP_NAME,
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Add navigation buttons
        self.nav_buttons = {}

        # Dashboard button
        self.nav_buttons["dashboard"] = ctk.CTkButton(
            self,
            text="Dashboard",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=lambda: self.on_button_click("dashboard"),
        )
        self.nav_buttons["dashboard"].grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        # Patients button
        self.nav_buttons["patients"] = ctk.CTkButton(
            self,
            text="Patients",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=lambda: self.on_button_click("patients"),
        )
        self.nav_buttons["patients"].grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        # Appointments button
        self.nav_buttons["appointments"] = ctk.CTkButton(
            self,
            text="Appointments",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=lambda: self.on_button_click("appointments"),
        )
        self.nav_buttons["appointments"].grid(
            row=3, column=0, sticky="ew", padx=10, pady=5
        )

        # Reports button
        self.nav_buttons["reports"] = ctk.CTkButton(
            self,
            text="Reports",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=lambda: self.on_button_click("reports"),
        )
        self.nav_buttons["reports"].grid(row=4, column=0, sticky="ew", padx=10, pady=5)

        # Settings button
        self.nav_buttons["settings"] = ctk.CTkButton(
            self,
            text="Settings",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=lambda: self.on_button_click("settings"),
        )
        self.nav_buttons["settings"].grid(row=5, column=0, sticky="ew", padx=10, pady=5)

        # Add logout button at the bottom
        self.logout_button = ctk.CTkButton(
            self,
            text="Logout",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=self.on_logout,
        )
        self.logout_button.grid(row=7, column=0, sticky="ew", padx=10, pady=(5, 10))

        # Set initial active button
        self.set_active_button("dashboard")

    def on_button_click(self, button_name: str):
        """Handle navigation button click."""
        self.set_active_button(button_name)
        self.on_navigation_change(button_name)

    def set_active_button(self, button_name: str):
        """Set the active navigation button."""
        # Reset all buttons
        for name, button in self.nav_buttons.items():
            button.configure(
                fg_color="transparent",
                text_color=("gray10", "gray90"),
            )

        # Set active button
        if button_name in self.nav_buttons:
            self.nav_buttons[button_name].configure(
                fg_color=settings.ACCENT_COLOR,
                text_color=("white", "white"),
            )