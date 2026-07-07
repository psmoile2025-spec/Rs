from typing import Optional, List
from datetime import datetime, timezone, date

from ...interfaces import OrderRepository
from ...models import Order
from .client import get_supabase_client


class SupabaseOrderRepository(OrderRepository):
    def get_by_id(self, id: str) -> Optional[Order]:
        client = get_supabase_client()
        result = client.table("orders").select("*").eq("id", id).execute()
        if not result.data:
            return None
        return Order.from_dict(result.data[0])

    def list(self, **filters) -> List[Order]:
        client = get_supabase_client()
        query = client.table("orders").select("*").order("created_at", desc=True)
        for key, value in filters.items():
            query = query.eq(key, value)
        result = query.execute()
        return [Order.from_dict(row) for row in result.data]

    def list_active(self) -> List[Order]:
        client = get_supabase_client()
        result = (
            client.table("orders")
            .select("*")
            .eq("status", "open")
            .order("created_at", desc=True)
            .execute()
        )
        return [Order.from_dict(row) for row in result.data]

    def create(self, order_number: str, created_by: str) -> Order:
        client = get_supabase_client()
        data = {
            "order_number": order_number,
            "status": "open",
            "subtotal": 0,
            "tax": 0,
            "total": 0,
            "created_by": created_by,
        }
        result = client.table("orders").insert(data).execute()
        return Order.from_dict(result.data[0])

    def update_status(self, id: str, status: str) -> Optional[Order]:
        client = get_supabase_client()
        result = client.table("orders").update({"status": status}).eq("id", id).execute()
        if not result.data:
            return None
        return Order.from_dict(result.data[0])

    def mark_paid(self, id: str, payment_type: str, total: float, tax: float, subtotal: float) -> Optional[Order]:
        client = get_supabase_client()
        now = datetime.now(timezone.utc).isoformat()
        data = {
            "status": "paid",
            "payment_type": payment_type,
            "total": total,
            "tax": tax,
            "subtotal": subtotal,
            "paid_at": now,
        }
        result = client.table("orders").update(data).eq("id", id).execute()
        if not result.data:
            return None
        return Order.from_dict(result.data[0])

    def get_by_date_range(self, from_date: datetime, to_date: datetime) -> List[Order]:
        client = get_supabase_client()
        result = (
            client.table("orders")
            .select("*")
            .gte("created_at", from_date.isoformat())
            .lte("created_at", to_date.isoformat())
            .order("created_at", desc=True)
            .execute()
        )
        return [Order.from_dict(row) for row in result.data]

    def get_next_order_number(self) -> str:
        client = get_supabase_client()
        today = date.today()
        prefix = f"ORD-{today.strftime('%Y%m%d')}-"
        result = (
            client.table("orders")
            .select("order_number")
            .ilike("order_number", f"{prefix}%")
            .order("order_number", desc=True)
            .limit(1)
            .execute()
        )
        if not result.data:
            return f"{prefix}0001"
        last_num = int(result.data[0]["order_number"].split("-")[-1])
        return f"{prefix}{last_num + 1:04d}"

    def update_totals(self, id: str, subtotal: float, tax: float, total: float) -> Optional[Order]:
        client = get_supabase_client()
        result = (
            client.table("orders")
            .update({"subtotal": subtotal, "tax": tax, "total": total})
            .eq("id", id)
            .execute()
        )
        if not result.data:
            return None
        return Order.from_dict(result.data[0])
