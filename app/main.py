from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import Request
from contextlib import asynccontextmanager
from app.database import Base, engine, SessionLocal 
from app.messaging.event_publisher import event_publisher
from app.controllers import (
    patients_controller, 
    professionals_controller, 
    appointments_controller
)
from app.observability import setup_opentelemetry, PrometheusMiddleware, metrics_endpoint
from config.db.seed import create_initial_data

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando API...")
    
    db = SessionLocal()
    try:
        create_initial_data(db)
    finally:
        db.close()

    await event_publisher.connect()
    
    yield
    print("Apagando API...")
    await event_publisher.close()

app = FastAPI(
    title="API Rest - Sistema de Turnos",
    lifespan=lifespan
)

setup_opentelemetry(app)
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics_endpoint)

# --- Middleware de errores estándar ---
@app.middleware("http")
async def error_formatter(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # Si la excepción es HTTPException, FastAPI la maneja; aquí capturamos no controladas
        return JSONResponse(status_code=500, content={"message": "Error interno", "detail": str(e)})

# Routers
app.include_router(patients_controller.router, prefix="/patients", tags=["Patients"])
app.include_router(professionals_controller.router, prefix="/professionals", tags=["Professionals"])
app.include_router(appointments_controller.router, prefix="/appointments", tags=["Appointments"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}