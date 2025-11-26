from sqlalchemy.orm import Session
from app.models.appointment import Appointment
from app.schemas import AppointmentCreate

class AppointmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, appointment: AppointmentCreate) -> Appointment:
        db_appointment = Appointment(
            patient_id=appointment.patient_id,
            professional_id=appointment.professional_id,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            notes=appointment.notes,
            # Status por defecto es PENDING (definido en el modelo)
        )
        self.db.add(db_appointment)
        self.db.commit()
        self.db.refresh(db_appointment)
        return db_appointment

    def get_by_id(self, appointment_id: int) -> Appointment | None:
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Appointment]:
        return self.db.query(Appointment).offset(skip).limit(limit).all()

    def get_by_professional(self, professional_id: int) -> list[Appointment]:
        """Devuelve todos los turnos de un médico específico"""
        return self.db.query(Appointment).filter(Appointment.professional_id == professional_id).all()

    def exists_overlap(self, professional_id: int, start_time, end_time) -> bool:
        """Verifica si existe solapamiento de turnos para el mismo profesional.
        Criterio: (start_time < existing.end_time) AND (end_time > existing.start_time)
        Ignora turnos CANCELLED.
        """
        q = (
            self.db.query(Appointment)
            .filter(Appointment.professional_id == professional_id)
            .filter(Appointment.status != 'CANCELLED')
            .filter(Appointment.start_time < end_time)
            .filter(Appointment.end_time > start_time)
        )
        return self.db.query(q.exists()).scalar()