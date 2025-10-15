from pydantic import BaseModel, EmailStr
from typing import Optional

#Schema base com os campos comuns
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str
    active: bool = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

#Schema para criação: Pede a senha
class UserCreate(UserBase):
    password: str

#Schema para leitura: Nunca incluir senha
class UserRead(UserBase):
    id: int

    #Configuração para permitir que o Pydantic leia dados de um objeto ORM (modelo SQLModel)
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserRead

class TokenData(BaseModel):
    email: Optional[str] = None
    role: str = None
    user_id: int = None