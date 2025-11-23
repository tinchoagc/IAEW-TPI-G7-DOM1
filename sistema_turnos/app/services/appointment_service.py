from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.schemas import AppointmentCreate, Appointment
# Importamos el publicador
from app.messaging.event_publisher import event_publisher
from datetime import datetime
# Importamos el cliente webhook
from app.integration.webhook_client import WebhookClient
from app.models.appointment import AppointmentStatus

class AppointmentService:
    def __init__(self, db: Session):
        self.appointment_repo = AppointmentRepository(db)
        self.patient_repo = PatientRepository(db)
        self.professional_repo = ProfessionalRepository(db)
        self.webhook_client = WebhookClient()

    # NOTA: Ahora definimos la función con 'async'
    async def create_appointment(self, data: AppointmentCreate) -> Appointment:
        # 1. Validar paciente
        if not self.patient_repo.get_by_id(data.patient_id):
            raise HTTPException(status_code=404, detail="Paciente no encontrado")

        # 2. Validar profesional
        if not self.professional_repo.get_by_id(data.professional_id):
            raise HTTPException(status_code=404, detail="Profesional no encontrado")

        # 3. Crear el turno en DB
        new_appointment = self.appointment_repo.create(data)
        
        # 4. --- EVENTO ASÍNCRONO ---
        # Publicamos el mensaje en RabbitMQ
        message = {
            "event": "AppointmentCreated",
            "data": {
                "appointment_id": new_appointment.id,
                "patient_id": new_appointment.patient_id,
                "professional_id": new_appointment.professional_id,
                "date": str(new_appointment.start_time)
            }
        }
        # 'reminder.requested' es la "Routing Key" (la etiqueta del mensaje)
        await event_publisher.publish_message("reminder.requested", message)
        
        return new_appointment

    # Las de lectura pueden seguir siendo normales (sync) o async, 
    # pero por simplicidad las dejamos sync si no usan cosas asíncronas.
    def get_appointments_for_professional(self, professional_id: int) -> list[Appointment]:
        return self.appointment_repo.get_by_professional(professional_id)

    def get_appointment_detail(self, appointment_id: int) -> Appointment:
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Turno no encontrado")
        return appointment
    
    # --- NUEVA FUNCIÓN ---
    async def update_status(self, appointment_id: int, new_status: AppointmentStatus, webhook_url: str = None) -> Appointment:
        # 1. Buscar el turno
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Turno no encontrado")

        # 2. Actualizar estado
        appointment.status = new_status
        appointment.updated_at = datetime.utcnow()
        
        # Guardamos en DB (Commit manual rápido para el ejemplo)
        self.appointment_repo.db.add(appointment)
        self.appointment_repo.db.commit()
        self.appointment_repo.db.refresh(appointment)

        # 3. Integración: Disparar Webhook
        # Solo si nos pasaron una URL (o si la tuviéramos configurada fija)
        if webhook_url:
            event_name = f"appointment.{new_status.value.lower()}"
            # Convertimos el modelo SQLAlchemy a Schema Pydantic para enviarlo limpio
            # Ojo: Aquí pasamos el objeto DB, el cliente se encargará de sacar los datos
            await self.webhook_client.send_notification(webhook_url, event_name, appointment)

        return appointment