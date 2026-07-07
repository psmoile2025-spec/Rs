from functools import lru_cache
from supabase import create_client, Client
from flask import current_app


@lru_cache(maxsize=1)
def _create_client(url: str, key: str) -> Client:
    return create_client(url, key)


def get_supabase_client() -> Client:
    url = current_app.config["SUPABASE_URL"]
    key = current_app.config["SUPABASE_KEY"]
    return _create_client(url, key)
