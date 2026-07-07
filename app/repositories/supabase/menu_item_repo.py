from typing import Optional, List
from datetime import datetime, timezone

from ...interfaces import MenuItemRepository
from ...models import MenuItem
from .client import get_supabase_client


class SupabaseMenuItemRepository(MenuItemRepository):
    def get_by_id(self, id: str) -> Optional[MenuItem]:
        client = get_supabase_client()
        result = (
            client.table("menu_items")
            .select("*, categories(name)")
            .eq("id", id)
            .execute()
        )
        if not result.data:
            return None
        row = result.data[0]
        row["category_name"] = row.get("categories", {}).get("name") if row.get("categories") else None
        return MenuItem.from_dict(row)

    def list(self, **filters) -> List[MenuItem]:
        client = get_supabase_client()
        query = client.table("menu_items").select("*, categories(name)").order("name")
        for key, value in filters.items():
            query = query.eq(key, value)
        result = query.execute()
        return self._map_rows(result.data)

    def list_by_category(self, category_id: str) -> List[MenuItem]:
        client = get_supabase_client()
        result = (
            client.table("menu_items")
            .select("*, categories(name)")
            .eq("category_id", category_id)
            .order("name")
            .execute()
        )
        return self._map_rows(result.data)

    def create(self, category_id: str, name: str, price: float, description: Optional[str] = None, cost: Optional[float] = None) -> MenuItem:
        client = get_supabase_client()
        data = {
            "category_id": category_id,
            "name": name,
            "price": price,
            "description": description,
        }
        if cost is not None:
            data["cost"] = cost
        result = client.table("menu_items").insert(data).execute()
        return MenuItem.from_dict(result.data[0])

    def update(self, id: str, **kwargs) -> Optional[MenuItem]:
        client = get_supabase_client()
        allowed = {"name", "description", "price", "category_id", "available", "cost"}
        updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        if not updates:
            return self.get_by_id(id)
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = client.table("menu_items").update(updates).eq("id", id).execute()
        if not result.data:
            return None
        return MenuItem.from_dict(result.data[0])

    def toggle_available(self, id: str) -> Optional[MenuItem]:
        client = get_supabase_client()
        item = self.get_by_id(id)
        if not item:
            return None
        result = (
            client.table("menu_items")
            .update({"available": not item.available, "updated_at": datetime.now(timezone.utc).isoformat()})
            .eq("id", id)
            .execute()
        )
        if not result.data:
            return None
        return MenuItem.from_dict(result.data[0])

    def delete(self, id: str) -> bool:
        client = get_supabase_client()
        result = client.table("menu_items").delete().eq("id", id).execute()
        return len(result.data) > 0

    def _map_rows(self, rows: list) -> List[MenuItem]:
        items = []
        for row in rows:
            row["category_name"] = row.get("categories", {}).get("name") if row.get("categories") else None
            items.append(MenuItem.from_dict(row))
        return items
