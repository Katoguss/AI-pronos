from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    discord_token: str
    discord_guild_id: int | None

    zai_api_key: str
    zai_base_url: str
    zai_model: str

    zai_search_engine: str
    zai_search_recency_filter: str
    zai_search_count: int


def _get_int(name: str) -> int | None:
    v = os.getenv(name, "").strip()
    if not v:
        return None
    try:
        return int(v)
    except ValueError:
        raise RuntimeError(f"{name} invalide (doit être un entier)")


def get_settings() -> Settings:
    discord_token = os.getenv("DISCORD_TOKEN", "").strip()
    zai_api_key = os.getenv("ZAI_API_KEY", "").strip()

    if not discord_token:
        raise RuntimeError("DISCORD_TOKEN manquant dans .env")
    if not zai_api_key:
        raise RuntimeError("ZAI_API_KEY manquant dans .env")

    base_url = os.getenv("ZAI_API_BASE_URL", "https://api.z.ai/api/paas/v4").strip()
    if base_url.endswith("/"):
        base_url = base_url[:-1]

    count_raw = os.getenv("ZAI_SEARCH_COUNT", "8").strip() or "8"
    try:
        search_count = int(count_raw)
    except ValueError:
        raise RuntimeError("ZAI_SEARCH_COUNT invalide (doit être un entier)")

    return Settings(
        discord_token=discord_token,
        discord_guild_id=_get_int("DISCORD_GUILD_ID"),
        zai_api_key=zai_api_key,
        zai_base_url=base_url,
        zai_model=os.getenv("ZAI_MODEL", "glm-4.7").strip(),
        zai_search_engine=os.getenv("ZAI_SEARCH_ENGINE", "search-prime").strip(),
        zai_search_recency_filter=os.getenv("ZAI_SEARCH_RECENCY_FILTER", "oneWeek").strip(),
        zai_search_count=search_count,
    )
