from abc import ABC, abstractmethod
from typing import Optional, List

from ..models import User


class AuthServiceInterface(ABC):
    @abstractmethod
    def login(self, email: str, password: str) -> Optional[User]:
        ...

    @abstractmethod
    def get_current_user(self, user_id: str) -> Optional[User]:
        ...

    @abstractmethod
    def list_users(self) -> List[User]:
        ...

    @abstractmethod
    def create_user(self, email: str, password: str, display_name: str) -> User:
        ...

    @abstractmethod
    def update_user(self, user_id: str, email: str, display_name: str) -> Optional[User]:
        ...

    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        ...
