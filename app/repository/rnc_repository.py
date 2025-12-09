from sqlmodel import Session, select, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from app import schema, model
from typing import Optional

class RNCRepository:
    """Repositório para operações de RNC (Registro de Não Conformidade)"""
    def __init__(self, db: Session):
        self.db = db

    def _get_current_utc_datetime(self) -> datetime:
        """Retorna a data/hora atual em UTC"""
        return datetime.now(timezone.utc)
    
    def _apply_eager_loading(self, statement):
        """Aplica eager loading padrão para relacionamentos do RNC"""
        return statement.options(
            selectinload(model.RNC.part),
            selectinload(model.RNC.open_by)
        )

    def get_by_num(self, num_rnc: int, lock: bool = False) -> Optional[model.RNC]:
        """
        Busca um RNC pelo número
        
        Args:
            num_rnc: Número do RNC
            lock: Se True, aplica bloqueio pessimista (FOR UPDATE)
        Returns:
            RNC encontrado ou None
        """
        statement = select(model.RNC).where(model.RNC.num_rnc == num_rnc)
        if lock:
            statement = statement.with_for_update()
        return self.db.exec(statement).first()

    def get_rnc_by_part_code(self, part_code: str) -> Optional[model.RNC]:
        """
        Retorna o RNC aberto associado a um código de peça
        
        Args:
            part_code: Código da peça
        Returns: 
            RNC encontrado ou None
        """
        statement = select(model.RNC).where(
            model.RNC.part_code == part_code,
            model.RNC.status == model.RNCStatus.ABERTO.value
        )
        statement = self._apply_eager_loading(statement)
        return self.db.exec(statement).first()

    def search_rnc_opened_by_user(self, user_id: int, limit: int = 100, offset: int = 0) -> list[model.RNC]:
        """
        Retorna todos os RNCs abertos por um usuário específico
        
        Args:
            user_id: ID do Usuário logado
            limit: Limite de resultados
            offset: Offser para paginação
        Returns:
            Lista de RNCs
        """
        statement = (
            select(model.RNC)
            .where(model.RNC.open_by_id == user_id)
            .order_by(model.RNC.date_of_occurrence.desc())
            .limit(limit).offset(offset)
        )
        statement = self._apply_eager_loading(statement)
        return self.db.exec(statement).all()
    
    def search_rnc_rework_by_user(self, user_id: int, limit: int = 100, offset: int = 0) -> list[model.RNC]:
        """
        Retorna todos os RNCs retrabalhados por um usuário específico
        """
        statement = (
            select(model.RNC)
            .where(model.RNC.rework_user_id == user_id)
            .order_by(model.RNC.rework_date.desc())
            .limit(limit).offset(offset)
        )
        statement = self._apply_eager_loading(statement)
        return self.db.exec(statement).all()

    def search_rnc_by_analysis_user(self, user_id: int, limit: int = 100, offset: int = 0) -> list[model.RNC]:
        """
        Retorna todos os RNCs analisados por um usuário
        """
        statement = (
            select(model.RNC)
            .where(model.RNC.analysis_user_id == user_id)
            .order_by(model.RNC.analysis_date.desc())
            .limit(limit).offset(offset)
        )
        statement = self._apply_eager_loading(statement)
        return self.db.exec(statement).all()

    
    def list_all(self, status: Optional[str] = None, condition: Optional[str] = None, limit: int = 1000, offset: int = 0) -> list[model.RNC]:
        """
        Lista todos os RNCs com filtros opcionais
        
        Args:
            status: Filtro por status (ABERTO, FECHADO)
            condition: Filtro por condição (EM_ANALISE, etc)
            limit: Limite de resultados
            offset: Offset para paginação
        Returns:
            Lista de RNCs
        """
        statement = select(model.RNC).limit(limit).offset(offset)
        if status:
            statement = statement.where(model.RNC.status == status)
        if condition:
            statement = statement.where(model.RNC.condition == condition)
        
        statement = self._apply_eager_loading(statement)

        return self.db.exec(statement).all()
    
    def list_by_rework_status(self, pending: bool) -> list[model.RNC]:
        """
        Lista RNCs por status de retrabalho

        pending=True: RNCs que precisam ser retrabalhados
        pending=False: RNCs que já foram retrabalhados
        """
        if pending:
            statement = select(model.RNC).where(
                model.RNC.condition == model.RNCCondition.AGUARDANDO_RETRABALHO.value
            )
        else:
            statement = select(model.RNC).where(
                model.RNC.condition == model.RNCCondition.AGUARDANDO_VERIFICACAO.value
            )
        statement = self._apply_eager_loading(statement)
        return self.db.exec(statement).all()
    
    def list_by_analysis_status(self, pending: bool) -> list[model.RNC]:
        """
        Lista RNCs por status de análise

        pending=True: RNCs que precisam ser analisados
        pending=False: RNCs que já foram analisados
        """
        analysis_pending_states = [model.RNCCondition.EM_ANALISE.value, model.RNCCondition.AGUARDANDO_VERIFICACAO.value]
        if pending:
            statement = select(model.RNC).where(
                model.RNC.condition.in_(analysis_pending_states)
            )
        else:
            statement = select(model.RNC).where(
                model.RNC.condition != "em_analise"
            )
        statement = self._apply_eager_loading(statement)
        return self.db.exec(statement).all()
    
    def create_rnc(self, rnc_data: schema.RNCCreate, open_by_id: int) -> model.RNC:
        """
        Cria um novo RNC no banco com validações otimizadas
        
        Args:
            rnc_data: Dados do RNC a ser criado
            open_by_id: ID do usuário que está abrindo o RNC
        Returns:
            RNC criado
        Raises:
            ValueError: Se já existir um RNC aberto para a peça
        """
        existing = self.get_rnc_by_part_code(rnc_data.part_code)
        if existing:
            raise ValueError(f"A peça (ID {rnc_data.part_id}) já está associada ao RNC ativo n° {existing.num_rnc}.")
        next_num = model.RNC.generate_next_num_rnc(self.db)

        db_rnc = model.RNC(
            num_rnc=next_num,
            title=rnc_data.title,
            critical_level=rnc_data.critical_level,
            date_of_occurrence=self._get_current_utc_datetime(),
            part_id=rnc_data.part_id,
            observations=rnc_data.observations,
            part_code=rnc_data.part_code,
            status=model.RNCStatus.ABERTO.value,
            condition=model.RNCCondition.EM_ANALISE.value,
            open_by_id=open_by_id
        )

        self.db.add(db_rnc)
        self.db.commit()
        self.db.refresh(db_rnc)
        return db_rnc
    
    def register_quality_analysis(self, num_rnc: int, analysis_data: schema.QualityAnalysis, quality_user: model.User) -> model.RNC:
        """
        Registra o apontamento/análise feita pela qualidade
        
        Args:
            num_rnc: Número do RNC
            analysis_data: Dados da análise da qualidade
            quality_user: Usuário da qualidade que está fazendo a análise
        Returns:
            RNC atualizado
        Raises:
            ValueError: Se o RNC não for encontrado
        """
        db_rnc = self.get_by_num(num_rnc, lock=True)
        if not db_rnc:
            raise ValueError(f"RNC n° {num_rnc} não encontrado.")
        update_data = analysis_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_rnc, field, value)
        db_rnc.analysis_user_id = quality_user.id
        db_rnc.analysis_by = quality_user
        db_rnc.analysis_date = self._get_current_utc_datetime()
        
        if analysis_data.close_rnc:
            if analysis_data.refused:
                db_rnc.condition = model.RNCCondition.REFUGO.value
                db_rnc.status = model.RNCStatus.FECHADO.value
                db_rnc.closed_by_id = quality_user.id
                db_rnc.closing_date = self._get_current_utc_datetime()
            else:
                db_rnc.condition = model.RNCCondition.APROVADO.value
                db_rnc.status = model.RNCStatus.FECHADO.value
                db_rnc.closed_by_id = quality_user.id
                db_rnc.closing_date = self._get_current_utc_datetime()
        else:
            db_rnc.condition = model.RNCCondition.AGUARDANDO_RETRABALHO.value

        self.db.commit()
        self.db.refresh(db_rnc)
        return db_rnc
    
    def register_technician_rework(self, num_rnc: int, rework_data: schema.TechnicianRework, technician_user: model.User) -> model.RNC:
        """
        Registra o retrabalho realizado pelo técnico
        
        Args:
            num_rnc: Número do RNC
            rework_data: Dados do retrabalho realizado
            technician_user: Usuário técnico que realizou o retrabalho
        Returns:
            RNC atualizado
        Raises:
            ValueError: Se o RNC não for encontrado
        """
        db_rnc = self.get_by_num(num_rnc)
        if not db_rnc:
            raise ValueError(f"RNC n° {num_rnc} não encontrado")
        update_data = rework_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_rnc, field, value)
        db_rnc.rework_user_id = technician_user.id
        db_rnc.rework_by = technician_user
        db_rnc.rework_date = self._get_current_utc_datetime()
        db_rnc.condition = model.RNCCondition.AGUARDANDO_VERIFICACAO.value

        self.db.commit()
        self.db.refresh(db_rnc)
        return db_rnc
    
    def close_rnc(self, num_rnc: int, closing_user: model.User, closing_notes: Optional[str] = None) -> model.RNC:
        """
        Fecha um RNC manualmente
        
        Args:
            num_rnc: Número do RNC
            closing_user: Usuário que está fechando o RNC
            closing_notes: Observações sobre o fechamento
        Returns:
            RNC fechado
        Raises:
            ValueError: Se o RNC não for encontrado
        """
        db_rnc = self.get_by_num(num_rnc, lock=True)
        if not db_rnc:
            raise ValueError(f"RNC n° {num_rnc} não encontrado.")
        db_rnc.status = model.RNCStatus.FECHADO.value
        db_rnc.closed_by_id = closing_user.id
        db_rnc.closing_date = self._get_current_utc_datetime()
        db_rnc.condition = model.RNCCondition.CONCLUIDO.value

        if closing_notes:
            db_rnc.closing_notes = closing_notes
        self.db.commit()
        self.db.refresh(db_rnc)
        return db_rnc