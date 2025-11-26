from fastapi import APIRouter, Depends, HTTPException, status # <--- Agregué 'status'
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import Appointment, AppointmentCreate
from app.services.appointment_service import AppointmentService
from app.models.professional import Professional
from app.models.appointment import AppointmentStatus
from typing import Optional

# 👇 Solo importamos lo que realmente está en auth (el usuario)
from app.auth.dependencies import get_current_user, get_current_professional

router = APIRouter()

# --- DEPENDENCIA LOCAL ---
# Al definirla aquí, no necesitamos importarla de ningún lado. ¡Más simple!
def get_appointment_service(db: Session = Depends(get_db)) -> AppointmentService:
    return AppointmentService(db)

# --- ENDPOINTS ---

@router.post("/", response_model=Appointment, status_code=status.HTTP_201_CREATED)
async def create_appointment( 
    appt_data: AppointmentCreate, 
    service: AppointmentService = Depends(get_appointment_service),
    # 👇 Validamos token y obtenemos datos del usuario (Messi)
    current_user: dict = Depends(get_current_user)
):
    # Sacamos el email del token
    user_email = current_user.get("email")

    # Se lo pasamos al servicio para la auto-detección
    return await service.create_appointment(appt_data, user_email=user_email)

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
    current_user: Professional = Depends(get_current_professional) # <--- Candado para Médicos
):
    return service.get_appointments_for_professional(current_user.id)

@router.patch("/{appointment_id}/status", response_model=Appointment)
async def update_appointment_status(
    appointment_id: int, 
    status: AppointmentStatus,
    webhook_url: Optional[str] = None,
    service: AppointmentService = Depends(get_appointment_service),
    current_user: Professional = Depends(get_current_professional) # <--- Candado para Médicos
):
    """
    Cambia el estado del turno y dispara notificaciones (RabbitMQ + Webhook).
    """
    return await service.update_status(appointment_id, status, webhook_url)