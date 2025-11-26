from sqlalchemy.orm import Session
from app.models.professional import Professional
from app.schemas import ProfessionalCreate, ProfessionalUpdate

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

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(Professional).filter(Professional.is_active == True).offset(skip).limit(limit).all()
    
    def update(self, id: int, data: ProfessionalUpdate):
        prof = self.get_by_id(id)
        if not prof:
            return None
        
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(prof, key, value)
            
        self.db.add(prof)
        self.db.commit()
        self.db.refresh(prof)
        return prof

    def delete(self, id: int):
        prof = self.get_by_id(id)
        if prof:
            prof.is_active = False
            self.db.commit()
            return True
        return False