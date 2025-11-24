# config/db/seed.py
from sqlalchemy.orm import Session
from app.models.professional import Professional
from app.models.patient import Patient

def create_initial_data(db: Session):
    print("🌱 [SEED] Verificando datos iniciales...")
    
    # 1. Verificar si existe Román
    roman = db.query(Professional).filter_by(email="roman@riquelme.com").first()
    if not roman:
        print("   -> Creando a Román...")
        roman = Professional(
            first_name="Roman",
            last_name="Riquelme",
            email="roman@riquelme.com",
            specialty="Traumatología",
            is_active=True
        )
        db.add(roman)
    
    # 2. Verificar si existe el Paciente
    messi = db.query(Patient).filter_by(email="lio@messi.com").first()
    if not messi:
        print("   -> Creando a Messi...")
        messi = Patient(
            first_name="Lionel",
            last_name="Messi",
            email="lio@messi.com",
            phone="+5491122334455"
        )
        db.add(messi)

    db.commit()
    print("✅ [SEED] Datos iniciales listos.")