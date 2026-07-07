from typing import Optional, List

from postgrest.exceptions import APIError

from ...interfaces import SettingRepository
from ...models import Setting
from .client import get_supabase_client


class SupabaseSettingRepository(SettingRepository):
    TABLE = "settings"

    def get(self, key: str) -> Optional[str]:
        try:
            client = get_supabase_client()
            result = client.table(self.TABLE).select("value").eq("key", key).execute()
            if not result.data:
                return None
            return result.data[0]["value"]
        except APIError:
            return None

    def set(self, key: str, value: str) -> bool:
        try:
            client = get_supabase_client()
            client.table(self.TABLE).upsert({"key": key, "value": value}, on_conflict="key").execute()
            return True
        except APIError:
            return False

    def list(self, **filters) -> List[Setting]:
        try:
            client = get_supabase_client()
            query = client.table(self.TABLE).select("*").order("key")
            for k, v in filters.items():
                query = query.eq(k, v)
            result = query.execute()
            return [Setting.from_dict(r) for r in result.data]
        except APIError:
            return []