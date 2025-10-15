from sqlmodel import Session, select
from passlib.context import CryptContext

from app import model, schema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    """Busca o primeiro usuário encontrado com o email fornecido"""

    user = db.exec(select(model.User).where(model.User.email == email)).first()
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not user.check_password(password):
        return False
    
    return user

def create_user(db: Session, user_data: schema.UserCreate):
    """Cria um novo usuário no banco"""

    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise ValueError("Email already registered")

    #Cria novo objeto do usuário
    db_user = model.User(**user_data.model_dump(exclude={"password"}))
    db_user.set_password(user_data.password)

    #define a senha usando o método da classe
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user