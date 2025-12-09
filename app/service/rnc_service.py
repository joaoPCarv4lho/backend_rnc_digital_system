from app import repository, schema, model
from app.websocket.manager import manager
from app.utils.serializable import serialize_rnc
from typing import Optional
from collections import Counter
import logging

logger = logging.getLogger(__name__)
model_rnc = model.RNC

class RNCService:
    """
    Serviço para gerenciamento de RNCs (Registro de não conformidades)
    Responsável pela lógica de negócio e orquestração entre repository e API
    """
    def __init__(self, repo: repository.RNCRepository):
        self.repo = repo

    #CRIAÇÃO
    async def create(self, rnc_data: schema.RNCCreate, current_user: model.User) -> model_rnc:
        """
        Cria um novo rnc no sistema
        Args:
            rnc_data: Dados do RNC a ser criado
            current_user: Usuário autenticado que está criando
        Returns:
            RNC criado
        Raises:
            ValueError: Se dados inválidos ou usuário não autenticado
        """
        if not rnc_data:
            raise ValueError("Dados do RNC são obrigatórios")
        if not current_user or not current_user.id:
            raise ValueError("Usuário não autenticado")
        
        self._validate_critical_level(rnc_data.critical_level)
        try:
            new_rnc = self.repo.create_rnc(rnc_data, open_by_id=current_user.id)

            await manager.broadcast_all("rnc_created", serialize_rnc(new_rnc))
            logger.info(f"RNC #{new_rnc.num_rnc} criado por usuário {current_user.id} para peça {rnc_data.part_code}")

            return new_rnc
        except ValueError as e:
            logger.warning(f"Tentativa de criar RNC duplicado: {str(e)}")
            raise
    
    #CONSULTAS
    def get_rnc_by_num(self, num_rnc: int) -> Optional[model.RNC]:
        """
        Busca por um RNC específico pelo número
        Args:
            num_rnc: Número do RNC
        Returns:
            RNC encontrado ou None
        """
        rnc = self.repo.get_by_num(num_rnc)
        if not rnc:
            logger.warning(f"RNC #{num_rnc} não encontrado")
        return rnc

    def get_rnc_by_part_code(self, partCode: str) -> model.RNC:
        """
        Busca um RNC aberto pelo código da peça
        Args:
            part_code: Código da peça
        Returns:
            RNC encontrado
        Raises:
            ValueError: Se não encontrar RNC para a peça
        """
        rnc = self.repo.get_rnc_by_part_code(partCode)
        if not rnc:
            raise ValueError(f"Não existe RNC aberto para a peça com código: '{partCode}'")
        return rnc

    def get_rncs_opened_by_user(self, current_user: model.User, limit: int = 100, offset: int = 0) -> schema.RNCListResponse:
        """
        Busca RNCs abertos por um usuário autenticado
        Args:
            current_user: Usuário autenticado
            limit: Limite de resultados
            offset: Offset para paginação
        Returns:
            Lista de RNCs do usuário
        """
        rncs = self.repo.search_rnc_opened_by_user(current_user.id, limit, offset)
        return schema.RNCListResponse(
            items=[schema.RNCRead.model_validate(rnc) for rnc in rncs],
            total=len(rncs),
            page=1,
            page_size=len(rncs),
            total_pages=1
        )
    
    def get_rncs_reworked_by_user(self, current_user: model.User, limit: int = 200, offset: int = 0) -> schema.RNCListResponse:
        """
        Retorna RNCs retrabalhados por um usuário específico
        """
        rncs = self.repo.search_rnc_rework_by_user(current_user.id, limit, offset)
        return schema.RNCListResponse(
            items=[schema.RNCRead.model_validate(rnc) for rnc in rncs],
            total=len(rncs),
            page=1,
            page_size=len(rncs),
            total_pages=1
        )
    
    def get_rncs_analyzed_by_user(self, current_user: model.User, limit: int = 200, offset: int = 0) -> schema.RNCListResponse:
        """
        Retorna RNCs analisados por um usuário específico
        """
        rncs = self.repo.search_rnc_by_analysis_user(current_user.id, limit, offset)
        return schema.RNCListResponse(
            items=[schema.RNCRead.model_validate(rnc) for rnc in rncs],
            total=len(rncs),
            page=1,
            page_size=len(rncs),
            total_pages=1
        )
    
    def get_filtered_rncs(self, status: str = None, condition: str = None, limit: int = 200, offset: int = 0) -> list[model_rnc]:
        """
        Busca RNCs com filtros opcionais
        Args:
            status: Filtro por status (aberto/fechado)
            condition: Filtro por condição
            limit: Limite de resultados
            offset: Offset para paginação
        Returns:
            Lista de RNCs filtrados
        Raises:
            ValueError: Se filtros inválidos
        """
        self._validate_filters(status, condition)
        rncs = self.repo.list_all(status, condition, limit, offset)
        logger.info(f"Listagem de RNCs: status={status}, condition={condition}, " f"encontrados={len(rncs)}")
        return rncs

    def get_rncs_pending_rework(self) -> schema.RNCListResponse:
        """
        Retorna RNCs que precisam ser retrabalhados
        """
        rncs = self.repo.list_by_rework_status(pending=True)
        return schema.RNCListResponse(
            items=[schema.RNCRead.model_validate(rnc) for rnc in rncs],
            total=len(rncs),
            page=1,
            page_size=len(rncs),
            total_pages=1
        )

    def get_rncs_with_completed_rework(self) -> schema.RNCListResponse:
        """
        Retorna RNCs que já foram retrabalhados
        """
        rncs = self.repo.list_by_rework_status(pending=False)
        return schema.RNCListResponse(
            items=[schema.RNCRead.model_validate(rnc) for rnc in rncs],
            total=len(rncs),
            page=1,
            page_size=len(rncs),
            total_pages=1
        )

    def get_rncs_pending_analysis(self) -> schema.RNCListResponse:
        """
        Retorna RNCs que precisam ser analisados
        """
        rncs = self.repo.list_by_analysis_status(pending=True)
        return schema.RNCListResponse(
            items=[schema.RNCRead.model_validate(rnc) for rnc in rncs],
            total=len(rncs),
            page=1,
            page_size=len(rncs),
            total_pages=1
        )
    
    def get_rncs_with_completed_analysis(self) -> schema.RNCListResponse:
        """
        Retorna RNCs que já foram analisados
        """
        rncs = self.repo.list_by_analysis_status(pending=False)
        return schema.RNCListResponse(
            items=[schema.RNCRead.model_validate(rnc) for rnc in rncs],
            total=len(rncs),
            page=1,
            page_size=len(rncs),
            total_pages=1
        )
    
    async def register_quality_analysis(self, num_rnc: int, analysis_data: schema.QualityAnalysis, quality_user: model.User) -> model.RNC:
        """
        Registra análise da qualidade no RNC
        Args:
            num_rnc: Número do RNC
            analysis_data: Dados da análise
            quality_user: Usuário da qualidade
        """
        rnc = self.get_rnc_by_num(num_rnc)
        if not rnc:
            raise ValueError(f"RNC #{num_rnc} não encontrado.")
        if rnc.is_closed():
            raise ValueError(f"RNC #{num_rnc} já está fechado")
        if not self._user_can_analyze(quality_user):
            raise ValueError(f"Usuário não tem permissão para analisar RNCs")
        try:
            updated_rnc = self.repo.register_quality_analysis(num_rnc, analysis_data, quality_user)
            if updated_rnc.is_closed():
                await manager.broadcast_all("rnc_closed", serialize_rnc(updated_rnc))
                logger.info(f"RNC #{num_rnc} fechado após análise.")
            else:
                await manager.broadcast_all("rnc_analysis_completed", serialize_rnc(updated_rnc))
                logger.info(f"Análise registrada no RNC #{num_rnc} por usuário {quality_user.id}")
            return updated_rnc
        except Exception as e:
            logger.error(f"Erro ao registrar análise no RNC #{num_rnc}: {str(e)}")
            raise
    
    async def register_technician_rework(self, num_rnc: int, rework_data: schema.TechnicianRework, technician_user: model.User) -> model.RNC:
        """
        Registra retrabalho realizado pelo técnico
        Args:   
            num_rnc: Número do RNC
            rework_data: Dados do retrabalho
            technician_user: Usuário técnico
        Returns:
            RNC atualizado
        Raises:
            ValueError: Se RNC não encontrado, já fechado ou sem análise
        """
        rnc = self.get_rnc_by_num(num_rnc)
        if not rnc:
            raise ValueError(f"RNC #{num_rnc} não encontrado")
        if rnc.is_closed():
            raise ValueError(f"RNC #{num_rnc} já está fechado.")
        if not rnc.has_analysis():
            raise ValueError(f"RNC #{num_rnc} ainda não possui análise da qualidade")
        if not self._user_can_rework(technician_user):
            raise ValueError(f"Usuário não tem permissão para realizar retrabalho")
        
        try:
            updated_rnc = self.repo.register_technician_rework(num_rnc, rework_data, technician_user)
            await manager.broadcast_all("rnc_rework_completed", serialize_rnc(updated_rnc))
            logger.info(f"Retrabalho registrado com sucesso no RNC #{num_rnc}, aguardando nova análise.")
            return updated_rnc
        except Exception as e:
            logger.error(f"Erro ao registrar retrabalho no RNC #{num_rnc}: {str(e)}")
            raise
    
    async def close_rnc(self, num_rnc: int, close_data: schema.RNCClose, closing_user: model.User) -> model.RNC:
        """
        Fecha um RNC manualmente
        Args:
            num_rnc: Número do RNC
            close_data: Dados do fechamento
            closing_user: Usuário que está fechando
        Returns:
            RNC fechado
        Raises:
            ValueError: Se RNC não encontrado ou já fechado
        """
        rnc = self.get_rnc_by_num(num_rnc)
        if not rnc:
            raise ValueError(f"RNC #{num_rnc} não encontrado")
        if rnc.is_closed():
            raise ValueError(f"RNC #{num_rnc} já está fechado")
        if not self._user_can_close(closing_user):
            raise ValueError(f"Usuário não tem permissão para fechar RNCs")

        try:
            closed_rnc = self.repo.close_rnc(num_rnc, closing_user, close_data.closing_notes)
            await manager.broadcast_all("rnc_closed", serialize_rnc(closed_rnc))
            logger.info(f"RNC #{num_rnc} fechado manualmente por usuário {closing_user.id}")
            return closed_rnc
        except Exception as e:
            logger.error(f"Erro ao fechar RNC #{num_rnc}: {str(e)}")
            raise

    def get_statistics(self) -> schema.RNCStatistics:
        """
        Retorna estatísticas sobre os RNCs
        Returns:
            Objeto com estatísticas
        """
        all_rncs = self.repo.list_all(limit=10000, offset=0)  #busca todos os RNCs

        open_rncs = [r for r in all_rncs if r.is_open()]    #filta os RNCs abertos
        closed_rncs = [r for r in all_rncs if r.is_closed()]    #filta os RNCs fechados
        approved_rncs = [r for r in all_rncs if r.condition == "aprovado"]
        refused_rncs = [r for r in all_rncs if r.condition == "refugo"]
        resolution_times = [r.get_resolution_time_days() for r in closed_rncs if r.get_resolution_time_days()]    #calcula o tempo médio de resolução
        avg_resolution = (sum(resolution_times) / len(resolution_times) if resolution_times else None)

        monthly_counter = Counter()
        for r in all_rncs:
            if r.date_of_occurrence:
                month_key = r.date_of_occurrence.strftime("%Y-%m")
                monthly_counter[month_key] +=1
        monthly_data = [
            {"month": month, "count": count}
            for month, count in sorted(monthly_counter.items())
        ]

        status_counter = Counter(r.status for r in all_rncs if r.status)
        by_status = [
            {"status": status, "total": total}
            for status, total in status_counter.items()
        ]

        condition_counter = Counter(r.condition for r in all_rncs if r.condition)
        by_condition = [
            {"condition": cond, "total": total}
            for cond, total in condition_counter.items()
        ]

        return schema.RNCStatistics(
            total_rncs=len(all_rncs),
            open_rncs=len(open_rncs),
            closed_rncs=len(closed_rncs),
            approved_rncs=len(approved_rncs),
            refused_rncs=len(refused_rncs),
            average_resolution_time=avg_resolution,
            monthly=monthly_data,
            by_status=by_status,
            by_condition=by_condition
        )

    # async def update_rnc(self, num_rnc: int, rnc_data: schema.RNCUpdate, current_user: model.User) -> model_rnc:
    #     """Atualiza um RNC"""
    #     rnc = self.repo.get_by_num(num_rnc)
    #     if not rnc:
    #         raise ValueError(f"RNC com número '{num_rnc}' não foi encontrado")
    #     if hasattr(rnc, "status") and rnc.status.lower() == "fechado":
    #         raise ValueError("Não é permitido atualizar um RNC que já está fechado")
        
    #     fechando_rnc = (
    #         rnc_data.status == model.RNCStatus.FECHADO
    #         and rnc_data.condition in {
    #             model.RNCCondition.APROVADO,
    #             model.RNCCondition.REFUGO
    #         }
    #     )
    #     updated_rnc = self.repo.update_rnc(num_rnc, rnc_data, current_user, fechando_rnc)
    #     if fechando_rnc:
    #         await manager.broadcast("rnc_closed", serialize_rnc(updated_rnc))

    #     if updated_rnc.condition == model.RNCCondition.RETRABALHO.value:
    #         await manager.broadcast("rnc_rework", serialize_rnc(updated_rnc))

    #     await manager.broadcast("rnc_updated", serialize_rnc(updated_rnc))
    #     return updated_rnc
    
    #Métodos Auxiliares
    def _validate_filters(self, status, condition):
        if status and status.lower() not in ["aberto", "fechado"]:
            raise ValueError("Status inválido")
        if condition and condition.lower() not in ["em_analise", "aprovado", "refugo", "retrabalho"]:
            raise ValueError("Condição inválida")
        
    def _validate_critical_level(self, critical_level: str) -> None:
        """Valida o nível de criticidade"""
        valid_levels = [level.value for level in model.RNCCriticalLevel]

        if critical_level.lower() not in valid_levels:
            raise ValueError(
                f"Nível de criticidade inválido."
                f"Valores válidos: {', '.join(valid_levels)}"
                )
        
    def _user_can_analyze(self, user: model.User) -> bool:
        """Verifica se o usuário pode fazer análise de qualidade"""
        valid_roles = [role.value for role in model.UserRole]
        if user.role.lower() not in valid_roles:
            raise ValueError(f"Role inválido!")
        if user.role == model.UserRole.ENGENHARIA.value or user.role == model.UserRole.QUALIDADE:
            return True
        
        return False
    
    def _user_can_rework(self, user: model.User) -> bool:
        """Verifica se o usuário pode fazer retrabalho"""
        valid_roles = [role.value for role in model.UserRole]
        if user.role.lower() not in valid_roles:
            raise ValueError(f"Role inválido!")
        if user.role == model.UserRole.TECNICO.value:
            return True
        
        return False
    
    def _user_can_close(self, user: model.User) -> bool:
        """Verifica se o usuário pode fechar o RNC"""
        valid_roles = [role.value for role in model.UserRole]
        if user.role.lower() not in valid_roles:
            raise ValueError(f"Role inválido!")
        if user.role == model.UserRole.ENGENHARIA.value or user.role == model.UserRole.QUALIDADE:
            return True
        
        return False