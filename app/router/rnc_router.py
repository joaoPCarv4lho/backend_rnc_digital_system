from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlmodel import Session
from typing import Annotated, Optional

from app import repository, schema, model, service
from app.core.dependencies import require_role, get_current_user
from app.database import get_db

router = APIRouter()

@router.post('/create_rnc', response_model=schema.RNCReadSimple, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role(model.UserRole.OPERADOR))])
async def creating_rnc(rnc_data: schema.RNCCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[model.User, Depends(get_current_user)]):
    repo = repository.RNCRepository(db)
    rnc_service = service.RNCService(repo)
    try:
        rnc = await rnc_service.create(rnc_data, current_user)
        return schema.RNCReadSimple.model_validate(rnc)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")
    

@router.get('/list_rncs', response_model=schema.RNCListResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(require_role(model.UserRole.ADMIN, model.UserRole.QUALIDADE, model.UserRole.TECNICO, model.UserRole.ENGENHARIA))])
async def get_all_rncs(db: Annotated[Session, Depends(get_db)], status: Optional[str] = Query(None), condition: Optional[str] = Query(None)):
    """Lista todos os rncs que foram finalizados"""
    repo = repository.RNCRepository(db)
    rnc_service = service.RNCService(repo)
    try:
        rncs = rnc_service.get_filtered_rncs(status=status, condition=condition)
        return schema.RNCListResponse(
            items=rncs,
            total=len(rncs),
            page=1,
            page_size=len(rncs),
            total_pages=1
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e :
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")

@router.get('/list/to_be_reworked', response_model=schema.RNCListResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(require_role(model.UserRole.ADMIN, model.UserRole.TECNICO))])
async def get_rncs_to_be_reworkeds(db: Annotated[Session, Depends(get_db)]):
    """Lista todos os rncs que precisam ser retrabalhados"""
    repo = repository.RNCRepository(db)
    rnc_service = service.RNCService(repo)
    try:
        rncs_to_be_reworkeds = rnc_service.get_rncs_pending_rework()
        return schema.RNCListResponse(
            items=rncs_to_be_reworkeds.items,
            total=len(rncs_to_be_reworkeds.items),
            page=1,
            page_size=len(rncs_to_be_reworkeds.items),
            total_pages=1
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")

@router.get('/partCode/{partCode}', response_model=schema.RNCReadWithPart, status_code=status.HTTP_200_OK, dependencies=[Depends(require_role(model.UserRole.ADMIN, model.UserRole.QUALIDADE, model.UserRole.TECNICO, model.UserRole.ENGENHARIA))])
async def get_rnc_by_part_code(partCode: str, db: Annotated[Session, Depends(get_db)]):
    """Busca um RNC pelo código da peça"""
    repo = repository.RNCRepository(db)
    rnc_service = service.RNCService(repo)
    try:
        rnc = rnc_service.get_rnc_by_part_code(partCode)
        return rnc
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e :
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")

@router.get('/list/open/user', response_model=schema.RNCListResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(require_role(model.UserRole.OPERADOR, model.UserRole.TECNICO, model.UserRole.ENGENHARIA, model.UserRole.QUALIDADE))])
async def get_user_rncs(db: Annotated[Session, Depends(get_db)], current_user: Annotated[model.User, Depends(get_current_user)]):
    """Lista todos os RNCs abertos pelo usuário autenticado"""
    repo = repository.RNCRepository(db)
    rnc_service = service.RNCService(repo)
    try:
        rncs = rnc_service.get_rncs_opened_by_user(current_user)
        return rncs
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e :
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")
    
@router.get('/list/analysis/user', response_model=schema.RNCListResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(require_role(model.UserRole.ENGENHARIA, model.UserRole.QUALIDADE))])
async def get_rncs_analysis_by_user(db: Annotated[Session, Depends(get_db)], current_user: Annotated[model.User, Depends(get_current_user)]):
    """Lista todos os RNCs analisados pelo usuário autenticado"""
    repo = repository.RNCRepository(db)
    rnc_service = service.RNCService(repo)
    try:
        rncs = rnc_service.get_rncs_analyzed_by_user(current_user)
        return rncs
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")

@router.get('/list/rework/user', response_model=schema.RNCListResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(require_role(model.UserRole.TECNICO))])
async def get_rncs_rework_by_user(db: Annotated[Session, Depends(get_db)], current_user: Annotated[model.User, Depends(get_current_user)]):
    """Lista todos os RNCs retrabalhados pelo usuário autenticado"""
    repo = repository.RNCRepository(db)
    rnc_service = service.RNCService(repo)
    try:
        rncs = rnc_service.get_rncs_reworked_by_user(current_user)
        return rncs
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")

@router.get('/statistics/', response_model=schema.RNCStatistics, status_code=status.HTTP_200_OK, dependencies=[Depends(require_role(model.UserRole.ADMIN))])
async def get_statistics(db: Annotated[Session, Depends(get_db)]):
    """Busca estatísticas a respeito dos RNCs"""
    repo = repository.RNCRepository(db)
    s_service = service.RNCService(repo)
    try:
        statistics = s_service.get_statistics()
        return statistics
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")

@router.patch('/analysis/{num_rnc}', response_model=schema.RNCRead, status_code=status.HTTP_200_OK, dependencies=[Depends(require_role(model.UserRole.QUALIDADE, model.UserRole.ENGENHARIA))])
async def register_analysis(num_rnc: int, analysis_data: schema.QualityAnalysis, db: Annotated[Session, Depends(get_db)], current_user: Annotated[model.User, Depends(get_current_user)]):
    """Rota para registrar análise da qualidade"""
    repo = repository.RNCRepository(db)
    rnc_service = service.RNCService(repo)
    try:
        rnc_update = await rnc_service.register_quality_analysis(num_rnc, analysis_data, current_user)
        return rnc_update
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")

@router.patch('/rework/{num_rnc}', response_model=schema.RNCRead, status_code=status.HTTP_200_OK, dependencies=[Depends(require_role(model.UserRole.TECNICO, model.UserRole.TECNICO))])
async def register_rework(num_rnc: int, rework_data: schema.TechnicianRework, db: Annotated[Session, Depends(get_db)], current_user: Annotated[model.User, Depends(get_current_user)]):
    """Rota para registrar retrabalho no RNC"""
    repo = repository.RNCRepository(db)
    rnc_service = service.RNCService(repo)
    try:
        rnc_rework = await rnc_service.register_technician_rework(num_rnc, rework_data, current_user)
        return rnc_rework
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")
