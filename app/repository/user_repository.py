from sqlmodel import Session, select
from app import model, schema


class UserRepository:
    """Camada de acesso e manipulação de dados de usuário"""

    def _init_(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> model.User | None:
        return self.db.exec(select(model.User).where(model.User.email == email)).first()

    def get_by_id(self, user_id: int) -> model.User | None:
        return self.db.get(model.User, user_id)

    def create(self, user_data: schema.UserCreate) -> model.User:
        if self.get_by_email(user_data.email):
            raise ValueError("Email already registered")

        db_user = model.User(
            name=user_data.name,
            email=user_data.email,
            role=user_data.role,
            active=user_data.active
        )
        db_user.set_password(user_data.password)

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def list_all(self) -> list[model.User]:
        return list(self.db.exec(select(model.User)))

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True