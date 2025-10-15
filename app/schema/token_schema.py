from pydantic import BaseModel, EmailStr
from typing import Optional
from .user_schema import UserRead



class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserRead

class TokenData(BaseModel):
    email: Optional[str] = None
    role: str = None
    user_id: int = None