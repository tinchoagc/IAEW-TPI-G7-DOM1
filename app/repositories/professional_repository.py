from sqlalchemy.orm import Session
from app.models.professional import Professional
from app.schemas import ProfessionalCreate

class ProfessionalRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, professional: ProfessionalCreate) -> Professional:    
        db_professional = Professional(
            first_name=professional.first_name,
            last_name=professional.last_name,
            email=professional.email,
            specialty=professional.specialty,
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

    def update(self, professional_id: int, data: ProfessionalCreate) -> Professional | None:
        professional = self.get_by_id(professional_id)
        if not professional:
            return None
        professional.first_name = data.first_name
        professional.last_name = data.last_name
        professional.email = data.email
        professional.specialty = data.specialty
        self.db.add(professional)
        self.db.commit()
        self.db.refresh(professional)
        return professional

    def delete(self, professional_id: int) -> bool:
        professional = self.get_by_id(professional_id)
        if not professional:
            return False
        self.db.delete(professional)
        self.db.commit()
        return True