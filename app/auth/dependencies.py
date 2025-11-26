import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.repositories.professional_repository import ProfessionalRepository
from app.models.professional import Professional

# 1. SWAGGER
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.KEYCLOAK_URL}/protocol/openid-connect/token"
)

# --- FUNCIÓN AUXILIAR PARA VALIDAR TOKEN (DRY - Don't Repeat Yourself) ---
async def verify_token(token: str) -> dict:
    """Valida el token contra Keycloak y devuelve el payload"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        issuer_url = settings.keycloak_issuer 
        jwks_url = f"{issuer_url}/protocol/openid-connect/certs"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            jwks = response.json()

        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }

        if not rsa_key:
            raise credentials_exception

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=[settings.JWT_ALGORITHM],
            audience="account",
            options={"verify_aud": False} # Simplificación para el TP
        )
        
        return payload

    except Exception as e:
        print(f"Error Auth: {e}")
        raise credentials_exception

# --- DEPENDENCIA 1: USUARIO GENÉRICO (Para Pacientes o Staff) ---
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Devuelve los datos del usuario (email) sin chequear DB"""
    payload = await verify_token(token)
    email: str = payload.get("email")
    if email is None:
        raise HTTPException(status_code=401, detail="Token sin email")
    
    return {"email": email, "id": payload.get("sub")}

# --- DEPENDENCIA 2: SOLO PROFESIONALES (Para endpoints de médicos) ---
async def get_current_professional(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> Professional:
    """Valida token Y verifica que exista en la tabla Professionals"""
    payload = await verify_token(token)
    email: str = payload.get("email")
    
    repo = ProfessionalRepository(db)
    user = repo.get_by_email(email)
    
    if user is None:
        raise HTTPException(status_code=404, detail="Profesional no encontrado en sistema local")
    
    return user