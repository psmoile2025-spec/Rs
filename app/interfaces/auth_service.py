from abc import ABC, abstractmethod
from typing import Optional

from ..models import User


class AuthServiceInterface(ABC):
    @abstractmethod
    def login(self, email: str, password: str) -> Optional[User]:
        ...

    @abstractmethod
    def get_current_user(self, user_id: str) -> Optional[User]:
        ...
