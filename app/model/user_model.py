from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum
import bcrypt

if TYPE_CHECKING:
    from .rnc_model import RNC
class UserRole(str, Enum):
    ADMIN = "admin"
    OPERADOR = "operador"
    QUALIDADE = "qualidade"
    TECNICO = "tecnico"
    ENGENHARIA = "engenharia"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    password_hash: str = Field(max_length=255) 
    role: str
    active: bool = Field(default=True)

    open_rncs: List["RNC"] = Relationship(back_populates="open_by", sa_relationship_kwargs={"foreign_keys": "RNC.open_by_id"})
    analysis_rncs: List["RNC"] = Relationship(back_populates="analysis_by", sa_relationship_kwargs={"foreign_keys": "RNC.analysis_user_id"})
    rework_rncs: List["RNC"] = Relationship(back_populates="rework_by", sa_relationship_kwargs={"foreign_keys": "RNC.rework_user_id"})
    rncs_closed: List["RNC"] = Relationship(back_populates="closed_by", sa_relationship_kwargs={"foreign_keys": "RNC.closed_by_id"})

    def set_password(self, password: str):

        password_bytes = password.encode('utf-8')[:72]
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]

        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        try:
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]

            return bcrypt.checkpw(password_bytes, self.password_hash.encode('utf-8'))
        except Exception:
            return False