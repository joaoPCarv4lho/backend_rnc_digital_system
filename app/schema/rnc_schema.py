from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

# Importamos os schemas dos quais ele depende
from .user_schema import UserRead
from .part_schema import PartRead
from app import model

class RNCCreate(BaseModel):
    """Schema para criação de um novo RNC"""
    part_id: int = Field(..., description="ID da peça relacionada ao RNC")
    part_code: str = Field(..., description="Código da peça")
    title: str = Field(..., min_length=10, max_length=200, description="Título do RNC")
    critical_level: str = Field(..., description="Nível de criticidade (BAIXA, MEDIA, ALTA, CRITICA)")
    observations: Optional[str] = Field(None, description="Observações iniciais")

    @field_validator('critical_level')
    @classmethod
    def validate_critical_level(cls, v: str) -> str:
        """Valida se o nível de criticidade é válido"""
        valid_levels = ['BAIXA', 'MEDIA', 'ALTA', 'CRITICA']
        if v.upper() not in valid_levels:
            raise ValueError(f"Nível de criticidade deve ser um de: {", ".join(valid_levels)}")
        return v.upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "part_id": 1,
                "part_code": "R-1234",
                "title": "Defeito na peça XYZ",
                "critical_level": "ALTA",
                "observations": "Observações iniciais sobre o defeito"
            }
        }

class QualityAnalysis(BaseModel):
    """Schema para registro da análise feita pela equipe da qualidade"""
    condition: Optional[str] = Field(None, description="Condição atual no fluxo")
    root_cause: Optional[str] = Field(..., min_length=20, description="Causa raiz identificada")
    corrective_action: Optional[str] = Field(None, description="Ação corretiva proposta")
    preventive_action: Optional[str] = Field(None, description="Ação preventiva proposta")
    analysis_observations: Optional[str] = Field(None, description="Observações da análise")
    estimated_rework_time: Optional[int] = Field(None, description="Tempo estimado de retrabalho (minutos)")
    requires_external_support: bool = Field(False, description="Requer suporte externo")
    quality_verified: bool = Field(True, description="Qualidade verificada após retrabalho")
    close_rnc: bool = Field(False, description="Se True, fecha o RNC")
    refused: Optional[bool] = Field(False, description="Se True, fecha o RNC como refugo")

    class Config:
        json_schema_extra = {
            "example": {
                "root_cause": "Falha no processo de soldagem devido temperatura incorreta",
                "corrective_action": "Refazer soldagem com temperatura adequada",
                "preventive_action": "Calibrar equipamento semanalmente",
                "analysis_observations": "Verificar outros produtos do mesmo lote",
                "estimated_rework_time": 60,
                "requires_external_support": False,
                "quality_verified": False,
                "close_rnc": False
            }
        }

class TechnicianRework(BaseModel):
    """Schema para registro do retrabalho pelo técnico"""
    condition: Optional[str] = Field(None, description="Condição atual no fluxo")
    rework_description: str = Field(..., min_length=10, description="Descrição do retrabalho realizado")
    actions_taken: str = Field(..., min_length=20, description="Ações tomadas durante o retrabalho")
    materials_used: Optional[str] = Field(None, description="Materiais utilizados")
    time_spent: Optional[int] = Field(None, gt=0, description="Tempo gasto em minutos")
    rework_observations: Optional[str] = Field(None, description="Observações sobre o retrabalho")

    class Config:
        json_schema_extra = {
            "example": {
                "rework_description": "Retrabalho realizado conforme análise da qualidade",
                "actions_taken": "Soldagem refeita com temperatura correta",
                "materials_used": "Solda estanho 60/40",
                "time_spent": 45,
                "rework_observations": "Peça testada após retrabalho"
            }
        }

class RNCClose(BaseModel):
    """Schema para fechamento manual de um RNC"""
    closing_notes: str = Field(..., min_length=20, description="Notas sobre fechamento")
    resolution_type: Optional[str] = Field(None, description="Tipo de resolução (CONCLUIDO, REFUGO, etc)")

    class Config:
        json_schema_extra = {
            "example": {
                "closing_notes": "RNC fechado após aprovação da qualidade",
                "resolution_type": "CONCLUIDO"
            }
        }

class RNCRead(BaseModel):
    """Schema para leitura completa de um RNC"""
    id: int
    num_rnc: int
    title: str
    status: model.RNCStatus
    condition: model.RNCCondition
    critical_level: str
    observations: Optional[str] = None

    #Informações da peça
    part_id: int
    part_code: str
    part: PartRead

    #Informações de abertura
    open_by_id: int
    open_by: UserRead
    date_of_occurrence: datetime

    #Informações de análise da qualidade
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    analysis_observations: Optional[str] = None
    analysis_date: Optional[datetime] = None
    estimated_rework_time: Optional[int] = None
    requires_external_support: Optional[bool] = None
    quality_verified: Optional[bool] = None

    #Informações de retrabalho
    rework_description: Optional[str] = None
    actions_taken: Optional[str] = None
    materials_used: Optional[str] = None
    time_spent: Optional[int] = None
    rework_observations: Optional[str] = None
    rework_date: Optional[datetime] = None

    #Informações de responsável atual
    current_responsible_id: Optional[int] = None

    #Informações de fechamento
    closed_by_id: Optional[int] = None
    closed_by: Optional[UserRead] = None
    closing_date: Optional[datetime] = None
    closing_notes: Optional[str] = None

    class Config:
        from_attributes = True

class RNCReadSimple(BaseModel):
    """Schema simplificado para listagens de RNC"""
    id: int
    num_rnc: int
    title: str
    status: model.RNCStatus
    condition: model.RNCCondition
    critical_level: str
    part_code: str
    date_of_occurrence: datetime
    closing_date: Optional[datetime] = None
    open_by_id: int
    open_by: UserRead

    class Config:
        from_attributes = True

class RNCReadWithPart(BaseModel):
    """Schema de RNC com informações da peça"""
    id: int
    num_rnc: int
    title: str
    status: model.RNCStatus
    condition: model.RNCCondition
    critical_level: str
    observations: str
    analysis_observations: Optional[str] = None
    rework_observations: Optional[str] = None
    part_code: str
    part: PartRead
    analysis_date: Optional[datetime] = None
    rework_date: Optional[datetime] = None
    date_of_occurrence: datetime
    closing_date: Optional[datetime] = None

    class Config:
        from_attributes = True

#Schemas de Resposta
class RNCListResponse(BaseModel):
    """Schema de resposta para listagem paginada de RNCs"""
    items: list[RNCReadSimple]
    total: int
    page: int
    page_size: int
    total_pages: int

class RNCStatistics(BaseModel):
    """Schema para estatísticas de RNCs"""
    total_rncs: int
    open_rncs: int
    closed_rncs: int
    approved_rncs: int
    refused_rncs: int
    average_resolution_time: Optional[float] = None #em dias

    monthly: list[dict]
    by_status: list[dict]
    by_condition: list[dict]
    class Config:
        json_schema_extra = {
            "example": {
                "total_rncs": 215,
                "open_rncs": 45,
                "closed_rncs": 105,
                "average_resolution_time": 3.5,
                "monthly": [
                    {"month": "2025-01", "count": 12},
                    {"month": "2025-02", "count": 18}
                ],
                "by_status": [
                    {"status": "aberto", "total": 45},
                    {"status": "fechado", "total": 105}
                ],
                "by_condition": [
                    {"condition": "aprovado", "total": 20},
                    {"condition": "refugo", "total": 25}
                ]
            }
        }
