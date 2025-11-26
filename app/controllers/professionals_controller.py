from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ProfessionalCreate, ProfessionalUpdate, Professional as ProfessionalSchema
from app.repositories.professional_repository import ProfessionalRepository

router = APIRouter()

@router.post("/", response_model=ProfessionalSchema, status_code=status.HTTP_201_CREATED)
def create_professional(data: ProfessionalCreate, db: Session = Depends(get_db)):
    repo = ProfessionalRepository(db)
    if repo.get_by_email(data.email):
        raise HTTPException(status_code=400, detail="Email ya registrado")
    return repo.create(data)

@router.get("/", response_model=list[ProfessionalSchema])
def list_professionals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ProfessionalRepository(db).get_all(skip, limit)

@router.get("/{id}", response_model=ProfessionalSchema)
def get_professional(id: int, db: Session = Depends(get_db)):
    prof = ProfessionalRepository(db).get_by_id(id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    return prof

@router.patch("/{id}", response_model=ProfessionalSchema)
def update_professional(id: int, data: ProfessionalUpdate, db: Session = Depends(get_db)):
    prof = ProfessionalRepository(db).update(id, data)
    if not prof:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    return prof

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_professional(id: int, db: Session = Depends(get_db)):
    if not ProfessionalRepository(db).delete(id):
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    return None