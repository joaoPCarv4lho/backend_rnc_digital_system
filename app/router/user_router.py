from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Annotated

from app.repository.user_repository import UserRepository
from app.service.user_service import UserService
from app.core.dependencies import require_role
from app.database import get_db
from app import model, schema

router = APIRouter()


@router.post('/register', response_model=schema.UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: schema.UserCreate, db: Annotated[Session, Depends(get_db)]):
    repo = UserRepository(db)
    service = UserService(repo)
    try:
        user = service.create_user(user_data)
        return schema.UserRead.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

#rota apenas para usuários do tipo admin
@router.post('/creating', response_model=schema.UserRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role(model.UserRole.ADMIN))])
async def creating_users( user_data: schema.UserCreate, db: Annotated[Session, Depends(get_db)]):
    """Cria um novo usuário"""
    repo = UserRepository(db)
    service = UserService(repo)
    try:
        user = service.create_user(user_data)
        return schema.UserRead.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

