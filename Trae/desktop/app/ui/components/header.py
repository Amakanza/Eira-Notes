import logging
from typing import Optional

import customtkinter as ctk

from app.app import EiraApp

logger = logging.getLogger(__name__)


class Header(ctk.CTkFrame):
    """Header component for the Eira desktop application."""

    def __init__(self, master, app: EiraApp):
        super().__init__(master, height=60)
        self.master = master
        self.app = app

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)  # Title expands
        self.grid_columnconfigure(1, weight=0)  # User info fixed width

        # Title label
        self.title_label = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w",
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # User info frame
        self.user_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.user_frame.grid(row=0, column=1, padx=20, pady=10, sticky="e")

        # User avatar (placeholder)
        self.user_avatar = ctk.CTkLabel(
            self.user_frame,
            text="👤",
            font=ctk.CTkFont(size=20),
            width=30,
        )
        self.user_avatar.pack(side="left", padx=(0, 5))

        # User info
        self.user_info = ctk.CTkLabel(
            self.user_frame,
            text="Not logged in",
            font=ctk.CTkFont(size=14),
        )
        self.user_info.pack(side="left")

        # Update user info if available
        self.update_user_info()

    def set_title(self, title: str):
        """Set the header title."""
        self.title_label.configure(text=title)

    def update_user_info(self, user_data: Optional[dict] = None):
        """Update the user information display."""
        if user_data is None:
            # Try to get user data from app
            try:
                current_user = self.app.db.get_current_user()
                if current_user:
                    user_data = current_user
            except Exception as e:
                logger.error(f"Error getting current user: {e}")

        if user_data:
            name = user_data.get("name", "")
            role = user_data.get("role", "")
            display_text = f"{name} ({role})" if role else name
            self.user_info.configure(text=display_text)
        else:
            self.user_info.configure(text="Not logged in")