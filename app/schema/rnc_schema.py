from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Importamos os schemas dos quais ele depende
from .user_schema import UserRead
from .part_schema import PartRead

class RNCBase(BaseModel):
    num_rnc: str
    title: str
    status: str
    critical_level: str
    date_of_occurrence: datetime
    part_id: int
    machine_id: Optional[int] = None

class RNCCreate(RNCBase):
    pass

class RNCRead(RNCBase):
    id: int
    opening_date: datetime
    closing_date: Optional[datetime] = None
    open_by_id: int
    
    # Usamos os schemas de leitura para aninhar os dados na resposta da API
    part: PartRead
    open_by_id: UserRead
    
    class Config:
        from_attributes = True