from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Importamos os schemas dos quais ele depende
from .user_schema import UserRead
from .part_schema import PartRead
from app import model

class RNCCreate(BaseModel):
    part_id: int
    status: model.RNCStatus = model.RNCStatus.ABERTO
    condition: model.RNCCondition = model.RNCCondition.EM_ANALISE
    date_of_occurrence: datetime
    critical_level: str
    title: str
    observations: Optional[str] = None
    open_by_id: int

class RNCUpdate(BaseModel):
    title: Optional[str] = None
    critical_level: Optional[str] = None
    status: Optional[model.RNCStatus] = None
    condition: Optional[model.RNCCondition] = None
    observations: Optional[str] = None
    current_responsible_id: Optional[int] = None
    closed_by_id: Optional[int] = None

class RNCRead(BaseModel):
    id: int
    num_rnc: int
    title: str
    status: model.RNCStatus
    condition: model.RNCCondition
    observations: Optional[str] = None
    part_id: int
    open_by_id: int
    current_responsible_id: Optional[int] = None
    closed_by_id: Optional[int] = None
    opening_date: datetime
    closing_date: Optional[datetime] = None

    # Usamos os schemas de leitura para aninhar os dados na resposta da API
    part: PartRead
    open_by: UserRead
    closed_by: Optional[UserRead] = None
    
    class Config:
        from_attributes = True
