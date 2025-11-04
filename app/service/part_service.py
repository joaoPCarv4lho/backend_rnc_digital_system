from app import repository, schema, model

class PartService:
    def __init__(self, repo: repository.PartRepository):
        self.repo = repo

    def get_part_by_code(self, part_code: str) -> schema.PartRead:
        """Busca uma peça pelo código"""
        part = self.repo.get_by_code(part_code)
        if not part:
            raise ValueError(f"Peça com código '{part_code}' não encontrada.")
        return schema.PartRead.model_validate(part)