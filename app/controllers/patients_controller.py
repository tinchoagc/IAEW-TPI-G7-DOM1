from fastapi import APIRouter, Depends, HTTPException, status
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

@router.get("/{patient_id}", response_model=Patient)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    repo = PatientRepository(db)
    patient = repo.get_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return patient

@router.put("/{patient_id}", response_model=Patient)
def update_patient(patient_id: int, patient_data: PatientCreate, db: Session = Depends(get_db)):
    repo = PatientRepository(db)
    updated = repo.update(patient_id, patient_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return updated

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    repo = PatientRepository(db)
    ok = repo.delete(patient_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return None