import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk

from app.app import app
from app.core.config import settings
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(settings.LOG_DIR, "eira.log"),
            encoding="utf-8",
        ),
    ],
)

logger = logging.getLogger(__name__)


class EiraDesktopApp(ctk.CTk):
    """Main desktop application class."""

    def __init__(self):
        super().__init__()

        # Set up the main window
        self.title(settings.APP_NAME)
        self.geometry("1200x800")
        self.minsize(800, 600)

        # Set appearance mode based on settings
        if settings.THEME == "system":
            ctk.set_appearance_mode("system")
        else:
            ctk.set_appearance_mode(settings.THEME)

        # Set default color theme
        ctk.set_default_color_theme("blue")

        # Initialize the app
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(app.initialize())

        # Show login window if not authenticated, otherwise show main window
        if app.auth_token is None:
            self.show_login_window()
        else:
            self.show_main_window()

        # Set up clean shutdown
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_login_window(self):
        """Show the login window."""
        # Clear any existing frames
        for widget in self.winfo_children():
            widget.destroy()

        # Create and show login window
        self.login_window = LoginWindow(self, self.on_login_success)
        self.login_window.pack(fill="both", expand=True)

    def show_main_window(self):
        """Show the main application window."""
        # Clear any existing frames
        for widget in self.winfo_children():
            widget.destroy()

        # Create and show main window
        self.main_window = MainWindow(self, app)
        self.main_window.pack(fill="both", expand=True)

    def on_login_success(self):
        """Handle successful login."""
        self.show_main_window()

    def on_closing(self):
        """Handle application closing."""
        logger.info("Application closing")
        # Run shutdown tasks
        self.loop.run_until_complete(app.shutdown())
        self.destroy()


def main():
    """Main entry point for the application."""
    app_instance = EiraDesktopApp()
    app_instance.mainloop()


if __name__ == "__main__":
    main()