from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash

from ..interfaces import AuthServiceInterface, UserRepository
from ..models import User


class AuthService(AuthServiceInterface):
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def login(self, email: str, password: str) -> Optional[User]:
        user = self._user_repo.get_by_email(email)
        if not user:
            return None
        if not check_password_hash(user.password_hash, password):
            return None
        return user

    def get_current_user(self, user_id: str) -> Optional[User]:
        return self._user_repo.get_by_id(user_id)

    @staticmethod
    def hash_password(password: str) -> str:
        return generate_password_hash(password)

    @staticmethod
    def hash_password(password: str) -> str:
        return generate_password_hash(password)

    @staticmethod
    def create_default_admin(user_repo: UserRepository, email: str, password: str, display_name: str = "Admin") -> User:
        hashed = generate_password_hash(password)
        existing = user_repo.get_by_email(email)
        if existing:
            return existing
        return user_repo.create(email, hashed, display_name)
