from sqlmodel import Field, SQLModel, Relationship, Session, select, func, Column, Text
from datetime import datetime
from typing import Optional
from enum import Enum

from .user_model import User
from .part_model import Part

class RNCStatus(str, Enum):
    """Status do RNC no Sistema"""
    ABERTO = "aberto"
    FECHADO = "fechado"

class RNCCondition(str, Enum):
    """Condição atual do RNC no fluxo de trabalho"""
    EM_ANALISE = "em_analise"
    AGUARDANDO_RETRABALHO = "aguardando_retrabalho"
    AGUARDANDO_VERIFICACAO = "aguardando_verificacao"
    APROVADO = "aprovado"
    REFUGO = "refugo"

class RNCCriticalLevel(str, Enum):
    """Nível de criticidade do RNC"""
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"

class RNC(SQLModel, table=True):
    """
    Modelo de Registro de Não Conformidade (RNC)
    Representa um registro de não conformidade que passa por análise da qualidade e retrabalho técnico até sua solução
    """
    #Identificação e informações básicas
    id: Optional[int] = Field(default=None, primary_key=True)
    num_rnc: int = Field(default=None, unique=True, index=True, description="Número único do RNC")
    title: str = Field(max_length=100, description="Título/Resumo do RNC")
    status: str = Field(index=True, description="Status do RNC (aberto/fechado)")
    condition: str = Field(index=True, description="Condição atual no fluxo")
    critical_level: str = Field(description="Nível de criticidade")
    observations: Optional[str] = Field(default=None, sa_column=Column(Text), description="Observações iniciais")
    
    #Informações da Peça
    part_id: int = Field(foreign_key="part.id", description="ID da peça relacionada")
    part_code: str = Field(index=True, unique=True, max_length=150, description="Código da peça")

    #Data e timestamps
    date_of_occurrence: datetime = Field(description="Data/hora de ocorrência do problema")
    analysis_date: Optional[datetime] = Field(default=None, description="Data/hora da análise da qualidade")
    rework_date: Optional[datetime] = Field(default=None, description="Data/hora do retrabalho")
    closing_date: Optional[datetime] = Field(default=None, description="Data/hora de fechamento")

    #Análise da qualidade
    root_cause: Optional[str] = Field(default=None, sa_column=Column(Text), description="Causa raiz identificada pela qualidade")
    corrective_action: Optional[str] = Field(default=None, sa_column=Column(Text), description="Ação corretiva proposta")
    preventive_action: Optional[str] = Field(default=None, sa_column=Column(Text), description="Ação preventiva proposta")
    analysis_observations: Optional[str] = Field(default=None, sa_column=Column(Text), description="Observações da análise")
    estimated_rework_time: Optional[int] = Field(default=None, description="Tempo estimado de retrabalho em minutos")
    requires_external_support: Optional[bool] = Field(default=False, description="Indica se requer suporte externo")
    quality_verified: Optional[bool] = Field(default=None, description="Indica se a qualidade foi verificada após o retrabalho")
    close_rnc: Optional[bool] = Field(default=False, description="Indica se está fechando o RNC")
    refused: Optional[bool] = Field(default=False, description="Indica se a peça virou refugo")

    #Retrabalho do Técnico
    rework_description: Optional[str] = Field(default=None, sa_column=Column(Text), description="Descrição do retrabalho realizado")
    actions_taken: Optional[str] = Field(default=None, sa_column=Column(Text), description="Ações tomadas durante o retrabalho")
    materials_used: Optional[str] = Field(default=None, sa_column=Column(Text), description="Materiais utilizados no retrabalho")
    time_spent: Optional[int] = Field(default=None, description="Tempo gasto no retrabalho em minutos")
    rework_observations: Optional[str] = Field(default=None, sa_column=Column(Text), description="Observações sobre o retrabalho")

    #Foreign Keys - Responsáveis
    open_by_id: int = Field(foreign_key="user.id", description="ID do usuário que abriu o RNC")
    analysis_user_id: Optional[int] = Field(default=None, foreign_key="user.id", description="ID do usuário da área da qualidade")
    rework_user_id: Optional[int] = Field(default=None, foreign_key="user.id", description="ID do usuário da área de retrabalho")
    current_responsible_id: Optional[int] = Field(default=None, foreign_key="user.id", description="ID do responsável atual")
    closed_by_id: Optional[int] = Field(default=None, foreign_key="user.id", description="ID do usuário que fechou o RNC")

    #Relationships
    part: Part = Relationship(back_populates="rnc", sa_relationship_kwargs={"lazy": "selectin"})
    open_by: "User" = Relationship(back_populates="open_rncs", sa_relationship_kwargs={"foreign_keys": "RNC.open_by_id", "lazy": "selectin"})
    analysis_by: "User" = Relationship(back_populates="analysis_rncs", sa_relationship_kwargs={"foreign_keys": "RNC.analysis_user_id", "lazy": "selectin"})
    rework_by: "User" = Relationship(back_populates="rework_rncs", sa_relationship_kwargs={"foreign_keys": "RNC.rework_user_id", "lazy": "selectin"})
    closed_by: "User" = Relationship(back_populates="rncs_closed", sa_relationship_kwargs={"foreign_keys": "RNC.closed_by_id", "lazy": "selectin"})

    #Métodos Estáticos
    @staticmethod
    def generate_next_num_rnc(session: Session) -> int:
        """
        Gera o próximo número sequencial do RNC (até 8 dígitos)
        
        Args:
            session: Sessão do banco de dados
        Returns:
            Próximo número do RNC
        Raises:
            ValueError: Se o limite se 8 dígitos for atingido
        """
        result = session.exec(select(func.max(RNC.num_rnc))).first()
        next_number = (result or 0) + 1
        if next_number > 99999999:
            raise ValueError("Limite máximo de 8 dígitos atingido para num_rnc")
        return next_number
    
    #Métodos de instância
    def is_open(self) -> bool:
        """Verifica se o RNC está aberto"""
        return self.status == RNCStatus.ABERTO.value
    
    def is_closed(self) -> bool:
        """Verifica se o RNC está fechado"""
        return self.status == RNCStatus.FECHADO.value
    
    def is_critical(self) -> bool:
        """Verifica se o RNC é crítico"""
        return self.critical_level in [
            RNCCriticalLevel.ALTA.value,
            RNCCriticalLevel.CRITICA.value
        ]
    
    def has_analysis(self) -> bool:
        """Verifica se o RNC já tem análise da qualidade"""
        return self.root_cause is not None and self.corrective_action is not None
    
    def has_rework(self) -> bool:
        """Verifica se o RNC já tem retrabalho registrado"""
        return self.rework_description is not None and self.actions_taken is not None
    
    def get_total_time_spent(self) -> Optional[int]:
        """
        Retorna o tempo total gasto (estimado + real) em minutos
        
        Returns:
            Tempo total em minutos ou None se não houver dados
        """
        estimated = self.estimated_rework_time or 0
        actual = self.time_spent or 0

        if estimated == 0 and actual == 0:
            return None
        
        return estimated + actual
    
    def get_resolution_time_days(self) -> Optional[float]:
        """
        Calcula o tempo total de resolução em dias
        
        Returns:
            Tempo em dias ou None se ainda não foi fechado
        """
        if not self.closing_date:
            return None
        
        delta = self.closing_date - self.date_of_occurrence
        return round(delta.total_seconds() / 86400, 2)
    
    def __repr__(self) -> str:
        """Representação string do RNC"""
        return f"<RNC(num_rnc={self.num_rnc}, title='{self.title}', status='{self.status}')>"
