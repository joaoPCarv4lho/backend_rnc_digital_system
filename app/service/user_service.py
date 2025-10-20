from app.repository.user_repository import UserRepository
from app import schema

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def create_user(self, user_data: schema.UserCreate):
        """Cria um novo usuário no banco"""
        existing_user = self.repo.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")
        return self.repo.create(user_data)
    
    def get_all_users(self):
        return self.repo.list_all()
    
    def get_by_email(self, email: str):
        return self.repo.get_by_email(email)
    
        #Acrescentar método update

    def delete_user(self, user_id: int):
        deleted = self.repo.delete(user_id)
        if not deleted:
            raise ValueError("User not found")
        return deleted