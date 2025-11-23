from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import Base, engine
from app.messaging.event_publisher import event_publisher

# --- NUEVOS IMPORTS ---
from app.controllers import (
    patients_controller, 
    professionals_controller, 
    appointments_controller
)
from app.observability import setup_opentelemetry, PrometheusMiddleware, metrics_endpoint

# Crear tablas (dev only)
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando API...")
    await event_publisher.connect()
    
    # --- ACTIVAR OBSERVABILIDAD (TRAZAS) ---
    # setup_opentelemetry(app)
    
    yield
    print("Apagando API...")
    await event_publisher.close()

app = FastAPI(
    title="API Rest - Sistema de Turnos",
    lifespan=lifespan
)

setup_opentelemetry(app)

# --- ACTIVAR MÉTRICAS (PROMETHEUS) ---
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics_endpoint)

# --- ROUTERS ---
app.include_router(patients_controller.router, prefix="/patients", tags=["Patients"])
app.include_router(professionals_controller.router, prefix="/professionals", tags=["Professionals"])
app.include_router(appointments_controller.router, prefix="/appointments", tags=["Appointments"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}