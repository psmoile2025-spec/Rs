from abc import ABC, abstractmethod
from typing import List, Optional

from ..models import Category, MenuItem


class MenuServiceInterface(ABC):
    @abstractmethod
    def list_categories(self) -> List[Category]:
        ...

    @abstractmethod
    def create_category(self, name: str, sort_order: int = 0) -> Category:
        ...

    @abstractmethod
    def update_category(self, id: str, name: Optional[str] = None, sort_order: Optional[int] = None) -> Optional[Category]:
        ...

    @abstractmethod
    def delete_category(self, id: str) -> bool:
        ...

    @abstractmethod
    def get_category(self, id: str) -> Optional[Category]:
        ...

    @abstractmethod
    def list_items(self, category_id: Optional[str] = None) -> List[MenuItem]:
        ...

    @abstractmethod
    def create_item(self, category_id: str, name: str, price: float, description: Optional[str] = None, cost: Optional[float] = None) -> MenuItem:
        ...

    @abstractmethod
    def update_item(self, id: str, **kwargs) -> Optional[MenuItem]:
        ...

    @abstractmethod
    def toggle_item_available(self, id: str) -> Optional[MenuItem]:
        ...

    @abstractmethod
    def delete_item(self, id: str) -> bool:
        ...

    @abstractmethod
    def get_item(self, id: str) -> Optional[MenuItem]:
        ...
