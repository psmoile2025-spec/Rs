from typing import Optional, List
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

    def list_users(self) -> List[User]:
        return self._user_repo.list()

    def create_user(self, email: str, password: str, display_name: str) -> User:
        existing = self._user_repo.get_by_email(email)
        if existing:
            raise ValueError(f"User with email '{email}' already exists")
        hashed = generate_password_hash(password)
        return self._user_repo.create(email, hashed, display_name)

    def update_user(self, user_id: str, email: str, display_name: str) -> Optional[User]:
        return self._user_repo.update(user_id, email=email, display_name=display_name)

    def delete_user(self, user_id: str) -> bool:
        return self._user_repo.delete(user_id)

    @staticmethod
    def hash_password(password: str) -> str:
        return generate_password_hash(password)
