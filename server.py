from fastapi.middleware.cors import CORSMiddleware
from app.core.security import create_access_token
from app.core.logging_config import setup_logging
from contextlib import asynccontextmanager
from app.core.config import settings
from datetime import timedelta
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
import os

from app.database import create_db_and_tables
from app.router import user_router, auth_router, rnc_router, part_router
from app.websocket.route import router as websocket_router

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando a API RNC Digital System...")
    
    # Debug das configurações
    print(f"🔑 SECRET_KEY configurada: {len(settings.SECRET_KEY) > 20}")
    print(f"⚙️ ALGORITHM: {settings.ALGORITHM}")
    print(f"⏰ Token expira em: {settings.ACCESS_TOKEN_EXPIRE_IN_MINUTES} minutos")
    
    # Teste SIMPLES de criação de token
    try:
        print("🧪 Testando criação de token...")
        test_data = {"sub": "test@example.com", "user_id": 1}
        test_token = create_access_token(test_data, timedelta(minutes=1))
        print(f"✅ Teste de token: SUCESSO!")
    except Exception as e:
        print(f"❌ Teste de token: FALHA - {e}")
        # Força uma SECRET_KEY para desenvolvimento
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

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user_router.router, prefix="/api/user", tags=["Users"])
app.include_router(rnc_router.router, prefix="/api/rnc", tags=["RNC"])
app.include_router(part_router.router, prefix="/api/part", tags=["Parts"])

app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])

@app.get('/')
async def root():
    return { "msg": "System RNC started" }

@app.get('/health')
async def health_check():
    return { "status": "healthy", "message": "RNC is running" }



