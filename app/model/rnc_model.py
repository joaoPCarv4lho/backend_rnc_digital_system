from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

from .user_model import User
from .machine_model import Machine
from .part_model import Part
from .rnc_defect_model import RNC_Defect
from .rnc_observation_model import RNC_Observation

class RNC(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    num_rnc: str = Field(unique=True, index=True)
    title: str 
    status: str = Field(index=True)
    critical_level: str

    date_of_occurrence: datetime
    opening_date: datetime = Field(default_factory=datetime.utcnow)
    closing_date: Optional[datetime] = None

    part_id: int = Field(foreign_key="part.id")
    machine_id: Optional[int] = Field(default=None, foreign_key="machine.id")
    open_by_id: int = Field(foreign_key="user.id")
    current_responsible_id: Optional[int] = Field(default=None, foreign_key="user.id")
    closed_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    part: Part = Relationship(back_populates="rnc")
    machine: Optional[Machine] = Relationship(back_populates="rnc")
    open_by: "User" = Relationship(back_populates="open_rncs", sa_relationship_kwargs={"foreign_keys": "RNC.open_by_id"})
    current_responsible: "User" = Relationship(back_populates="rncs_responsible", sa_relationship_kwargs={"foreign_keys": "RNC.current_responsible_id"})
    closed_by: "User" = Relationship(back_populates="rncs_closed", sa_relationship_kwargs={"foreign_keys": "RNC.closed_by_id"})

    defects: List[RNC_Defect] = Relationship(back_populates="rnc")
    observations: List[RNC_Observation] = Relationship(back_populates="rnc")