from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.appointment import AppointmentStatus

# --- Schemas de Patient ---

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None

class PatientCreate(PatientBase):
    pass

# 👇 ESTO ES LO QUE FALTABA: Schema para actualizar (todo opcional)
class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    # No incluimos email para evitar conflictos de unicidad en un update simple

class Patient(PatientBase):
    id: int
    is_active: bool  # <--- Importante para ver si está borrado o no
    created_at: datetime
    
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

# 👇 ESTO TAMBIÉN FALTABA
class ProfessionalUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    specialty: Optional[str] = None

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
    # patient_id es opcional para permitir el auto-agendamiento (lógica de Messi)
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
    
    class Config:
        from_attributes = True