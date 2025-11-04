from app import repository, schema, model
import logging

logger = logging.getLogger(__name__)
rnc_repository = repository.RNCRepository
model_rnc = model.RNC

class RNCService:
    def __init__(self, repo: rnc_repository):
        self.repo = repo

    def create(self, rnc_data: schema.RNCCreate, current_user: model.User) -> model_rnc:
        """Cria um novo rnc no banco"""
        if not rnc_data:
            raise ValueError("Dados inválidos")
        if not current_user or not current_user.id:
            raise ValueError("Usuário autenticado inválido")
        
        return self.repo.create_rnc(rnc_data, open_by_id=current_user.id)
    
    def get_rnc_by_num(self, num_rnc: int):
        """Busca por um RNC específico pelo id"""
        return self.repo.get_by_num(num_rnc)

    def get_rncs_by_user(self, current_user: model.User) -> list[schema.RNCRead]:
        """Busca por RNCs abertos pelo usuário autenticado"""
        rncs = self.repo.get_by_user_id(current_user.id)
        logger.info("REGISTROS DE NAO CONFORMIDADES!!!!!",rncs)
        print(rncs)
        return [schema.RNCRead.model_validate(rnc) for rnc in rncs]
    
    def get_filtered_rncs(self, status: str = None, condition: str = None) -> list[model_rnc]:
        """Busca por todos os RNCs, aplicando as regras de negócio antes de chamar o repositório"""
        if status and status.upper() not in ["ABERTO", "FECHADO"]:
            raise ValueError("Status inválido")
        if condition and condition.lower() not in [
            "em_analise",
            "aprovado",
            "refugo",
            "retrabalho",
        ]:
            raise ValueError("Condition inválida")
        rncs = self.repo.list_all(status=status, condition=condition)
        return rncs
    
    def update_rnc(self, num_rnc: int, rnc_data: schema.RNCUpdate, current_user: model.User) -> model_rnc:
        """Atualiza um RNC"""
        rnc = self.repo.get_by_num(num_rnc)
        if not rnc:
            raise ValueError(f"RNC com número '{num_rnc}' não foi encontrado")
        if hasattr(rnc, "status") and rnc.status.lower() == "fechado":
            raise ValueError("Não é permitido atualizar um RNC que já está fechado")
        
        fechando_rnc = (
            rnc_data.status == model.RNCStatus.FECHADO
            and rnc.status != model.RNCStatus.FECHADO
        )
        return self.repo.update_rnc(num_rnc, rnc_data, current_user, fechando_rnc)