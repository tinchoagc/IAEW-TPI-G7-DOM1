from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Convierte una contraseña plana en un hash seguro."""
    # SOLUCIÓN: Cortamos la contraseña a los primeros 72 caracteres
    # para evitar el error de límite de bcrypt.
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash."""
    # Aquí también es buena práctica cortar la entrada para comparar lo mismo
    return pwd_context.verify(plain_password[:72], hashed_password)