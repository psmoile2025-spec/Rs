from typing import Optional, List

from ...interfaces import CategoryRepository
from ...models import Category
from .client import get_supabase_client


class SupabaseCategoryRepository(CategoryRepository):
    def get_by_id(self, id: str) -> Optional[Category]:
        client = get_supabase_client()
        result = client.table("categories").select("*").eq("id", id).execute()
        if not result.data:
            return None
        return Category.from_dict(result.data[0])

    def list(self, **filters) -> List[Category]:
        client = get_supabase_client()
        query = client.table("categories").select("*").order("sort_order")
        for key, value in filters.items():
            query = query.eq(key, value)
        result = query.execute()
        return [Category.from_dict(row) for row in result.data]

    def create(self, name: str, sort_order: int = 0) -> Category:
        client = get_supabase_client()
        result = client.table("categories").insert({
            "name": name,
            "sort_order": sort_order,
        }).execute()
        return Category.from_dict(result.data[0])

    def update(self, id: str, name: Optional[str] = None, sort_order: Optional[int] = None) -> Optional[Category]:
        client = get_supabase_client()
        updates = {}
        if name is not None:
            updates["name"] = name
        if sort_order is not None:
            updates["sort_order"] = sort_order
        if not updates:
            return self.get_by_id(id)
        result = client.table("categories").update(updates).eq("id", id).execute()
        if not result.data:
            return None
        return Category.from_dict(result.data[0])

    def delete(self, id: str) -> bool:
        client = get_supabase_client()
        result = client.table("categories").delete().eq("id", id).execute()
        return len(result.data) > 0
