from pydantic import BaseModel, EmailStr
from typing import Optional
from app import model

#Schema base com os campos comuns
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: Optional[model.UserRole] = model.UserRole.OPERADOR
    active: bool = True

#Schema para criação: Pede a senha
class UserCreate(UserBase):
    password: str

#Schema para realização do login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

#Schema para leitura: Nunca incluir senha
class UserRead(UserBase):
    id: int

    #Configuração para permitir que o Pydantic leia dados de um objeto ORM (modelo SQLModel)
    class Config:
        from_attributes = True

#schema para atualização dos dados do usuário
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[model.UserRole] = None
    active: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserRead

class TokenData(BaseModel):
    email: Optional[str] = None
    role: str = None
    user_id: int = None