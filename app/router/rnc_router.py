from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session
from typing import Annotated

from app import repository, schema, model, service
from app.core.dependencies import require_role, get_current_user
from app.database import get_db

router = APIRouter()

@router.post('/create_rnc', response_model=schema.RNCRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role(model.UserRole.OPERADOR))])
async def creating_rnc(rnc_data: schema.RNCCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[model.User, Depends(get_current_user)]):
    repo = repository.RNCRepository(db)
    rnc_service = service.RNCService(repo)
    try:
        rnc = rnc_service.create(rnc_data, current_user)
        return schema.RNCRead.model_validate(rnc)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")
    

@router.get('/list_rncs', response_model=list[schema.RNCRead], status_code=status.HTTP_200_OK, dependencies=[Depends(require_role(model.UserRole.ADMIN, model.UserRole.QUALIDADE, model.UserRole.TECNICO_FUNDICAO, model.UserRole.ENGENHARIA))])
async def get_all_rncs_active(db: Annotated[Session, Depends(get_db)]):
    """Lista todos os rncs que foram finalizados"""
    repo = repository.RNCRepository(db)
    rnc_service = service.RNCService(repo)
    try:
        rncs = rnc_service.get_all_rncs()
        return rncs
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e :
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error.")
    

@router.patch('/update_rnc/{num_rnc}', response_model=schema.RNCRead, status_code=status.HTTP_200_OK, dependencies=[Depends(require_role(model.UserRole.QUALIDADE, model.UserRole.ENGENHARIA, model.UserRole.TECNICO_FUNDICAO, model.UserRole.TECNICO_USINAGEM))])
async def update_rnc(num_rnc: int, rnc_update: schema.RNCUpdate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[model.User, Depends(get_current_user)]):
    """Atualiza um RNC específico"""
    repo = repository.RNCRepository(db)
    rnc_service = service.RNCService(repo)
    try:
        rnc_update = rnc_service.update_rnc(num_rnc, rnc_update, current_user)
        return rnc_update
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")
