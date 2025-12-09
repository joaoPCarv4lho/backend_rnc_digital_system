from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from datetime import timedelta
from fastapi.responses import JSONResponse
from sqlmodel import Session
from typing import Annotated
from jose import jwt
import traceback
import logging

from app.repository.auth_repository import AuthRepository
from app.core.security import create_access_token, create_refresh_token, verify_token
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
        user = auth_service.authenticate_user(data_login)
        
        if not user:
            logger.error("❌ Autenticação falhou - usuário não encontrado ou senha incorreta")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        if not user.active:
            logger.error("❌ Usuário inativo")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive User!")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_IN_MINUTES)
        token_data = { "sub": user.email, "role": user.role, "user_id": user.id }
        access_token = create_access_token(data=token_data, expires_delta=access_token_expires)

        refresh__token__data = {"sub": user.email, "role": user.role, "user_id": user.id}
        refresh__token = create_refresh_token(refresh__token__data, expires_delta=timedelta(days=7))

        if not access_token:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create access token!")
        user_response = schema.UserRead(email=user.email, name=user.name, role=user.role, active=user.active, id=user.id)

        response_data = { "access_token": access_token, "token_type": "Bearer", "user": user_response }

        res_data = JSONResponse({ "access_token": access_token, "token_type": "Bearer", "user": user_response.model_dump() })
        res_data.set_cookie(
            key="refresh_token",
            value=refresh__token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=7 * 24 * 60 * 60
        )

        return response_data
    except HTTPException as he:
        logger.error(f"🚫 HTTPException no login: {he.detail}")
        raise he
    except Exception as e:
        logger.exception(f"💥 ERRO INESPERADO no login: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.post("/refresh", response_model=schema.Token)
async def refresh_token(request: Request, response: Response):
    refresh__token = request.cookies.get("refresh_token")
    if not refresh__token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sem refresh Token")
    
    try:
        payload = jwt.decode(refresh__token, settings.REFRESH_SECRET_KEY, algorithms=settings.ALGORITHM)
        role = payload.get("role")
        user_id = payload.get("user_id")
        sub = payload.get("sub")
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh Token inválido")
    new_access_token = create_access_token(data={"sub": sub, "role": role, "user_id": user_id})

    return {"access_token": new_access_token}