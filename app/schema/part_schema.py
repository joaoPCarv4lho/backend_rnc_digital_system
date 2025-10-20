from pydantic import BaseModel
from typing import Optional

class PartBase(BaseModel):
    part_code: str
    description: str
    client: Optional[str] = None
    active: bool = True

class PartCreate(PartBase):
    pass

class PartRead(PartBase):
    id: int

    class Config:
        from_attributes = True