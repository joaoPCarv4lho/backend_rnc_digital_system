from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from typing import Annotated

from app.core.security import verify_token
from app.repository.user_repository import UserRepository
from app.database import get_db
from app import model

security = HTTPBearer()

async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)], db: Annotated[Session, Depends(get_db)]) -> model.User:
    """Retorna o usuário atual a partir do token JWT gerado"""

    token = credentials.credentials
    payload = verify_token(token)

    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token!", headers={"WWW-Authenticate": "Bearer"})

    user_repo = UserRepository(db)
    user = user_repo.get_by_email(payload["sub"])

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!", headers={"WWW-Authenticate": "Bearer"})
    
    if not user.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user!")

    return user

def require_role(*allowed_roles: model.UserRole):
    """Garante que o usuário logado possua um dos papéis permitidos"""
    def role_dependency(current_user: model.User = Depends(get_current_user)):
        if current_user.role not in allowed_roles and current_user.role != model.UserRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Permission denied. Required roles: {', '.join(r.value for r in allowed_roles)}")
        return current_user
    return role_dependency

require_admin = require_role(model.UserRole.ADMIN)
require_operador = require_role(model.UserRole.OPERADOR)
require_qualidade = require_role(model.UserRole.QUALIDADE)
require_tecnico = require_role(model.UserRole.TECNICO)
require_engenharia = require_role(model.UserRole.ENGENHARIA)

