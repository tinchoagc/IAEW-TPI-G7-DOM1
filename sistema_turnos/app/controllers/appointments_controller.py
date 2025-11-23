from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import Appointment, AppointmentCreate
from app.services.appointment_service import AppointmentService
# --- IMPORTS NUEVOS ---
from app.auth.dependencies import get_current_professional
from app.models.professional import Professional
from app.models.appointment import AppointmentStatus # Importar el Enum
from typing import Optional

router = APIRouter()

def get_appointment_service(db: Session = Depends(get_db)) -> AppointmentService:
    return AppointmentService(db)

@router.post("/", response_model=Appointment)
async def create_appointment( 
    appt_data: AppointmentCreate, 
    service: AppointmentService = Depends(get_appointment_service)
):
    return await service.create_appointment(appt_data)

@router.get("/professional/{professional_id}", response_model=list[Appointment])
def get_professional_agenda(
    professional_id: int, 
    service: AppointmentService = Depends(get_appointment_service)
):
    return service.get_appointments_for_professional(professional_id)

@router.get("/{appointment_id}", response_model=Appointment)
def get_appointment(
    appointment_id: int, 
    service: AppointmentService = Depends(get_appointment_service)
):
    return service.get_appointment_detail(appointment_id)

@router.get("/me/agenda", response_model=list[Appointment])
def get_my_agenda(
    service: AppointmentService = Depends(get_appointment_service),
    current_user: Professional = Depends(get_current_professional) # <--- Esto activa el candado
):
    return service.get_appointments_for_professional(current_user.id)

@router.patch("/{appointment_id}/status", response_model=Appointment)
async def update_appointment_status(
    appointment_id: int, 
    status: AppointmentStatus,
    webhook_url: Optional[str] = None, # Para probar dinámicamente
    service: AppointmentService = Depends(get_appointment_service),
    current_user: Professional = Depends(get_current_professional) # Requiere login
):
    """
    Cambia el estado del turno y dispara un Webhook de notificación.
    """
    return await service.update_status(appointment_id, status, webhook_url)