from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from ..models import Order, OrderItem, MenuItem, Category


class POSServiceInterface(ABC):
    @abstractmethod
    def get_menu_data(self) -> Tuple[List[Category], List[MenuItem]]:
        ...

    @abstractmethod
    def create_order(self, user_id: str) -> Order:
        ...

    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Order]:
        ...

    @abstractmethod
    def add_item_to_order(self, order_id: str, menu_item_id: str, quantity: int = 1) -> OrderItem:
        ...

    @abstractmethod
    def remove_item_from_order(self, order_id: str, item_id: str) -> bool:
        ...

    @abstractmethod
    def pay_order(self, order_id: str, payment_type: str) -> Optional[Order]:
        ...

    @abstractmethod
    def cancel_order(self, order_id: str) -> Optional[Order]:
        ...

    @abstractmethod
    def list_active_orders(self) -> List[Order]:
        ...

    @abstractmethod
    def get_order_with_items(self, order_id: str) -> Optional[Order]:
        ...
