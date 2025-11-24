import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.repositories.professional_repository import ProfessionalRepository
from app.models.professional import Professional

# 1. SWAGGER: Usa la URL pública (localhost) para que el navegador llegue
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.KEYCLOAK_URL}/protocol/openid-connect/token"
)

async def get_current_professional(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> Professional:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 2. BACKEND: Usa la URL interna (nombre del contenedor) para la conexión Docker-to-Docker
        # Usamos la propiedad inteligente que creamos en config.py
        issuer_url = settings.keycloak_issuer 
        jwks_url = f"{issuer_url}/protocol/openid-connect/certs"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url)
            # Si falla la conexión interna, lanzamos error para verlo en logs
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
            options={"verify_aud": False}
        )
        
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception

    except Exception as e:
        print(f"Error Auth: {e}") # Debug en logs
        raise credentials_exception

    repo = ProfessionalRepository(db)
    user = repo.get_by_email(email)
    
    if user is None:
        raise HTTPException(status_code=404, detail="Profesional no encontrado en sistema local")
    
    return user