import httpx
from config import get_settings

class ZaiApiError(Exception):
    pass

async def zai_prono(prompt: str) -> str:
    s = get_settings()
    url = s.zai_base_url.rstrip("/") + "/chat/completions"

    headers = {
        "Authorization": f"Bearer {s.zai_api_key}",
        "Content-Type": "application/json",
        "Accept-Language": "fr-FR,fr",
    }

    payload = {
        "model": s.zai_model,
        "messages": [
            {"role": "system", "content": "Tu réponds en français (fr-FR)."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 900,

        # Autoriser l’usage d’outils côté Z.ai
        # La doc indique que tools peut inclure un Web Search object [Source](https://docs.z.ai/api-reference/llm/chat-completion)
        "tools": [
            {"type": "web_search"}
        ],
        "tool_choice": "auto",
    }

    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.post(url, headers=headers, json=payload)

    if r.status_code != 200:
        raise ZaiApiError(f"Z.ai HTTP {r.status_code}: {r.text}")

    data = r.json()
    return data["choices"][0]["message"]["content"]
