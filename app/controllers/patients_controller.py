from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import PatientCreate, PatientUpdate, Patient as PatientSchema
from app.repositories.patient_repository import PatientRepository

router = APIRouter()

@router.post("/", response_model=PatientSchema, status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    repo = PatientRepository(db)
    if repo.get_by_email(patient.email):
        raise HTTPException(status_code=400, detail="Email ya registrado")
    return repo.create(patient)

@router.get("/", response_model=list[PatientSchema])
def list_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return PatientRepository(db).get_all(skip, limit)

@router.get("/{id}", response_model=PatientSchema)
def get_patient(id: int, db: Session = Depends(get_db)):
    patient = PatientRepository(db).get_by_id(id)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return patient

@router.patch("/{id}", response_model=PatientSchema)
def update_patient(id: int, data: PatientUpdate, db: Session = Depends(get_db)):
    patient = PatientRepository(db).update(id, data)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return patient

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(id: int, db: Session = Depends(get_db)):
    if not PatientRepository(db).delete(id):
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return None