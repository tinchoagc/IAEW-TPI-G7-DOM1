from sqlalchemy.orm import Session
from app.models.professional import Professional
from app.schemas import ProfessionalCreate
from app.core.security import get_password_hash # Importamos la utilidad

class ProfessionalRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, professional: ProfessionalCreate) -> Professional:
        # HASHEAMOS la contraseña antes de guardar
        hashed_pwd = get_password_hash(professional.password)
        
        db_professional = Professional(
            first_name=professional.first_name,
            last_name=professional.last_name,
            email=professional.email,
            specialty=professional.specialty,
            hashed_password=hashed_pwd, # Guardamos el hash, NO la plana
            is_active=True
        )
        self.db.add(db_professional)
        self.db.commit()
        self.db.refresh(db_professional)
        return db_professional

    def get_by_id(self, professional_id: int) -> Professional | None:
        return self.db.query(Professional).filter(Professional.id == professional_id).first()

    def get_by_email(self, email: str) -> Professional | None:
        return self.db.query(Professional).filter(Professional.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Professional]:
        return self.db.query(Professional).offset(skip).limit(limit).all()