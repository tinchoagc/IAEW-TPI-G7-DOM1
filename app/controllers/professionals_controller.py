from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import Professional, ProfessionalCreate
from app.repositories.professional_repository import ProfessionalRepository

router = APIRouter()

@router.post("/", response_model=Professional)
def create_professional(prof_data: ProfessionalCreate, db: Session = Depends(get_db)):
    repo = ProfessionalRepository(db)
    if repo.get_by_email(prof_data.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    return repo.create(prof_data)

@router.get("/", response_model=list[Professional])
def read_professionals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = ProfessionalRepository(db)
    return repo.get_all(skip=skip, limit=limit)