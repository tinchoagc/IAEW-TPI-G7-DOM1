from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Usamos la DATABASE_URL de nuestro archivo de configuración
engine = create_engine(
    settings.DATABASE_URL,
    # connect_args={"check_same_thread": False} # Solo necesario para SQLite
)

# Creamos una fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creamos una clase Base de la que heredarán nuestros modelos
Base = declarative_base()

# --- Dependencia de FastAPI ---
# Esto es crucial para la inyección de dependencias en los controllers.
# Nos asegura que abrimos una sesión al recibir una request y
# la cerramos (incluso si hay error) al terminar.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()