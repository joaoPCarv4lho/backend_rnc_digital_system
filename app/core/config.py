from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
import secrets
import logging

logger = logging.getLogger()

class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., description="Chave secreta usada para geração de token JWT")
    ALGORITHM: str = Field(default="HS256", description="Algoritmo JWT padrão")
    ACCESS_TOKEN_EXPIRE_IN_MINUTES: int = Field(default=60, description="Tempo de expiração do token")

    DATABASE_URL: str = Field(..., description="URL de conexão com o banco de dados")

    class Config:
        env_file = ".env"
        case_sensitive = True

    @field_validator("SECRET_KEY")
    def validate_secret_key(cls, v: str):
        if not v or len(v):
            logger.warning("SECRET_KEY muito curta! Gerando nova chave secreta temporária...")
            return secrets.token_urlsafe(32)
        return v



settings = Settings()

logger.info(f"🔧 Configurações carregadas:")
logger.debug(f"   ALGORITHM: {settings.ALGORITHM}")
logger.debug(f"   TOKEN_EXPIRE: {settings.ACCESS_TOKEN_EXPIRE_IN_MINUTES}")