from sqlmodel import Session, select
from app import model

class AuthRepository:

    def __init__(self, db: Session):
        self.db = db

    def authenticate(self, email: str) -> model.User | None:
        return self.db.exec(select(model.User).where(model.User.email == email)).first()
    
