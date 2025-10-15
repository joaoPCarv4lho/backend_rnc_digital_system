from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship

class Part(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    part_code: str = Field(index=True, unique=True)
    description: str
    client: Optional[str] = None
    active: bool = Field(default=True)

    rnc: List["RNC"] = Relationship(back_populates="part")
