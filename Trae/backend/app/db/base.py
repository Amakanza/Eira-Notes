# Import all the models, so that Base has them before being imported by Alembic
from app.db.base_class import Base
from app.db.models.user import User
from app.db.models.patient import Patient
from app.db.models.clinical_note import ClinicalNote, Attachment
from app.db.models.appointment import Appointment
from app.db.models.sync_outbox import SyncOutbox