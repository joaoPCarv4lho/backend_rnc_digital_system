from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from app.core.security import verify_token
from app.crud import get_user_by_email
from app.database import get_db

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    
    return user

def require_role(required_role: str):
    """Factory para criar dependências de role"""
    def role_dependency(current_user = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user
    return role_dependency

require_admin = require_role("admin")
require_operador = require_role("operador")
require_qualidade = require_role("qualidade")
require_tecnico_usinagem = require_role("tecnico_usinagem")
require_tecnico_fundicao = require_role("tecnico_fundicao")
require_engenharia = require_role("engenharia")

