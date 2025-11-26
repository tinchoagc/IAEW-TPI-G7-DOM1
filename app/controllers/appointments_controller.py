from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import Appointment, AppointmentCreate
from app.services.appointment_service import AppointmentService
from app.models.appointment import AppointmentStatus
from typing import Optional

# Importamos el validador genérico y el chequeador de roles
from app.auth.dependencies import get_current_user, RoleChecker

router = APIRouter()

# --- DEFINICIÓN DE PORTEROS (Guards) ---
# Solo deja pasar si el token tiene el rol 'app_professional'
require_professional = RoleChecker(["app_professional"])

def get_appointment_service(db: Session = Depends(get_db)) -> AppointmentService:
    return AppointmentService(db)

@router.post("/", response_model=Appointment, status_code=status.HTTP_201_CREATED)
async def create_appointment( 
    appt_data: AppointmentCreate, 
    service: AppointmentService = Depends(get_appointment_service),
    current_user: dict = Depends(get_current_user) # Cualquiera logueado puede crear (Paciente o Staff)
):
    user_email = current_user.get("email")
    return await service.create_appointment(appt_data, user_email=user_email)

@router.get("/professional/{professional_id}", response_model=list[Appointment])
def get_professional_agenda(
    professional_id: int, 
    service: AppointmentService = Depends(get_appointment_service)
):
    return service.get_appointments_for_professional(professional_id)

@router.get("/", response_model=list[Appointment])
def get_all_appointments(
    skip: int = 0, 
    limit: int = 100, 
    service: AppointmentService = Depends(get_appointment_service)
):
    """
    Obtiene TODOS los turnos del sistema (Paginado).
    """
    return service.get_all_appointments(skip, limit)

@router.get("/{appointment_id}", response_model=Appointment)
def get_appointment(
    appointment_id: int, 
    service: AppointmentService = Depends(get_appointment_service)
):
    return service.get_appointment_detail(appointment_id)

# 👇 ESTE ENDPOINT AHORA ES SEGURO POR ROL
@router.get("/me/agenda", response_model=list[Appointment])
def get_my_agenda(
    service: AppointmentService = Depends(get_appointment_service),
    # Si no tiene rol 'app_professional', Keycloak/API lo rebota con 403
    current_user: dict = Depends(require_professional) 
):
    # current_user es {'email': 'roman@...', 'roles': ['app_professional']}
    return service.get_appointments_for_professional_by_email(current_user["email"])

# 👇 ESTE TAMBIÉN (Solo un profesional puede cambiar estados)
@router.patch("/{appointment_id}/status", response_model=Appointment)
async def update_appointment_status(
    appointment_id: int, 
    status: AppointmentStatus,
    webhook_url: Optional[str] = None,
    service: AppointmentService = Depends(get_appointment_service),
    current_user: dict = Depends(require_professional) # <--- Candado activado
):
    return await service.update_status(appointment_id, status, webhook_url)