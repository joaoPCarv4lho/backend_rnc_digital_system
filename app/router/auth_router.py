from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from sqlmodel import Session
from typing import Annotated
import traceback
import logging

from app.repository.auth_repository import AuthRepository
from app.core.security import create_access_token
from app.service.auth_service import AuthService
from app.core.config import settings
from app.database import get_db
from app import schema

logger = logging.getLogger(__name__ )
router = APIRouter()

@router.post('/login', response_model=schema.Token, status_code=status.HTTP_200_OK)
async def login(data_login: schema.UserLogin, db: Annotated[Session, Depends(get_db)]):
    repo = AuthRepository(db)
    auth_service = AuthService(repo)
    try:
        logger.info(f"🔐 Tentando login para: {data_login.email}")

        user = auth_service.authenticate_user(data_login)
        logger.debug(f"🔐 Resultado da autenticação: {user is not None}")

        if not user:
            logger.error("❌ Autenticação falhou - usuário não encontrado ou senha incorreta")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        if not user.active:
            logger.error("❌ Usuário inativo")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive User!")
        
        logger.debug(f"✅ Usuário autenticado: {user.email}, ID: {user.id}, Role: {user.role}")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_IN_MINUTES)

        token_data = { "sub": user.email, "role": user.role, "user_id": user.id }
        logger.info(f"📝 Dados do token: {token_data}")

        access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
        logger.debug(f"✅ Token criado: {access_token[:50]}...")

        if not access_token:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create access token!")
        user_response = schema.UserRead(email=user.email, name=user.name, role=user.role, active=user.active, id=user.id)

        response_data = { "access_token": access_token, "token_type": "Bearer", "user": user_response }
        logger.debug(f"📦 Resposta final montada: {response_data}")
        
        logger.info("🎉 Login realizado com sucesso! Retornando resposta...")
        return response_data
    except HTTPException as he:
        logger.error(f"🚫 HTTPException no login: {he.detail}")
        raise he
    except Exception as e:
        logger.exception(f"💥 ERRO INESPERADO no login: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")