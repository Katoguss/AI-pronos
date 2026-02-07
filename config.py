import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    discord_token: str
    zai_api_key: str
    zai_base_url: str
    zai_model: str

def get_settings() -> Settings:
    discord_token = os.getenv("DISCORD_TOKEN", "").strip()
    zai_api_key = os.getenv("ZAI_API_KEY", "").strip()

    if not discord_token:
        raise RuntimeError("DISCORD_TOKEN manquant dans .env")
    if not zai_api_key:
        raise RuntimeError("ZAI_API_KEY manquant dans .env")

    return Settings(
        discord_token=discord_token,
        zai_api_key=zai_api_key,
        zai_base_url=os.getenv("ZAI_API_BASE_URL", "https://api.z.ai/api/paas/v4/").strip(),
        zai_model=os.getenv("ZAI_MODEL", "glm-4.7").strip(),
    )
