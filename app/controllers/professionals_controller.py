from fastapi import APIRouter, Depends, HTTPException, status
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

@router.get("/{professional_id}", response_model=Professional)
def get_professional(professional_id: int, db: Session = Depends(get_db)):
    repo = ProfessionalRepository(db)
    professional = repo.get_by_id(professional_id)
    if not professional:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    return professional

@router.put("/{professional_id}", response_model=Professional)
def update_professional(professional_id: int, prof_data: ProfessionalCreate, db: Session = Depends(get_db)):
    repo = ProfessionalRepository(db)
    updated = repo.update(professional_id, prof_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    return updated

@router.delete("/{professional_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_professional(professional_id: int, db: Session = Depends(get_db)):
    repo = ProfessionalRepository(db)
    ok = repo.delete(professional_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    return None