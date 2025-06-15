import asyncio
import logging
import tkinter as tk
from typing import Callable

import customtkinter as ctk

from app.app import app
from app.core.config import settings

logger = logging.getLogger(__name__)


class LoginWindow(ctk.CTkFrame):
    """Login window for the Eira desktop application."""

    def __init__(self, master, on_login_success: Callable):
        super().__init__(master)
        self.master = master
        self.on_login_success = on_login_success

        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create main frame
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Configure login frame grid layout
        self.login_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=0)
        self.login_frame.grid_columnconfigure(0, weight=1)

        # Add logo or app name
        self.logo_label = ctk.CTkLabel(
            self.login_frame,
            text=settings.APP_NAME,
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(40, 20))

        # Add welcome message
        self.welcome_label = ctk.CTkLabel(
            self.login_frame,
            text="Welcome! Please log in to continue.",
            font=ctk.CTkFont(size=14),
        )
        self.welcome_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Add username entry
        self.username_entry = ctk.CTkEntry(
            self.login_frame, width=300, placeholder_text="Username"
        )
        self.username_entry.grid(row=2, column=0, padx=30, pady=(15, 5))

        # Add password entry
        self.password_entry = ctk.CTkEntry(
            self.login_frame, width=300, placeholder_text="Password", show="*"
        )
        self.password_entry.grid(row=3, column=0, padx=30, pady=(5, 15))

        # Add login button
        self.login_button = ctk.CTkButton(
            self.login_frame, text="Login", command=self.login, width=200
        )
        self.login_button.grid(row=4, column=0, padx=30, pady=(5, 15))

        # Add status message
        self.status_label = ctk.CTkLabel(
            self.login_frame,
            text="",
            text_color="red",
            font=ctk.CTkFont(size=12),
        )
        self.status_label.grid(row=5, column=0, padx=30, pady=(0, 20))

        # Add server status indicator
        self.server_status_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        self.server_status_frame.grid(row=6, column=0, padx=30, pady=(20, 10))

        self.server_status_indicator = ctk.CTkLabel(
            self.server_status_frame,
            text="●",
            text_color="gray",
            font=ctk.CTkFont(size=16),
        )
        self.server_status_indicator.pack(side=tk.LEFT, padx=(0, 5))

        self.server_status_label = ctk.CTkLabel(
            self.server_status_frame,
            text="Checking server connection...",
            font=ctk.CTkFont(size=12),
        )
        self.server_status_label.pack(side=tk.LEFT)

        # Add version info
        self.version_label = ctk.CTkLabel(
            self.login_frame,
            text=f"Version {settings.APP_VERSION}",
            font=ctk.CTkFont(size=10),
            text_color="gray",
        )
        self.version_label.grid(row=7, column=0, padx=30, pady=(5, 20))

        # Set focus to username entry
        self.username_entry.focus()

        # Bind Enter key to login
        self.username_entry.bind("<Return>", lambda event: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda event: self.login())

        # Check server connection
        self.check_server_connection()

    def check_server_connection(self):
        """Check connection to the server."""
        asyncio.run_coroutine_threadsafe(
            self._check_connection_async(), self.master.loop
        )

    async def _check_connection_async(self):
        """Asynchronously check connection to the server."""
        try:
            is_online = await app.network_manager.check_connectivity_async()
            if is_online:
                self.server_status_indicator.configure(text_color="green")
                self.server_status_label.configure(text="Server connection established")
            else:
                self.server_status_indicator.configure(text_color="red")
                self.server_status_label.configure(
                    text="Cannot connect to server. You can still work offline."
                )
        except Exception as e:
            logger.error(f"Error checking server connection: {e}")
            self.server_status_indicator.configure(text_color="red")
            self.server_status_label.configure(
                text="Error checking server connection"
            )

    def login(self):
        """Handle login button click."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            self.status_label.configure(text="Please enter username and password")
            return

        # Disable login button and show loading state
        self.login_button.configure(state="disabled", text="Logging in...")
        self.status_label.configure(text="")

        # Start login process
        asyncio.run_coroutine_threadsafe(
            self._login_async(username, password), self.master.loop
        )

    async def _login_async(self, username: str, password: str):
        """Asynchronously log in to the API."""
        try:
            response = await app.login(username, password)
            if "access_token" in response:
                # Login successful
                self.status_label.configure(text="Login successful", text_color="green")
                # Call the success callback
                self.on_login_success()
            else:
                # Login failed with a response but no token
                self.status_label.configure(
                    text="Login failed: Invalid response from server"
                )
                self.login_button.configure(state="normal", text="Login")
        except Exception as e:
            # Login failed with an exception
            error_message = str(e)
            if "401" in error_message:
                self.status_label.configure(text="Invalid username or password")
            elif "Connection" in error_message:
                self.status_label.configure(
                    text="Cannot connect to server. Check your internet connection."
                )
            else:
                self.status_label.configure(text=f"Login error: {error_message}")
            self.login_button.configure(state="normal", text="Login")