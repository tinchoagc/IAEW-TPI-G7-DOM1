from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    RABBITMQ_URL: str
    
    # URL Pública (para el navegador/Swagger)
    KEYCLOAK_URL: str 
    CLIENT_ID: str = "turnos_app" # (Renombramos o aseguramos que coincida con .env)
    
    # URL Interna (para que Docker hable con Docker)
    # Si no la definimos, usará la misma que la pública
    KEYCLOAK_INTERNAL_URL: str | None = None 

    JWT_ALGORITHM: str = "RS256"
    
    # Variables de Observabilidad (Opcionales para config, requeridas por librerías)
    OTEL_SERVICE_NAME: str = "sistema-turnos-api"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://jaeger:4317"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def keycloak_issuer(self):
        # Si hay URL interna definida, úsala. Si no, usa la pública.
        return self.KEYCLOAK_INTERNAL_URL or self.KEYCLOAK_URL

settings = Settings()