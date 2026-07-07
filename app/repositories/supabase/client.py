from functools import lru_cache
from supabase import create_client, Client
from flask import current_app


class SupabaseConfigError(Exception):
    pass


@lru_cache(maxsize=1)
def _create_client(url: str, key: str) -> Client:
    return create_client(url, key)


def get_supabase_client() -> Client:
    url = current_app.config["SUPABASE_URL"]
    key = current_app.config["SUPABASE_KEY"]
    if not url or not key:
        raise SupabaseConfigError(
            "SUPABASE_URL and SUPABASE_KEY must be configured"
        )
    return _create_client(url, key)


def is_supabase_configured() -> bool:
    try:
        from flask import current_app
        url = current_app.config.get("SUPABASE_URL", "")
        key = current_app.config.get("SUPABASE_KEY", "")
        return bool(url and key)
    except (RuntimeError, KeyError):
        return False
