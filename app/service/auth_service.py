from app.repository.auth_repository import AuthRepository
from app import schema

class AuthService:

    def __init__(self, repo: AuthRepository):
        self.repo = repo

    def authenticate_user(self, data_login: schema.UserLogin):
        existing_user = self.repo.authenticate(data_login.email)
        if not existing_user:
            return None
        elif not existing_user.check_password(data_login.password):
            return None
        return existing_user