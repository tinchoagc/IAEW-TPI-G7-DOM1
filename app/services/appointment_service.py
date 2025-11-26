from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.schemas import AppointmentCreate, Appointment
from app.messaging.event_publisher import event_publisher
from datetime import datetime
from app.integration.webhook_client import WebhookClient
from app.models.appointment import AppointmentStatus

class AppointmentService:
    def __init__(self, db: Session):
        self.appointment_repo = AppointmentRepository(db)
        self.patient_repo = PatientRepository(db)
        self.professional_repo = ProfessionalRepository(db)
        self.webhook_client = WebhookClient()

    async def create_appointment(self, data: AppointmentCreate, user_email: str = None) -> Appointment:
        # --- Auto-detección de Paciente ---
        if data.patient_id is None:
            if not user_email:
                raise HTTPException(status_code=400, detail="Falta identificación del paciente.")
            
            patient = self.patient_repo.get_by_email(user_email)
            if not patient:
                raise HTTPException(status_code=403, detail="Perfil de paciente no encontrado.")
            
            data.patient_id = patient.id
        # ----------------------------------

        if not self.patient_repo.get_by_id(data.patient_id):
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        if not self.professional_repo.get_by_id(data.professional_id):
            raise HTTPException(status_code=404, detail="Profesional no encontrado")

        new_appointment = self.appointment_repo.create(data)
        
        # Publicar evento
        message = {
            "event": "AppointmentCreated",
            "data": {
                "appointment_id": new_appointment.id,
                "patient_id": new_appointment.patient_id,
                "professional_id": new_appointment.professional_id,
                "date": str(new_appointment.start_time),
                "status": "PENDING"
            }
        }
        await event_publisher.publish_message("reminder.requested", message)
        
        return new_appointment

    def get_appointments_for_professional(self, professional_id: int) -> list[Appointment]:
        return self.appointment_repo.get_by_professional(professional_id)

    # 👇 NUEVO MÉTODO: Puente entre Auth (Email) y Datos (ID)
    def get_appointments_for_professional_by_email(self, email: str) -> list[Appointment]:
        prof = self.professional_repo.get_by_email(email)
        if not prof:
            raise HTTPException(status_code=404, detail="Perfil profesional no encontrado")
        return self.appointment_repo.get_by_professional(prof.id)

    def get_appointment_detail(self, appointment_id: int) -> Appointment:
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Turno no encontrado")
        return appointment
    
    async def update_status(self, appointment_id: int, new_status: AppointmentStatus, webhook_url: str = None) -> Appointment:
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Turno no encontrado")

        appointment.status = new_status
        appointment.updated_at = datetime.utcnow()
        
        self.appointment_repo.db.add(appointment)
        self.appointment_repo.db.commit()
        self.appointment_repo.db.refresh(appointment)

        # Notificación Interna (RabbitMQ)
        message = {
            "event": "AppointmentUpdated",
            "data": {
                "appointment_id": appointment.id,
                "patient_id": appointment.patient_id,
                "professional_id": appointment.professional_id,
                "date": str(appointment.start_time),
                "status": new_status.value
            }
        }
        await event_publisher.publish_message("reminder.requested", message)

        # Notificación Externa (Webhook)
        if webhook_url:
            event_name = f"appointment.{new_status.value.lower()}"
            await self.webhook_client.send_notification(webhook_url, event_name, appointment)

        return appointment