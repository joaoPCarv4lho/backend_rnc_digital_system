from .user_schema import UserBase, UserCreate, UserRead, UserUpdate, UserLogin
from .rnc_schema import RNCCreate, RNCRead, QualityAnalysis, TechnicianRework, RNCClose, RNCListResponse, RNCReadSimple, RNCReadWithPart, RNCStatistics
from .part_schema import PartBase, PartCreate, PartRead
from .token_schema import Token, TokenData

# Opcional: define o que é exportado quando se usa "from app.schemas import *"
__all__ = [
    "PartBase", "PartCreate", "PartRead",
    "UserBase", "UserCreate", "UserRead", "UserUpdate", "UserLogin",
    "Token", "TokenData",
    "RNCCreate", "RNCRead", "QualityAnalysis", "TechnicianRework", "RNCClose", "RNCListResponse", "RNCReadSimple", "RNCReadWithPart", "RNCStatistics"
]