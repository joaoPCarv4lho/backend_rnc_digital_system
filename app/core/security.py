from datetime import datetime, timedelta
from app.core.config import settings
from jose import JWTError, jwt
import logging

logger = logging.getLogger(__name__)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Cria token JWT com debug detalhado"""
    
    if not data or not isinstance(data, dict):
        logger.error("Dados inválidos!")
        raise ValueError("Invalid payload data for token generation")

    try:
        # Preparar dados e definir expiração
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_IN_MINUTES))
        to_encode.update({"exp": expire})
        
        logger.info(f"   ⏰ Data de expiração: {expire}")
        logger.info(f"   📦 Dados com expiração: {to_encode}")
        
        # Criar token
        token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        logger.debug(f"   🎉 Token criado com sucesso para o usuário: {data.get('sub')}")
        return token
        
    except Exception as e:
        logger.exception(f"   💥 ERRO em create_access_token: {e}")
        raise RuntimeError("Failed to create JWT token") from e

def verify_token(token: str) -> dict | None:
    """Verifica token JWT"""
    try:        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.debug("Token verificado com sucesso")
        return payload
    except JWTError as e:
        logger.warning(f"❌ Token inválido: {e}")
        return None