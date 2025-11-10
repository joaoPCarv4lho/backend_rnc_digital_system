from sqlmodel import Field, SQLModel, Relationship, Session, select
from datetime import datetime
from typing import Optional
from enum import Enum

from .user_model import User
from .part_model import Part

class RNCStatus(str, Enum):
    ABERTO = "aberto"
    FECHADO = "fechado"

class RNCCondition(str, Enum):
    EM_ANALISE = "em_analise"
    APROVADO = "aprovado"
    REFUGO = "refugo"
    RETRABALHO = "retrabalho"

class RNC(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    num_rnc: int = Field(default=None, unique=True, index=True)
    title: str 
    status: str = Field(index=True)
    condition: str = Field(index=True)
    critical_level: str
    observations: str = Field(default=None)
    part_code: str = Field(index=True, unique=True)

    date_of_occurrence: datetime
    opening_date: datetime = Field(default_factory=datetime.utcnow)
    closing_date: Optional[datetime] = None

    part_id: int = Field(foreign_key="part.id")
    open_by_id: int = Field(foreign_key="user.id")
    current_responsible_id: Optional[int] = Field(default=None, foreign_key="user.id")
    closed_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    part: Part = Relationship(back_populates="rnc")
    open_by: "User" = Relationship(back_populates="open_rncs", sa_relationship_kwargs={"foreign_keys": "RNC.open_by_id"})
    current_responsible: "User" = Relationship(back_populates="rncs_responsible", sa_relationship_kwargs={"foreign_keys": "RNC.current_responsible_id"})
    closed_by: "User" = Relationship(back_populates="rncs_closed", sa_relationship_kwargs={"foreign_keys": "RNC.closed_by_id"})

    @staticmethod
    def generate_next_num_rnc(session: Session) -> int:
        """Gera o próximo número do RNC (até 8 dígitos)"""
        last_rnc = session.exec(select(RNC).order_by(RNC.num_rnc.desc())).first()
        next_number = (last_rnc.num_rnc + 1) if last_rnc and last_rnc.num_rnc else 1
        if next_number > 99999999:
            raise ValueError("Limite máximo de 8 dígitos atingido para num_rnc")
        return next_number