import asyncio
import logging
import tkinter as tk
from datetime import datetime
from typing import Optional

import customtkinter as ctk

from app.app import EiraApp

logger = logging.getLogger(__name__)


class StatusBar(ctk.CTkFrame):
    """Status bar for the Eira desktop application."""

    def __init__(self, master, app: EiraApp):
        super().__init__(master, height=30)
        self.master = master
        self.app = app

        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)  # Message area expands

        # Network status indicator
        self.network_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.network_frame.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")

        self.network_indicator = ctk.CTkLabel(
            self.network_frame,
            text="●",
            text_color="gray",
            font=ctk.CTkFont(size=16),
        )
        self.network_indicator.pack(side=tk.LEFT, padx=(0, 5))

        self.network_label = ctk.CTkLabel(
            self.network_frame,
            text="Offline",
            font=ctk.CTkFont(size=12),
        )
        self.network_label.pack(side=tk.LEFT)

        # Status message
        self.status_message = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self.status_message.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Sync status
        self.sync_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.sync_frame.grid(row=0, column=2, padx=(5, 10), pady=5, sticky="e")

        self.sync_button = ctk.CTkButton(
            self.sync_frame,
            text="Sync",
            width=60,
            height=24,
            font=ctk.CTkFont(size=12),
            command=self.on_sync_click,
        )
        self.sync_button.pack(side=tk.LEFT, padx=(0, 5))

        self.last_sync_label = ctk.CTkLabel(
            self.sync_frame,
            text="Last sync: Never",
            font=ctk.CTkFont(size=12),
        )
        self.last_sync_label.pack(side=tk.LEFT)

        # Initialize status
        self.update_network_status(self.app.network_manager.get_status())
        self.last_sync_time = None

        # Set up periodic status updates
        self.update_status()

    def update_status(self):
        """Update status periodically."""
        # Update network status
        self.update_network_status(self.app.network_manager.get_status())

        # Update pending changes count
        pending_changes = self.app.db.get_pending_changes()
        conflicts = self.app.db.get_conflicts()

        if conflicts:
            self.status_message.configure(
                text=f"{len(conflicts)} sync conflicts need resolution",
                text_color="red",
            )
        elif pending_changes:
            self.status_message.configure(
                text=f"{len(pending_changes)} changes pending sync",
                text_color="orange",
            )
        else:
            self.status_message.configure(
                text="All changes synced",
                text_color="green",
            )

        # Schedule next update
        self.after(5000, self.update_status)  # Update every 5 seconds

    def update_network_status(self, is_online: bool):
        """Update network status indicator."""
        if is_online:
            self.network_indicator.configure(text_color="green")
            self.network_label.configure(text="Online")
            self.sync_button.configure(state="normal")
        else:
            self.network_indicator.configure(text_color="red")
            self.network_label.configure(text="Offline")
            self.sync_button.configure(state="disabled")

    def update_last_sync_time(self, sync_time: Optional[datetime] = None):
        """Update the last sync time display."""
        if sync_time:
            self.last_sync_time = sync_time
            time_str = sync_time.strftime("%H:%M:%S")
            self.last_sync_label.configure(text=f"Last sync: {time_str}")
        elif self.last_sync_time is None:
            self.last_sync_label.configure(text="Last sync: Never")

    def on_sync_click(self):
        """Handle sync button click."""
        # Disable button during sync
        self.sync_button.configure(state="disabled", text="Syncing...")
        self.status_message.configure(text="Syncing...", text_color="blue")

        # Start sync process
        asyncio.run_coroutine_threadsafe(
            self._sync_async(), self.master.loop
        )

    async def _sync_async(self):
        """Asynchronously perform sync operation."""
        try:
            result = await self.app.db.sync()
            now = datetime.now()
            self.update_last_sync_time(now)

            # Update status message based on result
            if result.get("status") == "success":
                pushed = result.get("pushed", {})
                pulled = result.get("pulled", {})
                total_pushed = sum(pushed.values())
                total_pulled = sum(pulled.values())

                self.status_message.configure(
                    text=f"Sync completed: {total_pushed} pushed, {total_pulled} pulled",
                    text_color="green",
                )
            elif result.get("status") == "offline":
                self.status_message.configure(
                    text="Cannot sync while offline",
                    text_color="orange",
                )
            else:
                self.status_message.configure(
                    text=f"Sync error: {result.get('message', 'Unknown error')}",
                    text_color="red",
                )
        except Exception as e:
            logger.error(f"Sync error: {e}")
            self.status_message.configure(
                text=f"Sync error: {str(e)}",
                text_color="red",
            )
        finally:
            # Re-enable sync button
            self.sync_button.configure(state="normal", text="Sync")