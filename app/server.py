from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.security import create_access_token
from datetime import timedelta

from app.database import create_db_and_tables
from app.router import user_router, auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando a API RNC Digital System...")
    
    # Debug das configurações
    print(f"🔑 SECRET_KEY configurada: {len(settings.SECRET_KEY) > 20}")
    print(f"⚙️ ALGORITHM: {settings.ALGORITHM}")
    print(f"⏰ Token expira em: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutos")
    
    # Teste SIMPLES de criação de token
    try:
        print("🧪 Testando criação de token...")
        test_data = {"sub": "test@example.com", "user_id": 1}
        test_token = create_access_token(test_data, timedelta(minutes=1))
        print(f"✅ Teste de token: SUCESSO!")
    except Exception as e:
        print(f"❌ Teste de token: FALHA - {e}")
        # Força uma SECRET_KEY para desenvolvimento
        import os
        os.environ["SECRET_KEY"] = "chave_de_desenvolvimento_32_caracteres_123!!"
        print("🔄 Tentando com SECRET_KEY forçada...")
        try:
            test_data = {"sub": "test@example.com", "user_id": 1}
            test_token = create_access_token(test_data, timedelta(minutes=1))
            print(f"✅ Teste com fallback: SUCESSO!")
        except Exception as e2:
            print(f"💥 Falha crítica: {e2}")

    # Cria tabelas do banco
    print("📦 Criando tabelas no banco de dados...")
    create_db_and_tables()
    print("✅ Tabelas criadas com sucesso!")
    
    yield
    
    print("👋 Encerrando API...")

app = FastAPI(
    title="RNC API", 
    description="API para sistema de Registro de Não Conformidades", 
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router.router, prefix="/user", tags=["Users"])

@app.get('/')
async def root():
    return { "msg": "System RNC started" }

@app.get('/health')
async def health_check():
    return { "status": "healthy", "message": "RNC is running" }



