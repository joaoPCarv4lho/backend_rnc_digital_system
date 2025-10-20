from .part_schema import PartBase, PartCreate, PartRead
from .user_schema import UserBase, UserCreate, UserRead, UserUpdate, UserLogin
from .token_schema import Token, TokenData
from .rnc_schema import RNCBase, RNCCreate, RNCRead

# Opcional: define o que é exportado quando se usa "from app.schemas import *"
__all__ = [
    "PartBase", "PartCreate", "PartRead",
    "UserBase", "UserCreate", "UserRead", "UserUpdate", "UserLogin",
    "Token", "TokenData",
    "RNCBase", "RNCCreate", "RNCRead",
]