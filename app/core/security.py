from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Cria token JWT com debug detalhado"""
    print("🎯 INICIANDO create_access_token...")
    
    try:
        # Debug 1: Verificar parâmetros de entrada
        print(f"   📥 Data recebida: {data}")
        print(f"   ⏰ Expires_delta: {expires_delta}")
        
        # Debug 2: Verificar configurações
        print(f"   🔧 SECRET_KEY existe: {bool(settings.SECRET_KEY)}")
        print(f"   🔧 SECRET_KEY tamanho: {len(settings.SECRET_KEY)}")
        print(f"   🔧 ALGORITHM: {settings.ALGORITHM}")
        
        # Preparar dados
        to_encode = data.copy()
        print(f"   📋 Dados copiados: {to_encode}")
        
        # Definir expiração
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        print(f"   ⏰ Data de expiração: {expire}")
        to_encode.update({"exp": expire})
        print(f"   📦 Dados com expiração: {to_encode}")
        
        # Debug 3: Antes de chamar jwt.encode
        print("   🔨 Chamando jwt.encode...")
        
        # Criar token
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        # Debug 4: Verificar resultado
        print(f"   ✅ jwt.encode retornou: {type(encoded_jwt)}")
        print(f"   ✅ Token criado: {encoded_jwt}")
        
        if encoded_jwt is None:
            print("   ❌ ERRO: jwt.encode retornou None!")
            return None
        
        print(f"   🎉 Token criado com sucesso! Tamanho: {len(encoded_jwt)}")
        return encoded_jwt
        
    except Exception as e:
        print(f"   💥 ERRO em create_access_token: {e}")
        print(f"   💥 Tipo do erro: {type(e).__name__}")
        import traceback
        print(f"   📜 Traceback: {traceback.format_exc()}")
        return None

def verify_token(token: str) -> dict:
    """Verifica token JWT"""
    try:
        secret_key = settings.SECRET_KEY
        if not secret_key or len(secret_key) < 32:
            secret_key = "chave_fallback_32_caracteres_muito_segura_123!!"
        
        payload = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        print(f"❌ Token inválido: {e}")
        return None