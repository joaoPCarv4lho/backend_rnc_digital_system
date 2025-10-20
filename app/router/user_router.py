from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app import crud, schema
from app.database import get_db
from app.core.dependencies import require_admin

router = APIRouter()


@router.post('/register', response_model=schema.UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    try:
        user = crud.create_user(db, user)
        user_response = schema.UserRead(email=user.email, name=user.name, role=user.role, active=user.active, id=user.id)
        return user_response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

#rota apenas para usuários do tipo admin
@router.post('/creating', response_model=schema.UserRead, status_code=status.HTTP_201_CREATED)
async def creating_users( user: schema.UserCreate, db: Session = Depends(get_db), current_user: schema.UserRead = Depends(require_admin)):
    """Cria um novo usuário"""

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário sem permissão!")
    try:
        user = crud.create_user(db, user)
        return schema.UserRead(email=user.email, name=user.name, role=user.role, active=user.active, id=user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
