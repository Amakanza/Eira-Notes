import json
import logging
from typing import Any, Dict, List, Optional, Union

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class APIClient:
    """Client for interacting with the Eira backend API."""

    def __init__(self, base_url: str = None, token: str = None):
        self.base_url = base_url or settings.API_URL
        self.token = token
        self.client = httpx.AsyncClient()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self.client.aclose()

    def set_token(self, token: str):
        """Set the authentication token."""
        self.token = token

    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if additional_headers:
            headers.update(additional_headers)
        return headers

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make an API request."""
        url = f"{self.base_url}/{endpoint}"
        request_headers = self._get_headers(headers)

        try:
            if method.lower() == "get":
                response = await self.client.get(url, params=params, headers=request_headers)
            elif method.lower() == "post":
                response = await self.client.post(
                    url, json=data, params=params, headers=request_headers
                )
            elif method.lower() == "put":
                response = await self.client.put(
                    url, json=data, params=params, headers=request_headers
                )
            elif method.lower() == "delete":
                response = await self.client.delete(
                    url, params=params, headers=request_headers
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            if response.status_code == 204 or not response.content:
                return {"status": "success"}

            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            try:
                error_data = e.response.json()
            except json.JSONDecodeError:
                error_data = {"detail": e.response.text}
            raise APIError(e.response.status_code, error_data)
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise APIError(0, {"detail": str(e)})

    # Authentication endpoints
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login to get access token."""
        data = {"username": username, "password": password}
        response = await self._request(
            "post", "api/v1/auth/login", data=data
        )
        if "access_token" in response:
            self.token = response["access_token"]
        return response

    async def refresh_token(self) -> Dict[str, Any]:
        """Refresh the access token."""
        return await self._request("post", "api/v1/auth/refresh")

    # User endpoints
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of users."""
        params = {"skip": skip, "limit": limit}
        return await self._request("get", "api/v1/users", params=params)

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user by ID."""
        return await self._request("get", f"api/v1/users/{user_id}")

    async def get_current_user(self) -> Dict[str, Any]:
        """Get current user profile."""
        return await self._request("get", "api/v1/users/me")

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        return await self._request("post", "api/v1/users", data=user_data)

    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user."""
        return await self._request("put", f"api/v1/users/{user_id}", data=user_data)

    async def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Delete a user."""
        return await self._request("delete", f"api/v1/users/{user_id}")

    # Patient endpoints
    async def get_patients(
        self, skip: int = 0, limit: int = 100, search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get list of patients with optional search."""
        params = {"skip": skip, "limit": limit}
        if search:
            params["search"] = search
        return await self._request("get", "api/v1/patients", params=params)

    async def get_patient(self, patient_id: int) -> Dict[str, Any]:
        """Get patient by ID."""
        return await self._request("get", f"api/v1/patients/{patient_id}")

    async def create_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new patient."""
        return await self._request("post", "api/v1/patients", data=patient_data)

    async def update_patient(self, patient_id: int, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a patient."""
        return await self._request(
            "put", f"api/v1/patients/{patient_id}", data=patient_data
        )

    async def delete_patient(self, patient_id: int) -> Dict[str, Any]:
        """Delete a patient."""
        return await self._request("delete", f"api/v1/patients/{patient_id}")

    # Clinical notes endpoints
    async def get_clinical_notes(
        self, patient_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get list of clinical notes, optionally filtered by patient."""
        params = {"skip": skip, "limit": limit}
        if patient_id:
            params["patient_id"] = patient_id
        return await self._request("get", "api/v1/clinical-notes", params=params)

    async def get_clinical_note(self, note_id: int) -> Dict[str, Any]:
        """Get clinical note by ID."""
        return await self._request("get", f"api/v1/clinical-notes/{note_id}")

    async def create_clinical_note(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new clinical note."""
        return await self._request("post", "api/v1/clinical-notes", data=note_data)

    async def update_clinical_note(self, note_id: int, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a clinical note."""
        return await self._request(
            "put", f"api/v1/clinical-notes/{note_id}", data=note_data
        )

    async def delete_clinical_note(self, note_id: int) -> Dict[str, Any]:
        """Delete a clinical note."""
        return await self._request("delete", f"api/v1/clinical-notes/{note_id}")

    # Appointment endpoints
    async def get_appointments(
        self,
        patient_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get list of appointments with optional filters."""
        params = {"skip": skip, "limit": limit}
        if patient_id:
            params["patient_id"] = patient_id
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return await self._request("get", "api/v1/appointments", params=params)

    async def get_appointment(self, appointment_id: int) -> Dict[str, Any]:
        """Get appointment by ID."""
        return await self._request("get", f"api/v1/appointments/{appointment_id}")

    async def create_appointment(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new appointment."""
        return await self._request("post", "api/v1/appointments", data=appointment_data)

    async def update_appointment(
        self, appointment_id: int, appointment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an appointment."""
        return await self._request(
            "put", f"api/v1/appointments/{appointment_id}", data=appointment_data
        )

    async def delete_appointment(self, appointment_id: int) -> Dict[str, Any]:
        """Delete an appointment."""
        return await self._request("delete", f"api/v1/appointments/{appointment_id}")

    # Report endpoints
    async def generate_clinical_note_report(
        self, note_id: int, format: str = "pdf"
    ) -> Dict[str, Any]:
        """Generate a report for a clinical note."""
        params = {"format": format}
        return await self._request(
            "get", f"api/v1/reports/clinical-notes/{note_id}", params=params
        )

    async def generate_patient_summary(
        self, patient_id: int, format: str = "pdf"
    ) -> Dict[str, Any]:
        """Generate a summary report for a patient."""
        params = {"format": format}
        return await self._request(
            "get", f"api/v1/reports/patients/{patient_id}/summary", params=params
        )

    async def get_report_templates(self) -> List[Dict[str, Any]]:
        """Get list of available report templates."""
        return await self._request("get", "api/v1/reports/templates")

    async def generate_custom_report(
        self, template_id: str, data: Dict[str, Any], format: str = "pdf"
    ) -> Dict[str, Any]:
        """Generate a custom report using a template."""
        params = {"format": format}
        return await self._request(
            "post", f"api/v1/reports/templates/{template_id}", data=data, params=params
        )

    # Storage endpoints
    async def upload_file(
        self, file_path: str, file_type: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Upload a file to storage."""
        # This would typically use multipart/form-data, but for simplicity
        # we're just showing the API structure
        data = {"file_type": file_type}
        if metadata:
            data["metadata"] = metadata
        # In a real implementation, you would use httpx's files parameter
        return await self._request("post", "api/v1/storage/upload", data=data)

    async def get_file(self, file_id: str) -> Dict[str, Any]:
        """Get file metadata by ID."""
        return await self._request("get", f"api/v1/storage/files/{file_id}")

    async def get_download_url(self, file_id: str, expires_in: int = 3600) -> Dict[str, Any]:
        """Get a pre-signed download URL for a file."""
        params = {"expires_in": expires_in}
        return await self._request(
            "get", f"api/v1/storage/files/{file_id}/download-url", params=params
        )

    # FHIR endpoints
    async def get_fhir_patient(self, patient_id: str) -> Dict[str, Any]:
        """Get a patient as a FHIR resource."""
        return await self._request("get", f"api/v1/fhir/Patient/{patient_id}")

    async def search_fhir_patients(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for patients using FHIR search parameters."""
        return await self._request("get", "api/v1/fhir/Patient", params=search_params)

    async def get_fhir_document_reference(self, doc_id: str) -> Dict[str, Any]:
        """Get a clinical note as a FHIR DocumentReference."""
        return await self._request("get", f"api/v1/fhir/DocumentReference/{doc_id}")

    async def search_fhir_document_references(
        self, search_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Search for clinical notes using FHIR search parameters."""
        return await self._request(
            "get", "api/v1/fhir/DocumentReference", params=search_params
        )

    async def create_patient_from_fhir(self, fhir_patient: Dict[str, Any]) -> Dict[str, Any]:
        """Create a patient from a FHIR Patient resource."""
        return await self._request(
            "post", "api/v1/fhir/Patient", data=fhir_patient
        )
        
    # Sync endpoints
    async def sync_push(self, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Push local changes to the server."""
        data = {"changes": changes}
        return await self._request("post", "api/v1/sync/push", data=data)
    
    async def sync_pull(self, since: str) -> Dict[str, Any]:
        """Pull changes from the server since the given timestamp."""
        params = {"since": since}
        return await self._request("get", "api/v1/sync/pull", params=params)


class APIError(Exception):
    """Exception raised for API errors."""

    def __init__(self, status_code: int, detail: Dict[str, Any]):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API Error {status_code}: {detail}")