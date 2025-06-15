import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from app.api.client import APIClient
from app.core.config import settings
from app.db.database import Database
from app.network.network_manager import NetworkManager

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


class EiraApp:
    """Main application class for Eira desktop client."""

    def __init__(self):
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.db = Database(
            db_path=settings.DB_PATH,
            api_url=settings.API_URL,
            loop=self.loop,
        )
        self.api_client = APIClient(base_url=settings.API_URL)
        self.network_manager = NetworkManager(
            api_url=settings.API_URL,
            check_interval=30,  # Check every 30 seconds
            connection_timeout=settings.CONNECTION_TIMEOUT,
            on_status_change=self._on_network_status_change,
        )
        self.auth_token = None
        self.current_user = None

    async def initialize(self):
        """Initialize the application."""
        logger.info("Initializing Eira desktop application")

        # Start network monitoring
        self.network_manager.start_monitoring()

        # Load auth token if available
        await self._load_auth_token()

        # Start sync if we're online and have a token
        if self.network_manager.get_status() and self.auth_token:
            self.db.set_auth_token(self.auth_token)
            self.db.set_online_status(True)
            if settings.SYNC_ON_STARTUP:
                await self.db.sync()
            self.db.start_auto_sync()

    async def shutdown(self):
        """Clean up resources when shutting down."""
        logger.info("Shutting down Eira desktop application")

        # Perform final sync if online
        if self.network_manager.get_status() and self.auth_token and settings.SYNC_ON_SHUTDOWN:
            await self.db.sync()

        # Stop background processes
        self.db.stop_auto_sync()
        self.network_manager.stop_monitoring()

        # Close API client
        await self.api_client.close()

    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Log in to the API and store the token."""
        try:
            response = await self.api_client.login(username, password)
            if "access_token" in response:
                self.auth_token = response["access_token"]
                self.api_client.set_token(self.auth_token)
                self.db.set_auth_token(self.auth_token)

                # Get current user profile
                self.current_user = await self.api_client.get_current_user()

                # Save token securely
                await self._save_auth_token()

                # Start sync if online
                if self.network_manager.get_status():
                    self.db.set_online_status(True)
                    await self.db.sync()
                    self.db.start_auto_sync()

            return response
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise

    async def logout(self):
        """Log out and clear the token."""
        self.auth_token = None
        self.current_user = None
        self.api_client.set_token(None)
        self.db.set_auth_token(None)
        self.db.stop_auto_sync()

        # Clear saved token
        await self._clear_auth_token()

    def _on_network_status_change(self, is_online: bool):
        """Handle network status changes."""
        logger.info(f"Network status changed: {'online' if is_online else 'offline'}")

        # Update database online status
        self.db.set_online_status(is_online)

        # If coming online and we have a token, start sync
        if is_online and self.auth_token:
            if self.loop:
                asyncio.run_coroutine_threadsafe(self.db.sync(), self.loop)
            else:
                asyncio.create_task(self.db.sync())
            self.db.start_auto_sync()
        elif not is_online:
            self.db.stop_auto_sync()

    async def _save_auth_token(self):
        """Save authentication token securely."""
        if not self.auth_token:
            return

        if settings.TOKEN_STORAGE == "keyring":
            try:
                import keyring
                keyring.set_password("eira", "auth_token", self.auth_token)
            except ImportError:
                logger.warning("Keyring not available, falling back to file storage")
                self._save_token_to_file()
        elif settings.TOKEN_STORAGE == "file":
            self._save_token_to_file()
        # For "memory" storage, we don't persist the token

    def _save_token_to_file(self):
        """Save token to an encrypted file."""
        if not self.auth_token:
            return

        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64

            # Generate a key from a machine-specific identifier
            machine_id = self._get_machine_id()
            salt = b"eira_salt_value"  # In a real app, store this securely
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
            cipher = Fernet(key)

            # Encrypt the token
            encrypted_token = cipher.encrypt(self.auth_token.encode())

            # Save to file
            token_path = os.path.join(os.path.dirname(settings.DB_PATH), "token.enc")
            with open(token_path, "wb") as f:
                f.write(encrypted_token)

        except Exception as e:
            logger.error(f"Error saving token to file: {e}")

    async def _load_auth_token(self):
        """Load authentication token."""
        if settings.TOKEN_STORAGE == "keyring":
            try:
                import keyring
                token = keyring.get_password("eira", "auth_token")
                if token:
                    self.auth_token = token
                    self.api_client.set_token(token)
                    # Get current user profile
                    try:
                        self.current_user = await self.api_client.get_current_user()
                    except Exception as e:
                        logger.error(f"Error getting user profile: {e}")
                        self.auth_token = None
                        self.api_client.set_token(None)
                        await self._clear_auth_token()
            except ImportError:
                logger.warning("Keyring not available, falling back to file storage")
                await self._load_token_from_file()
        elif settings.TOKEN_STORAGE == "file":
            await self._load_token_from_file()
        # For "memory" storage, we don't have a persisted token to load

    async def _load_token_from_file(self):
        """Load token from an encrypted file."""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64

            token_path = os.path.join(os.path.dirname(settings.DB_PATH), "token.enc")
            if not os.path.exists(token_path):
                return

            # Generate the same key used for encryption
            machine_id = self._get_machine_id()
            salt = b"eira_salt_value"  # Must match the salt used for encryption
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
            cipher = Fernet(key)

            # Read and decrypt the token
            with open(token_path, "rb") as f:
                encrypted_token = f.read()

            token = cipher.decrypt(encrypted_token).decode()
            self.auth_token = token
            self.api_client.set_token(token)

            # Verify token by getting current user profile
            try:
                self.current_user = await self.api_client.get_current_user()
            except Exception as e:
                logger.error(f"Error getting user profile: {e}")
                self.auth_token = None
                self.api_client.set_token(None)
                await self._clear_auth_token()

        except Exception as e:
            logger.error(f"Error loading token from file: {e}")

    async def _clear_auth_token(self):
        """Clear the saved authentication token."""
        if settings.TOKEN_STORAGE == "keyring":
            try:
                import keyring
                keyring.delete_password("eira", "auth_token")
            except ImportError:
                logger.warning("Keyring not available, falling back to file storage")
                self._clear_token_file()
        elif settings.TOKEN_STORAGE == "file":
            self._clear_token_file()

    def _clear_token_file(self):
        """Delete the token file."""
        token_path = os.path.join(os.path.dirname(settings.DB_PATH), "token.enc")
        if os.path.exists(token_path):
            try:
                os.remove(token_path)
            except Exception as e:
                logger.error(f"Error removing token file: {e}")

    def _get_machine_id(self) -> str:
        """Get a unique identifier for this machine."""
        # This is a simplified approach - in a real app, use a more robust method
        if sys.platform == "win32":
            try:
                import winreg
                reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Cryptography")
                machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
                return machine_guid
            except Exception:
                pass
        elif sys.platform == "darwin":
            try:
                import subprocess
                output = subprocess.check_output(["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"])
                for line in output.splitlines():
                    if b"IOPlatformUUID" in line:
                        return line.split(b'"')[-2].decode()
            except Exception:
                pass
        elif sys.platform.startswith("linux"):
            try:
                with open("/etc/machine-id", "r") as f:
                    return f.read().strip()
            except Exception:
                pass

        # Fallback to a hash of the home directory
        return str(hash(os.path.expanduser("~")))


# Global application instance
app = EiraApp()