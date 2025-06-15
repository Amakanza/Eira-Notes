import logging
import os
import json
from typing import Dict, Any, Optional, Callable

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog

from app.app import EiraApp
from app.config import settings

logger = logging.getLogger(__name__)


class SettingsView(ctk.CTkFrame):
    """Settings view for the Eira desktop application."""

    def __init__(self, master, app: EiraApp):
        super().__init__(master)
        self.master = master
        self.app = app
        self.settings_changed = False
        self.original_settings = {}
        self.settings_fields = {}

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create title
        self._create_title()

        # Create settings content
        self._create_settings_content()

        # Create bottom buttons
        self._create_bottom_buttons()

        # Load current settings
        self._load_settings()

    def _create_title(self):
        """Create title section."""
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        title_label = ctk.CTkLabel(
            title_frame,
            text="Application Settings",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Configure application behavior and appearance",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        subtitle_label.pack(anchor="w")

    def _create_settings_content(self):
        """Create settings content with tabs."""
        # Create scrollable frame for settings
        self.settings_frame = ctk.CTkScrollableFrame(self)
        self.settings_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.settings_frame.grid_columnconfigure(0, weight=1)

        # Create tabs
        self.tab_view = ctk.CTkTabview(self.settings_frame)
        self.tab_view.pack(fill="both", expand=True, padx=5, pady=5)

        # Add tabs
        self.general_tab = self.tab_view.add("General")
        self.appearance_tab = self.tab_view.add("Appearance")
        self.sync_tab = self.tab_view.add("Sync")
        self.advanced_tab = self.tab_view.add("Advanced")

        # Configure tab grid layouts
        for tab in [self.general_tab, self.appearance_tab, self.sync_tab, self.advanced_tab]:
            tab.grid_columnconfigure(0, weight=1)

        # Create settings sections in each tab
        self._create_general_settings()
        self._create_appearance_settings()
        self._create_sync_settings()
        self._create_advanced_settings()

    def _create_general_settings(self):
        """Create general settings section."""
        # API Settings
        api_frame = self._create_settings_section(self.general_tab, "API Connection", 0)

        # API URL
        self._add_text_setting(
            api_frame,
            "api_url",
            "API URL",
            "The URL of the backend API server",
            settings.api_url,
        )

        # Application Settings
        app_frame = self._create_settings_section(self.general_tab, "Application", 1)

        # Application name
        self._add_text_setting(
            app_frame,
            "app_name",
            "Application Name",
            "Display name of the application",
            settings.app_name,
        )

        # Application version
        self._add_text_setting(
            app_frame,
            "app_version",
            "Application Version",
            "Current version of the application",
            settings.app_version,
            readonly=True,
        )

        # Database Settings
        db_frame = self._create_settings_section(self.general_tab, "Database", 2)

        # Database path
        self._add_path_setting(
            db_frame,
            "db_path",
            "Database Path",
            "Path to the local SQLite database file",
            settings.db_path,
            is_file=True,
        )

    def _create_appearance_settings(self):
        """Create appearance settings section."""
        # Theme Settings
        theme_frame = self._create_settings_section(self.appearance_tab, "Theme", 0)

        # Color theme
        self._add_dropdown_setting(
            theme_frame,
            "ui_theme",
            "Color Theme",
            "Application color theme",
            settings.ui_theme,
            options=["system", "dark", "light"],
        )

        # Color mode
        self._add_dropdown_setting(
            theme_frame,
            "ui_color_mode",
            "Color Mode",
            "Application color accent",
            settings.ui_color_mode,
            options=["blue", "green", "dark-blue"],
        )

        # Scaling factor
        self._add_dropdown_setting(
            theme_frame,
            "ui_scaling",
            "UI Scaling",
            "Scale factor for UI elements",
            str(settings.ui_scaling),
            options=["0.8", "1.0", "1.2", "1.4", "1.6"],
        )

        # Font Settings
        font_frame = self._create_settings_section(self.appearance_tab, "Fonts", 1)

        # Default font size
        self._add_dropdown_setting(
            font_frame,
            "ui_font_size",
            "Default Font Size",
            "Base font size for UI elements",
            str(settings.ui_font_size),
            options=["10", "12", "14", "16", "18"],
        )

        # Font family
        self._add_dropdown_setting(
            font_frame,
            "ui_font_family",
            "Font Family",
            "Font family for UI elements",
            settings.ui_font_family,
            options=["Default", "Helvetica", "Arial", "Roboto", "Segoe UI"],
        )

    def _create_sync_settings(self):
        """Create sync settings section."""
        # Sync Settings
        sync_frame = self._create_settings_section(self.sync_tab, "Synchronization", 0)

        # Auto sync
        self._add_switch_setting(
            sync_frame,
            "sync_auto_enabled",
            "Auto Sync",
            "Automatically sync data when online",
            settings.sync_auto_enabled,
        )

        # Sync interval
        self._add_dropdown_setting(
            sync_frame,
            "sync_interval",
            "Sync Interval (minutes)",
            "How often to automatically sync data",
            str(settings.sync_interval),
            options=["5", "10", "15", "30", "60"],
        )

        # Sync on startup
        self._add_switch_setting(
            sync_frame,
            "sync_on_startup",
            "Sync on Startup",
            "Automatically sync when application starts",
            settings.sync_on_startup,
        )

        # Conflict Resolution
        conflict_frame = self._create_settings_section(self.sync_tab, "Conflict Resolution", 1)

        # Default conflict resolution
        self._add_dropdown_setting(
            conflict_frame,
            "sync_conflict_resolution",
            "Default Resolution",
            "How to resolve conflicts by default",
            settings.sync_conflict_resolution,
            options=["ask", "local_wins", "remote_wins", "newest_wins"],
        )

        # Network Settings
        network_frame = self._create_settings_section(self.sync_tab, "Network", 2)

        # Connection check interval
        self._add_dropdown_setting(
            network_frame,
            "network_check_interval",
            "Connection Check Interval (seconds)",
            "How often to check network connectivity",
            str(settings.network_check_interval),
            options=["10", "30", "60", "120", "300"],
        )

        # Connection timeout
        self._add_dropdown_setting(
            network_frame,
            "network_timeout",
            "Connection Timeout (seconds)",
            "Timeout for network requests",
            str(settings.network_timeout),
            options=["5", "10", "15", "30", "60"],
        )

    def _create_advanced_settings(self):
        """Create advanced settings section."""
        # Logging Settings
        logging_frame = self._create_settings_section(self.advanced_tab, "Logging", 0)

        # Log level
        self._add_dropdown_setting(
            logging_frame,
            "log_level",
            "Log Level",
            "Detail level for application logs",
            settings.log_level,
            options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )

        # Log file path
        self._add_path_setting(
            logging_frame,
            "log_file",
            "Log File Path",
            "Path to the log file",
            settings.log_file,
            is_file=True,
        )

        # Cache Settings
        cache_frame = self._create_settings_section(self.advanced_tab, "Cache", 1)

        # Cache enabled
        self._add_switch_setting(
            cache_frame,
            "cache_enabled",
            "Enable Cache",
            "Cache API responses for better performance",
            settings.cache_enabled,
        )

        # Cache expiration
        self._add_dropdown_setting(
            cache_frame,
            "cache_expiration",
            "Cache Expiration (minutes)",
            "How long to keep cached data",
            str(settings.cache_expiration),
            options=["5", "15", "30", "60", "120"],
        )

        # Cache directory
        self._add_path_setting(
            cache_frame,
            "cache_dir",
            "Cache Directory",
            "Directory for cached files",
            settings.cache_dir,
            is_file=False,
        )

        # Debug Settings
        debug_frame = self._create_settings_section(self.advanced_tab, "Debug", 2)

        # Debug mode
        self._add_switch_setting(
            debug_frame,
            "debug_mode",
            "Debug Mode",
            "Enable additional debugging features",
            settings.debug_mode,
        )

        # Reset button
        reset_button = ctk.CTkButton(
            debug_frame,
            text="Reset All Settings",
            command=self._on_reset_settings,
            fg_color="red",
            hover_color="#AA0000",
        )
        reset_button.pack(anchor="w", padx=10, pady=10)

    def _create_settings_section(self, parent, title: str, row: int) -> ctk.CTkFrame:
        """Create a settings section with title."""
        section_frame = ctk.CTkFrame(parent)
        section_frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")

        title_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title_label.pack(anchor="w", padx=10, pady=(10, 5))

        separator = ctk.CTkFrame(section_frame, height=1, fg_color="gray")
        separator.pack(fill="x", padx=10, pady=(0, 10))

        return section_frame

    def _add_text_setting(
        self,
        parent,
        key: str,
        label: str,
        description: str,
        default_value: str,
        readonly: bool = False,
    ):
        """Add a text input setting."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5)

        label_frame = ctk.CTkFrame(frame, fg_color="transparent")
        label_frame.pack(side="left", fill="x", expand=True)

        setting_label = ctk.CTkLabel(
            label_frame,
            text=label,
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        setting_label.pack(anchor="w")

        description_label = ctk.CTkLabel(
            label_frame,
            text=description,
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
        )
        description_label.pack(anchor="w")

        entry = ctk.CTkEntry(frame, width=250, state="readonly" if readonly else "normal")
        entry.pack(side="right", padx=(10, 0))
        entry.insert(0, default_value)

        self.settings_fields[key] = entry

    def _add_path_setting(
        self,
        parent,
        key: str,
        label: str,
        description: str,
        default_value: str,
        is_file: bool = True,
    ):
        """Add a path input setting with browse button."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5)

        label_frame = ctk.CTkFrame(frame, fg_color="transparent")
        label_frame.pack(side="left", fill="x", expand=True)

        setting_label = ctk.CTkLabel(
            label_frame,
            text=label,
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        setting_label.pack(anchor="w")

        description_label = ctk.CTkLabel(
            label_frame,
            text=description,
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
        )
        description_label.pack(anchor="w")

        path_frame = ctk.CTkFrame(frame, fg_color="transparent")
        path_frame.pack(side="right")

        entry = ctk.CTkEntry(path_frame, width=200)
        entry.pack(side="left")
        entry.insert(0, default_value)

        browse_button = ctk.CTkButton(
            path_frame,
            text="Browse",
            width=60,
            command=lambda: self._browse_path(entry, is_file),
        )
        browse_button.pack(side="left", padx=(5, 0))

        self.settings_fields[key] = entry

    def _add_dropdown_setting(
        self,
        parent,
        key: str,
        label: str,
        description: str,
        default_value: str,
        options: list,
    ):
        """Add a dropdown setting."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5)

        label_frame = ctk.CTkFrame(frame, fg_color="transparent")
        label_frame.pack(side="left", fill="x", expand=True)

        setting_label = ctk.CTkLabel(
            label_frame,
            text=label,
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        setting_label.pack(anchor="w")

        description_label = ctk.CTkLabel(
            label_frame,
            text=description,
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
        )
        description_label.pack(anchor="w")

        var = tk.StringVar(value=default_value)
        dropdown = ctk.CTkOptionMenu(
            frame,
            values=options,
            variable=var,
            width=150,
            command=lambda _: self._mark_settings_changed(),
        )
        dropdown.pack(side="right")

        self.settings_fields[key] = var

    def _add_switch_setting(
        self,
        parent,
        key: str,
        label: str,
        description: str,
        default_value: bool,
    ):
        """Add a switch setting."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5)

        label_frame = ctk.CTkFrame(frame, fg_color="transparent")
        label_frame.pack(side="left", fill="x", expand=True)

        setting_label = ctk.CTkLabel(
            label_frame,
            text=label,
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        setting_label.pack(anchor="w")

        description_label = ctk.CTkLabel(
            label_frame,
            text=description,
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
        )
        description_label.pack(anchor="w")

        var = tk.BooleanVar(value=default_value)
        switch = ctk.CTkSwitch(
            frame,
            text="",
            variable=var,
            command=self._mark_settings_changed,
        )
        switch.pack(side="right")

        self.settings_fields[key] = var

    def _create_bottom_buttons(self):
        """Create bottom buttons for saving/canceling settings."""
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="e")

        self.status_label = ctk.CTkLabel(
            buttons_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        self.status_label.pack(side="left", padx=(0, 20))

        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self._on_cancel,
            fg_color="gray",
            width=100,
        )
        cancel_button.pack(side="left", padx=5)

        save_button = ctk.CTkButton(
            buttons_frame,
            text="Save Settings",
            command=self._on_save,
            width=150,
        )
        save_button.pack(side="left", padx=5)

    def _load_settings(self):
        """Load current settings into form."""
        try:
            # Store original settings for comparison
            self.original_settings = {
                "api_url": settings.api_url,
                "app_name": settings.app_name,
                "app_version": settings.app_version,
                "db_path": settings.db_path,
                "ui_theme": settings.ui_theme,
                "ui_color_mode": settings.ui_color_mode,
                "ui_scaling": str(settings.ui_scaling),
                "ui_font_size": str(settings.ui_font_size),
                "ui_font_family": settings.ui_font_family,
                "sync_auto_enabled": settings.sync_auto_enabled,
                "sync_interval": str(settings.sync_interval),
                "sync_on_startup": settings.sync_on_startup,
                "sync_conflict_resolution": settings.sync_conflict_resolution,
                "network_check_interval": str(settings.network_check_interval),
                "network_timeout": str(settings.network_timeout),
                "log_level": settings.log_level,
                "log_file": settings.log_file,
                "cache_enabled": settings.cache_enabled,
                "cache_expiration": str(settings.cache_expiration),
                "cache_dir": settings.cache_dir,
                "debug_mode": settings.debug_mode,
            }

            # Set values in form fields
            for key, field in self.settings_fields.items():
                if key in self.original_settings:
                    if isinstance(field, ctk.CTkEntry):
                        field.delete(0, tk.END)
                        field.insert(0, self.original_settings[key])
                    elif isinstance(field, tk.Variable):
                        field.set(self.original_settings[key])

            self.settings_changed = False
            self.status_label.configure(text="")

        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            messagebox.showerror("Error", f"Error loading settings: {str(e)}")

    def _get_current_settings(self) -> Dict[str, Any]:
        """Get current settings from form fields."""
        current_settings = {}

        for key, field in self.settings_fields.items():
            if isinstance(field, ctk.CTkEntry):
                current_settings[key] = field.get()
            elif isinstance(field, tk.Variable):
                current_settings[key] = field.get()

        return current_settings

    def _mark_settings_changed(self):
        """Mark settings as changed."""
        self.settings_changed = True
        self.status_label.configure(text="* Settings have been modified")

    def _browse_path(self, entry_widget, is_file: bool):
        """Open file/directory browser dialog."""
        current_path = entry_widget.get()
        initial_dir = os.path.dirname(current_path) if current_path else os.path.expanduser("~")

        if is_file:
            path = filedialog.asksaveasfilename(
                initialdir=initial_dir,
                title="Select File",
                filetypes=[("All Files", "*.*")],
            )
        else:
            path = filedialog.askdirectory(
                initialdir=initial_dir,
                title="Select Directory",
            )

        if path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, path)
            self._mark_settings_changed()

    def _on_save(self):
        """Handle save button click."""
        try:
            # Get current settings from form
            current_settings = self._get_current_settings()

            # Check if settings have changed
            if not self.settings_changed:
                messagebox.showinfo("Info", "No settings have been changed")
                return

            # Validate settings
            if not self._validate_settings(current_settings):
                return

            # Save settings to file
            self._save_settings_to_file(current_settings)

            # Apply settings
            self._apply_settings(current_settings)

            # Update original settings
            self.original_settings = current_settings.copy()
            self.settings_changed = False
            self.status_label.configure(text="Settings saved successfully")

            messagebox.showinfo(
                "Success",
                "Settings saved successfully. Some changes may require restarting the application.",
            )

        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Error saving settings: {str(e)}")

    def _on_cancel(self):
        """Handle cancel button click."""
        if self.settings_changed:
            confirm = messagebox.askyesno(
                "Confirm Cancel",
                "You have unsaved changes. Are you sure you want to discard them?",
            )
            if not confirm:
                return

        # Reset form to original values
        self._load_settings()

    def _on_reset_settings(self):
        """Handle reset settings button click."""
        confirm = messagebox.askyesno(
            "Confirm Reset",
            "Are you sure you want to reset all settings to default values? This cannot be undone.",
            icon="warning",
        )
        if not confirm:
            return

        try:
            # Reset settings to defaults
            settings.reset_to_defaults()

            # Reload settings in form
            self._load_settings()

            messagebox.showinfo(
                "Success",
                "Settings have been reset to default values. Some changes may require restarting the application.",
            )

        except Exception as e:
            logger.error(f"Error resetting settings: {e}")
            messagebox.showerror("Error", f"Error resetting settings: {str(e)}")

    def _validate_settings(self, settings_dict: Dict[str, Any]) -> bool:
        """Validate settings before saving."""
        # Validate API URL
        api_url = settings_dict.get("api_url", "")
        if not api_url.startswith(("http://", "https://")):
            messagebox.showerror(
                "Validation Error", "API URL must start with http:// or https://"
            )
            return False

        # Validate paths
        for key in ["db_path", "log_file"]:
            path = settings_dict.get(key, "")
            if not path:
                messagebox.showerror("Validation Error", f"{key} cannot be empty")
                return False

            # Check if directory exists or can be created
            dir_path = os.path.dirname(path)
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except Exception as e:
                    messagebox.showerror(
                        "Validation Error", f"Cannot create directory for {key}: {str(e)}"
                    )
                    return False

        # Validate cache directory
        cache_dir = settings_dict.get("cache_dir", "")
        if not cache_dir:
            messagebox.showerror("Validation Error", "Cache directory cannot be empty")
            return False

        # Check if directory exists or can be created
        if not os.path.exists(cache_dir):
            try:
                os.makedirs(cache_dir, exist_ok=True)
            except Exception as e:
                messagebox.showerror(
                    "Validation Error", f"Cannot create cache directory: {str(e)}"
                )
                return False

        return True

    def _save_settings_to_file(self, settings_dict: Dict[str, Any]):
        """Save settings to configuration file."""
        # Convert settings to appropriate types
        typed_settings = {}
        for key, value in settings_dict.items():
            if key in ["ui_scaling", "ui_font_size", "sync_interval", "network_check_interval", 
                      "network_timeout", "cache_expiration"]:
                typed_settings[key] = float(value)
            elif key in ["sync_auto_enabled", "sync_on_startup", "cache_enabled", "debug_mode"]:
                typed_settings[key] = bool(value)
            else:
                typed_settings[key] = value

        # Get config file path
        config_dir = os.path.dirname(settings.config_file)
        os.makedirs(config_dir, exist_ok=True)

        # Write settings to file
        with open(settings.config_file, "w") as f:
            json.dump(typed_settings, f, indent=2)

    def _apply_settings(self, settings_dict: Dict[str, Any]):
        """Apply settings to the application."""
        # Update settings object
        for key, value in settings_dict.items():
            if hasattr(settings, key):
                # Convert to appropriate type
                if key in ["ui_scaling", "ui_font_size", "sync_interval", "network_check_interval", 
                          "network_timeout", "cache_expiration"]:
                    setattr(settings, key, float(value))
                elif key in ["sync_auto_enabled", "sync_on_startup", "cache_enabled", "debug_mode"]:
                    setattr(settings, key, bool(value))
                else:
                    setattr(settings, key, value)

        # Apply UI theme settings
        if "ui_theme" in settings_dict:
            ctk.set_appearance_mode(settings_dict["ui_theme"])

        if "ui_color_mode" in settings_dict:
            ctk.set_default_color_theme(settings_dict["ui_color_mode"])

        if "ui_scaling" in settings_dict:
            ctk.set_widget_scaling(float(settings_dict["ui_scaling"]))

        # Apply network settings
        if "network_check_interval" in settings_dict:
            if hasattr(self.app, "network_manager"):
                self.app.network_manager.check_interval = float(settings_dict["network_check_interval"])

        # Apply sync settings
        if "sync_auto_enabled" in settings_dict or "sync_interval" in settings_dict:
            if hasattr(self.app, "db"):
                if bool(settings_dict.get("sync_auto_enabled", False)):
                    self.app.db.start_auto_sync(float(settings_dict.get("sync_interval", 15)))
                else:
                    self.app.db.stop_auto_sync()