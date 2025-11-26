from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.appointment import AppointmentStatus # Reutilizamos el Enum

from typing import Optional # <--- Asegúrate de tener este import

# --- Schemas de Patient ---

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None

class PatientCreate(PatientBase):
    # Al crear, no necesitamos nada extra por ahora
    pass

class Patient(PatientBase):
    # Al leer (devolver) un paciente, sí incluimos su ID
    id: int
    created_at: datetime
    
    # Esta configuración permite que Pydantic lea datos
    # directamente desde los modelos de SQLAlchemy (ej: patient.id)
    class Config:
        from_attributes = True


# --- Schemas de Professional ---

class ProfessionalBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    specialty: Optional[str] = None

class ProfessionalCreate(ProfessionalBase):
    pass

class Professional(ProfessionalBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Schemas de Appointment ---

class AppointmentBase(BaseModel):
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    # Al crear un turno, necesitamos saber de quién y para quién
    # patient_id: int
    patient_id: Optional[int] = None
    professional_id: int

class Appointment(AppointmentBase):
    # Al leer un turno, devolvemos toda la info
    id: int
    patient_id: int
    professional_id: int
    status: AppointmentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Opcional: Podríamos anidar los datos del paciente/profesional
    # patient: Patient
    # professional: Professional

    class Config:
        from_attributes = True