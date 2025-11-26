import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.config import settings

# Configuración para que Swagger muestre el botón de "Authorize"
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.KEYCLOAK_URL}/protocol/openid-connect/token"
)

async def verify_token(token: str) -> dict:
    """Valida la firma del token contra Keycloak (JWKS)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Obtener claves públicas de Keycloak
        issuer_url = settings.keycloak_issuer 
        jwks_url = f"{issuer_url}/protocol/openid-connect/certs"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            jwks = response.json()

        # 2. Encontrar la clave correcta para este token
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"], "kid": key["kid"], "use": key["use"], "n": key["n"], "e": key["e"]
                }

        if not rsa_key:
            raise credentials_exception

        # 3. Decodificar y validar claims
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=[settings.JWT_ALGORITHM],
            audience="account",
            options={"verify_aud": False}
        )
        return payload

    except Exception as e:
        print(f"Error Auth: {e}")
        raise credentials_exception

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Devuelve un diccionario con la identidad del usuario:
    {'email': '...', 'id': '...', 'roles': ['app_professional', ...]}
    """
    payload = await verify_token(token)
    
    email = payload.get("email")
    if email is None:
        raise HTTPException(status_code=401, detail="Token inválido: sin email")
    
    # Extraer roles de Keycloak (Realm Roles)
    realm_access = payload.get("realm_access", {})
    roles = realm_access.get("roles", [])
    
    return {
        "id": payload.get("sub"),
        "email": email,
        "roles": roles
    }

# --- CLASE PORTERO (Role Guard) ---
class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: dict = Depends(get_current_user)):
        """Valida si el usuario tiene alguno de los roles permitidos"""
        user_roles = user.get("roles", [])
        
        # Intersección: Si comparten al menos un rol, pasa.
        if not set(self.allowed_roles).intersection(user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Acceso denegado. Se requiere rol: {self.allowed_roles}"
            )
        return user