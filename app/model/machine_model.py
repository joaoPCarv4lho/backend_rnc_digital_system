from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .rnc_model import RNC

class Machine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tag_machine: str = Field(index=True, unique=True)
    name: str 
    sector: Optional[str] = None
    active: bool = Field(default=True)

    rnc: List["RNC"] = Relationship(back_populates="machine")