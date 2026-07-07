from typing import Optional, List

from ...interfaces import OrderItemRepository
from ...models import OrderItem
from .client import get_supabase_client


class SupabaseOrderItemRepository(OrderItemRepository):
    def get_by_id(self, id: str) -> Optional[OrderItem]:
        client = get_supabase_client()
        result = (
            client.table("order_items")
            .select("*, menu_items(name)")
            .eq("id", id)
            .execute()
        )
        if not result.data:
            return None
        return self._map_row(result.data[0])

    def list(self, **filters) -> List[OrderItem]:
        client = get_supabase_client()
        query = client.table("order_items").select("*, menu_items(name)")
        for key, value in filters.items():
            query = query.eq(key, value)
        result = query.execute()
        return [self._map_row(row) for row in result.data]

    def list_by_order(self, order_id: str) -> List[OrderItem]:
        client = get_supabase_client()
        result = (
            client.table("order_items")
            .select("*, menu_items(name)")
            .eq("order_id", order_id)
            .execute()
        )
        return [self._map_row(row) for row in result.data]

    def find_by_order_and_menu_item(self, order_id: str, menu_item_id: str) -> Optional[OrderItem]:
        client = get_supabase_client()
        result = (
            client.table("order_items")
            .select("*, menu_items(name)")
            .eq("order_id", order_id)
            .eq("menu_item_id", menu_item_id)
            .limit(1)
            .execute()
        )
        if not result.data:
            return None
        return self._map_row(result.data[0])

    def update_quantity(self, id: str, quantity: int, line_total: float) -> Optional[OrderItem]:
        client = get_supabase_client()
        result = (
            client.table("order_items")
            .update({"quantity": quantity, "line_total": line_total})
            .eq("id", id)
            .execute()
        )
        if not result.data:
            return None
        return self._map_row(result.data[0])

    def create(self, order_id: str, menu_item_id: str, quantity: int, unit_price: float, line_total: float) -> OrderItem:
        client = get_supabase_client()
        data = {
            "order_id": order_id,
            "menu_item_id": menu_item_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "line_total": line_total,
        }
        result = client.table("order_items").insert(data).execute()
        return self._map_row(result.data[0])

    def delete(self, id: str) -> bool:
        client = get_supabase_client()
        result = client.table("order_items").delete().eq("id", id).execute()
        return len(result.data) > 0

    def delete_by_order(self, order_id: str) -> bool:
        client = get_supabase_client()
        result = client.table("order_items").delete().eq("order_id", order_id).execute()
        return True

    def _map_row(self, row: dict) -> OrderItem:
        row["item_name"] = row.get("menu_items", {}).get("name") if row.get("menu_items") else None
        return OrderItem.from_dict(row)
