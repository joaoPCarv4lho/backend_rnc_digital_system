from sqlmodel import Session, select
from datetime import datetime
from app import schema, model
from typing import Optional

class RNCRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_rnc_by_part(self, part_id: int) -> model.RNC:
        statement = select(model.RNC).where(
            model.RNC.part_id == part_id, 
            model.RNC.status != model.RNCStatus.FECHADO.value
        )
        return self.db.exec(statement).first()

    def get_by_user_id(self, user_id: int) -> list[model.RNC]:
        """Retorna todos os RNCs abertos por um usuário específico"""
        statement = select(model.RNC).where(model.RNC.open_by_id == user_id).order_by(model.RNC.opening_date.desc())
        return self.db.exec(statement).all()
    
    def create_rnc(self, rnc_data: schema.RNCCreate, open_by_id: int) -> model.RNC:
        """Cria um novo RNC no banco"""

        existing = self.get_active_rnc_by_part(rnc_data.part_id)
        if existing:
            raise ValueError(f"A peça (ID {rnc_data.part_id}) já está associada ao RNC ativo n° {existing.num_rnc}.")

        next_num = model.RNC.generate_next_num_rnc(self.db)
        db_rnc = model.RNC(
            num_rnc=next_num,
            title=rnc_data.title,
            critical_level=rnc_data.critical_level,
            date_of_occurrence=rnc_data.date_of_occurrence,
            part_id=rnc_data.part_id,
            observations=rnc_data.observations,
            status=model.RNCStatus.ABERTO.value,
            condition=model.RNCCondition.EM_ANALISE.value,
            open_by_id=open_by_id
        )

        self.db.add(db_rnc)
        self.db.commit()
        self.db.refresh(db_rnc)
        return db_rnc
    
    def get_by_num(self, num_rnc: int) -> model.RNC:
        """Busca um RNC pelo id"""
        statement = select(model.RNC).where(model.RNC.num_rnc == num_rnc)
        return self.db.exec(statement).first()

    def list_all(self, status: Optional[str] = None, condition: Optional[str] = None) -> list[model.RNC]:
        """Busca todos os RNCs"""
        statement = select(model.RNC)
        if status:
            statement = statement.where(model.RNC.status == status)
        if condition:
            statement = statement.where(model.RNC.condition == condition)
        return list(self.db.exec(statement))

    def update_rnc(self, num_rnc: int, rnc_update: schema.RNCUpdate, current_user: model.User, fechando_rnc: bool = False) -> model.RNC:
        """Atualiza uma RNC existente"""   
        db_rnc = self.get_by_num(num_rnc)    
        update_data = rnc_update.model_dump(exclude_unset=True)

        update_data["current_responsible_id"] = current_user.id
        for field, value in update_data.items():
            setattr(db_rnc, field, value)

        if fechando_rnc:
            db_rnc.closed_by = current_user
            db_rnc.closed_by_id = current_user.id
            db_rnc.closing_date = datetime.utcnow()

        self.db.add(db_rnc)
        self.db.commit()
        self.db.refresh(db_rnc)
        return db_rnc