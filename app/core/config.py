import os
from pydantic_settings import BaseSettings
from typing import Optional
import secrets
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

    DATABASE_URL: str = os.getenv("DATABASE_URL")

    class Config:
        env_file = ".env"


settings = Settings()

print(f"🔧 Configurações carregadas:")
print(f"   SECRET_KEY: {'✅' if settings.SECRET_KEY and len(settings.SECRET_KEY) >= 32 else '❌'}")
print(f"   ALGORITHM: {settings.ALGORITHM}")
print(f"   TOKEN_EXPIRE: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")