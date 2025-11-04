from sqlmodel import Session, select
from datetime import datetime
from app import schema, model

class PartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_code(self, part_code: str) -> model.Part:
        """Busca uma peça pelo código"""
        statement = select(model.Part).where(model.Part.part_code == part_code)
        return self.db.exec(statement).first()