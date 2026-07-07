from typing import List, Optional

from ..interfaces import MenuServiceInterface, CategoryRepository, MenuItemRepository
from ..models import Category, MenuItem


class MenuService(MenuServiceInterface):
    def __init__(self, category_repo: CategoryRepository, menu_item_repo: MenuItemRepository):
        self._category_repo = category_repo
        self._menu_item_repo = menu_item_repo

    def list_categories(self) -> List[Category]:
        return self._category_repo.list()

    def create_category(self, name: str, sort_order: int = 0) -> Category:
        return self._category_repo.create(name, sort_order)

    def update_category(self, id: str, name: Optional[str] = None, sort_order: Optional[int] = None) -> Optional[Category]:
        return self._category_repo.update(id, name, sort_order)

    def delete_category(self, id: str) -> bool:
        return self._category_repo.delete(id)

    def get_category(self, id: str) -> Optional[Category]:
        return self._category_repo.get_by_id(id)

    def list_items(self, category_id: Optional[str] = None) -> List[MenuItem]:
        if category_id:
            return self._menu_item_repo.list_by_category(category_id)
        return self._menu_item_repo.list()

    def create_item(self, category_id: str, name: str, price: float, description: Optional[str] = None, cost: Optional[float] = None) -> MenuItem:
        return self._menu_item_repo.create(category_id, name, price, description, cost)

    def update_item(self, id: str, **kwargs) -> Optional[MenuItem]:
        return self._menu_item_repo.update(id, **kwargs)

    def toggle_item_available(self, id: str) -> Optional[MenuItem]:
        return self._menu_item_repo.toggle_available(id)

    def delete_item(self, id: str) -> bool:
        return self._menu_item_repo.delete(id)

    def get_item(self, id: str) -> Optional[MenuItem]:
        return self._menu_item_repo.get_by_id(id)
