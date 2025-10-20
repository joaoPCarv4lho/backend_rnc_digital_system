from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from datetime import timedelta
import logging

from app.core.security import create_access_token
from app.core.config import settings
from app.crud import authenticate_user
from app.database import get_db
from app import schema

logger = logging.getLogger(__name__ )
router = APIRouter()

@router.post('/login', response_model=schema.Token, status_code=status.HTTP_200_OK)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        print(f"🔐 Tentando login para: {form_data.username}")

        user = authenticate_user(db, form_data.username, form_data.password)
        print(f"🔐 Resultado da autenticação: {user is not None}")

        if not user:
            print("❌ Autenticação falhou - usuário não encontrado ou senha incorreta")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
        
        if not user.active:
            print("❌ Usuário inativo")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive User!")
        
        print(f"✅ Usuário autenticado: {user.email}, ID: {user.id}, Role: {user.role}")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        token_data = { "sub": user.email, "role": user.role, "user_id": user.id }
        print(f"📝 Dados do token: {token_data}")

        print("🎯 Chamando create_access_token...")
        access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
        print(f"✅ Token criado: {access_token[:50]}...")

        if not access_token:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create access token!")
        user_response = schema.UserRead(email=user.email, name=user.name, role=user.role, active=user.active, id=user.id)
        print(f"📋 UserResponse criado: {user_response}")

        response_data = { "access_token": access_token, "token_type": "Bearer", "user": user_response }
        print(f"📦 Resposta final montada: {response_data}")
        
        print("🎉 Login realizado com sucesso! Retornando resposta...")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
    except HTTPException as he:
        print(f"🚫 HTTPException no login: {he.detail}")
        raise he
    except Exception as e:
        print(f"💥 ERRO INESPERADO no login: {e}")
        import traceback
        print(f"📜 Traceback completo: {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")