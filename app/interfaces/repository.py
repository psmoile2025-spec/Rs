from abc import ABC, abstractmethod
from typing import Optional, List, Any
from datetime import datetime

from ..models import User, Category, MenuItem, Order, OrderItem


class Repository(ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Any]:
        ...

    @abstractmethod
    def list(self, **filters) -> List[Any]:
        ...


class UserRepository(Repository, ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[User]:
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        ...

    @abstractmethod
    def create(self, email: str, password_hash: str, display_name: str) -> User:
        ...

    @abstractmethod
    def list(self, **filters) -> List[User]:
        ...

    @abstractmethod
    def update(self, id: str, **kwargs) -> Optional[User]:
        ...

    @abstractmethod
    def delete(self, id: str) -> bool:
        ...


class CategoryRepository(Repository, ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Category]:
        ...

    @abstractmethod
    def list(self, **filters) -> List[Category]:
        ...

    @abstractmethod
    def create(self, name: str, sort_order: int = 0) -> Category:
        ...

    @abstractmethod
    def update(self, id: str, name: Optional[str] = None, sort_order: Optional[int] = None) -> Optional[Category]:
        ...

    @abstractmethod
    def delete(self, id: str) -> bool:
        ...


class MenuItemRepository(Repository, ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[MenuItem]:
        ...

    @abstractmethod
    def list(self, **filters) -> List[MenuItem]:
        ...

    @abstractmethod
    def list_by_category(self, category_id: str) -> List[MenuItem]:
        ...

    @abstractmethod
    def create(self, category_id: str, name: str, price: float, description: Optional[str] = None, cost: Optional[float] = None, image_url: Optional[str] = None) -> MenuItem:
        ...

    @abstractmethod
    def update(self, id: str, **kwargs) -> Optional[MenuItem]:
        ...

    @abstractmethod
    def toggle_available(self, id: str) -> Optional[MenuItem]:
        ...

    @abstractmethod
    def delete(self, id: str) -> bool:
        ...


class OrderRepository(Repository, ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Order]:
        ...

    @abstractmethod
    def list(self, **filters) -> List[Order]:
        ...

    @abstractmethod
    def list_active(self) -> List[Order]:
        ...

    @abstractmethod
    def create(self, order_number: str, created_by: str) -> Order:
        ...

    @abstractmethod
    def update_status(self, id: str, status: str) -> Optional[Order]:
        ...

    @abstractmethod
    def mark_paid(self, id: str, payment_type: str, total: float, tax: float, subtotal: float) -> Optional[Order]:
        ...

    @abstractmethod
    def get_by_date_range(self, from_date: datetime, to_date: datetime) -> List[Order]:
        ...

    @abstractmethod
    def get_next_order_number(self) -> str:
        ...

    @abstractmethod
    def update_totals(self, id: str, subtotal: float, tax: float, total: float) -> Optional[Order]:
        ...


class OrderItemRepository(Repository, ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[OrderItem]:
        ...

    @abstractmethod
    def list(self, **filters) -> List[OrderItem]:
        ...

    @abstractmethod
    def list_by_order(self, order_id: str) -> List[OrderItem]:
        ...

    @abstractmethod
    def find_by_order_and_menu_item(self, order_id: str, menu_item_id: str) -> Optional[OrderItem]:
        ...

    @abstractmethod
    def create(self, order_id: str, menu_item_id: str, quantity: int, unit_price: float, line_total: float) -> OrderItem:
        ...

    @abstractmethod
    def update_quantity(self, id: str, quantity: int, line_total: float) -> Optional[OrderItem]:
        ...

    @abstractmethod
    def delete(self, id: str) -> bool:
        ...

    @abstractmethod
    def delete_by_order(self, order_id: str) -> bool:
        ...
