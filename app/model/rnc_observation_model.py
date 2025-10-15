from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .rnc_model import RNC
    from .user_model import User

class RNC_Observation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    observation_data: datetime = Field(default_factory=datetime.utcnow)
    observation_type: str
    observation: str

    rnc_id: int = Field(foreign_key="rnc.id")
    rnc: "RNC" = Relationship(back_populates="observations")

    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="observations")

