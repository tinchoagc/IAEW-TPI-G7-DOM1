from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import Patient, PatientCreate
from app.repositories.patient_repository import PatientRepository

router = APIRouter()

@router.post("/", response_model=Patient)
def create_patient(patient_data: PatientCreate, db: Session = Depends(get_db)):
    repo = PatientRepository(db)
    # Verificamos si ya existe el email
    if repo.get_by_email(patient_data.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    return repo.create(patient_data)

@router.get("/", response_model=list[Patient])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = PatientRepository(db)
    return repo.get_all(skip=skip, limit=limit)