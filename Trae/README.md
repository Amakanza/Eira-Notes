# Eira - Clinical Notes and Reporting Application

Eira is a cross-platform desktop and mobile application for clinical notes and reporting, backed by a cloud API with offline synchronization capabilities.

## Project Overview

This application consists of the following components:

1. **Desktop Client (Python)** - CustomTkinter UI with HTTPX for API communication and offline sync
2. **Mobile Client (Python-first)** - Using either BeeWare or Kivy for cross-platform mobile support
3. **Cloud-Hosted Backend** - FastAPI with Pydantic schemas, OAuth2 authentication, and role-based access
4. **Data Layer** - PostgreSQL database with SQLAlchemy ORM, Redis caching, and S3 blob storage
5. **Reporting Engine** - Document generation using python-docx and PDF conversion
6. **Offline-First Sync** - Outbox pattern for offline operations with conflict resolution
7. **DevOps & CI/CD** - Docker containerization, GitHub Actions for CI/CD, and monitoring
8. **Standards & Interoperability** - HL7 FHIR compliance for clinical data

## Getting Started

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- PostgreSQL
- Redis

### Installation

1. Clone the repository
2. Set up the backend:
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up the desktop client:
   ```
   cd desktop
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Set up the mobile client:
   ```
   cd mobile
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the backend:
   ```
   cd backend
   docker-compose up -d
   ```
2. Run the desktop client:
   ```
   cd desktop
   python main.py
   ```
3. Build and run the mobile client:
   ```
   cd mobile
   # For BeeWare:
   briefcase dev
   # For Kivy:
   python main.py
   ```

## Project Structure

## Backend API

The backend API is built with FastAPI and provides the following endpoints:

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/password` - Change password
- `GET /api/v1/auth/me` - Get current user

### Users
- `GET /api/v1/users/` - List all users (admin only)
- `POST /api/v1/users/` - Create a new user (admin only)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user (admin only)

### Patients
- `GET /api/v1/patients/` - List all patients
- `POST /api/v1/patients/` - Create a new patient
- `GET /api/v1/patients/{patient_id}` - Get patient by ID
- `PUT /api/v1/patients/{patient_id}` - Update patient
- `DELETE /api/v1/patients/{patient_id}` - Delete patient

### Clinical Notes
- `GET /api/v1/clinical-notes/` - List all clinical notes
- `POST /api/v1/clinical-notes/` - Create a new clinical note
- `GET /api/v1/clinical-notes/{note_id}` - Get clinical note by ID
- `PUT /api/v1/clinical-notes/{note_id}` - Update clinical note
- `DELETE /api/v1/clinical-notes/{note_id}` - Delete clinical note
- `GET /api/v1/clinical-notes/patient/{patient_id}` - Get clinical notes for a patient
- `POST /api/v1/clinical-notes/{note_id}/attachments` - Upload attachment
- `GET /api/v1/clinical-notes/{note_id}/attachments/{attachment_id}` - Get attachment
- `DELETE /api/v1/clinical-notes/{note_id}/attachments/{attachment_id}` - Delete attachment
- `GET /api/v1/clinical-notes/{note_id}/download` - Download attachment
- `GET /api/v1/clinical-notes/{note_id}/report` - Generate report

### Appointments
- `GET /api/v1/appointments/` - List all appointments
- `POST /api/v1/appointments/` - Create a new appointment
- `GET /api/v1/appointments/{appointment_id}` - Get appointment by ID
- `PUT /api/v1/appointments/{appointment_id}` - Update appointment
- `DELETE /api/v1/appointments/{appointment_id}` - Delete appointment
- `GET /api/v1/appointments/patient/{patient_id}` - Get appointments for a patient
- `GET /api/v1/appointments/today/` - Get today's appointments
- `GET /api/v1/appointments/week/` - Get this week's appointments

### Reports
- `GET /api/v1/reports/clinical-note/{note_id}` - Generate clinical note report
- `GET /api/v1/reports/patient-summary/{patient_id}` - Generate patient summary report
- `GET /api/v1/reports/templates` - List report templates
- `GET /api/v1/reports/custom/{template_name}` - Generate custom report

### FHIR Resources
- `GET /api/v1/fhir/Patient/{fhir_id}` - Get FHIR Patient resource
- `GET /api/v1/fhir/Patient` - Search FHIR Patient resources
- `GET /api/v1/fhir/DocumentReference/{fhir_id}` - Get FHIR DocumentReference resource
- `GET /api/v1/fhir/DocumentReference` - Search FHIR DocumentReference resources
- `GET /api/v1/fhir/Appointment/{fhir_id}` - Get FHIR Appointment resource
- `GET /api/v1/fhir/Appointment` - Search FHIR Appointment resources
- `POST /api/v1/fhir/Patient` - Create patient from FHIR Patient resource

## Database Models

The application uses SQLAlchemy ORM with the following models:

- **User**: Authentication and user management
- **Patient**: Patient information and demographics
- **ClinicalNote**: Clinical documentation with attachments
- **Appointment**: Scheduling and appointment management

## Offline Sync

The desktop and mobile clients implement offline sync using the following approach:

1. All write operations are wrapped in an outbox pattern
2. Changes are stored locally in SQLite
3. When connectivity is restored, changes are pushed to the API
4. Conflicts are resolved using a last-write-wins strategy or user prompt

### Running the Application

1. Start the backend:
   ```
   cd backend
   docker-compose up -d
   ```
2. Run the desktop client:
   ```
   cd desktop
   python main.py
   ```
3. Build and run the mobile client:
   ```
   cd mobile
   # For BeeWare:
   briefcase dev
   # For Kivy:
   python main.py
   ```

## Project Structure

```
├── backend/               # FastAPI backend
│   ├── app/               # Application code
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core functionality
│   │   ├── db/            # Database models and migrations
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   ├── tests/             # Backend tests
│   └── docker/            # Docker configuration
├── desktop/               # Desktop client
│   ├── app/               # Application code
│   │   ├── ui/            # CustomTkinter UI components
│   │   ├── api/           # API client
│   │   └── sync/          # Offline sync logic
│   └── tests/             # Desktop client tests
├── mobile/                # Mobile client
│   ├── app/               # Application code
│   │   ├── ui/            # UI components
│   │   ├── api/           # API client
│   │   └── sync/          # Offline sync logic
│   └── tests/             # Mobile client tests
├── shared/                # Shared code between clients
│   ├── models/            # Shared data models
│   └── utils/             # Shared utilities
└── infrastructure/        # Infrastructure as code
    ├── terraform/         # Terraform configuration
    └── kubernetes/        # Kubernetes configuration
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.