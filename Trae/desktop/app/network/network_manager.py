import asyncio
import logging
import socket
import threading
import time
from typing import Callable, Optional

import httpx

logger = logging.getLogger(__name__)


class NetworkManager:
    """Manages network connectivity status and operations."""

    def __init__(
        self,
        api_url: str,
        check_interval: int = 30,  # seconds
        connection_timeout: int = 5,  # seconds
        on_status_change: Optional[Callable[[bool], None]] = None,
    ):
        self.api_url = api_url
        self.check_interval = check_interval
        self.connection_timeout = connection_timeout
        self.on_status_change = on_status_change
        self.is_online = False
        self._stop_event = threading.Event()
        self._check_thread = None

    def start_monitoring(self) -> None:
        """Start monitoring network connectivity in a background thread."""
        if self._check_thread is None or not self._check_thread.is_alive():
            self._stop_event.clear()
            self._check_thread = threading.Thread(
                target=self._connectivity_check_loop, daemon=True
            )
            self._check_thread.start()

    def stop_monitoring(self) -> None:
        """Stop monitoring network connectivity."""
        if self._check_thread and self._check_thread.is_alive():
            self._stop_event.set()
            self._check_thread.join(timeout=1.0)

    def _connectivity_check_loop(self) -> None:
        """Background thread that periodically checks connectivity."""
        while not self._stop_event.is_set():
            try:
                is_connected = self.check_connectivity()
                if is_connected != self.is_online:
                    logger.info(f"Network status changed: {'online' if is_connected else 'offline'}")
                    self.is_online = is_connected
                    if self.on_status_change:
                        self.on_status_change(is_connected)
            except Exception as e:
                logger.error(f"Error checking connectivity: {e}")
                # Assume offline if there's an error
                if self.is_online:
                    self.is_online = False
                    if self.on_status_change:
                        self.on_status_change(False)

            # Sleep for the check interval or until stopped
            self._stop_event.wait(self.check_interval)

    def check_connectivity(self) -> bool:
        """Check if the device has internet connectivity."""
        # First check if we can resolve DNS
        try:
            socket.getaddrinfo("google.com", 80)
        except socket.gaierror:
            return False

        # Then check if we can connect to our API
        try:
            with httpx.Client(timeout=self.connection_timeout) as client:
                # Try to connect to the API health endpoint
                response = client.get(f"{self.api_url}/health")
                return response.status_code == 200
        except httpx.RequestError:
            return False

    async def check_connectivity_async(self) -> bool:
        """Asynchronously check if the device has internet connectivity."""
        # First check if we can resolve DNS
        try:
            # Run DNS resolution in a thread to avoid blocking
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None, lambda: socket.getaddrinfo("google.com", 80)
            )
        except socket.gaierror:
            return False

        # Then check if we can connect to our API
        try:
            async with httpx.AsyncClient(timeout=self.connection_timeout) as client:
                # Try to connect to the API health endpoint
                response = await client.get(f"{self.api_url}/health")
                return response.status_code == 200
        except httpx.RequestError:
            return False

    def get_status(self) -> bool:
        """Get the current network status."""
        return self.is_online