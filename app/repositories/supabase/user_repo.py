from typing import Optional, List

from ...interfaces import UserRepository
from ...models import User
from .client import get_supabase_client


class SupabaseUserRepository(UserRepository):
    def get_by_id(self, id: str) -> Optional[User]:
        client = get_supabase_client()
        result = client.table("users").select("*").eq("id", id).execute()
        if not result.data:
            return None
        return User.from_dict(result.data[0])

    def get_by_email(self, email: str) -> Optional[User]:
        client = get_supabase_client()
        result = client.table("users").select("*").eq("email", email).execute()
        if not result.data:
            return None
        return User.from_dict(result.data[0])

    def create(self, email: str, password_hash: str, display_name: str) -> User:
        client = get_supabase_client()
        result = client.table("users").insert({
            "email": email,
            "password_hash": password_hash,
            "display_name": display_name,
        }).execute()
        return User.from_dict(result.data[0])

    def list(self, **filters) -> List[User]:
        client = get_supabase_client()
        query = client.table("users").select("*")
        for key, value in filters.items():
            query = query.eq(key, value)
        result = query.execute()
        return [User.from_dict(row) for row in result.data]

    def update(self, id: str, **kwargs) -> Optional[User]:
        client = get_supabase_client()
        allowed = {"email", "password_hash", "display_name"}
        updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        if not updates:
            return self.get_by_id(id)
        result = client.table("users").update(updates).eq("id", id).execute()
        if not result.data:
            return None
        return User.from_dict(result.data[0])
