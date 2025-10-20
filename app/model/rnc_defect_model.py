from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class RNC_Defect(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    defect_code: str
    description_defect: Optional[str] = None
    quantity: int

    rnc_id: int = Field(foreign_key="rnc.id")
    rnc: "RNC" = Relationship(back_populates="defects")