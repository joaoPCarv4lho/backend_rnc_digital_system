from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session
from typing import Annotated

from app import repository, schema, model, service
from app.core.dependencies import require_role, get_current_user
from app.database import get_db

router = APIRouter()

@router.get('/code/{part_code}', response_model=schema.PartRead, status_code=status.HTTP_200_OK, dependencies=[Depends(require_role(model.UserRole.OPERADOR, model.UserRole.TECNICO, model.UserRole.ENGENHARIA, model.UserRole.QUALIDADE))])
async def get_part_by_code(part_code: str, db: Annotated[Session, Depends(get_db)]):
    repo = repository.PartRepository(db)
    part_service = service.PartService(repo)
    try:
        part = part_service.get_part_by_code(part_code)
        return part
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")
