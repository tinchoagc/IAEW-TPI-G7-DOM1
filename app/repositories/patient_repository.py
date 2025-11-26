from sqlalchemy.orm import Session
from app.models.patient import Patient
from app.schemas import PatientCreate

class PatientRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, patient: PatientCreate) -> Patient:
        # Convertimos el esquema Pydantic a Modelo SQLAlchemy
        db_patient = Patient(
            first_name=patient.first_name,
            last_name=patient.last_name,
            email=patient.email,
            phone=patient.phone
        )
        self.db.add(db_patient)
        self.db.commit()
        self.db.refresh(db_patient) # Recarga el objeto con el ID generado
        return db_patient

    def get_by_id(self, patient_id: int) -> Patient | None:
        return self.db.query(Patient).filter(Patient.id == patient_id).first()

    def get_by_email(self, email: str) -> Patient | None:
        return self.db.query(Patient).filter(Patient.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Patient]:
        return self.db.query(Patient).offset(skip).limit(limit).all()
    
    # Agregado para obtener usuario del email
    def get_by_email(self, email: str):
        """Busca un paciente por su email exacto"""
        return self.db.query(Patient).filter(Patient.email == email).first()