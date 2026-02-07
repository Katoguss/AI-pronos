from __future__ import annotations

import json
from typing import Any

import httpx

from config import get_settings


class ZaiApiError(Exception):
    pass


def _pretty_zai_http_error(prefix: str, status_code: int, text: str) -> str:
    try:
        data = json.loads(text)
    except Exception:
        return f"{prefix} HTTP {status_code}: {text}"

    err = data.get("error") if isinstance(data, dict) else None
    if isinstance(err, dict):
        code = str(err.get("code") or "").strip()
        msg = str(err.get("message") or "").strip()

        if status_code == 429 and code == "1113":
            return "Crédits/solde Z.ai insuffisants (code 1113). Recharge ton compte Z.ai ou active un pack/abonnement, puis réessaie."

        if status_code == 429:
            details = f" (code {code})" if code else ""
            return f"Limite / quota Z.ai atteint{details}. Réessaie plus tard ou augmente ton quota."

        details = f" (code {code})" if code else ""
        if msg:
            return f"{prefix} HTTP {status_code}{details}: {msg}"

    return f"{prefix} HTTP {status_code}: {text}"


def format_web_results(results: list[dict[str, Any]]) -> str:
    if not results:
        return "(Aucun résultat)"

    lines: list[str] = []
    for i, item in enumerate(results, start=1):
        title = (item.get("title") or "").strip()
        link = (item.get("link") or "").strip()
        content = (item.get("content") or "").strip()
        publish_date = (item.get("publish_date") or "").strip()

        chunk = [f"[{i}] {title}"]
        if publish_date:
            chunk.append(f"Date: {publish_date}")
        if link:
            chunk.append(f"URL: {link}")
        if content:
            chunk.append(f"Résumé: {content}")
        lines.append("\n".join(chunk))

    return "\n\n".join(lines)


async def zai_web_search(
    search_query: str,
    *,
    count: int | None = None,
    search_recency_filter: str | None = None,
    user_id: str | None = None,
) -> list[dict[str, Any]]:
    s = get_settings()
    url = s.zai_base_url.rstrip("/") + "/web_search"

    headers = {
        "Authorization": f"Bearer {s.zai_api_key}",
        "Content-Type": "application/json",
        "Accept-Language": "fr-FR,fr",
    }

    payload: dict[str, Any] = {
        "search_engine": s.zai_search_engine,
        "search_query": search_query,
        "count": count if count is not None else s.zai_search_count,
        "search_recency_filter": (
            search_recency_filter if search_recency_filter is not None else s.zai_search_recency_filter
        ),
    }
    if user_id:
        payload["user_id"] = user_id

    async with httpx.AsyncClient(timeout=45) as client:
        r = await client.post(url, headers=headers, json=payload)

    if r.status_code != 200:
        raise ZaiApiError(_pretty_zai_http_error("Z.ai Web Search", r.status_code, r.text))

    try:
        data = r.json()
    except json.JSONDecodeError:
        raise ZaiApiError("Z.ai Web Search: réponse JSON invalide")

    return data.get("search_result") or []


async def zai_prono(prompt: str, *, user_id: str | None = None) -> str:
    s = get_settings()
    url = s.zai_base_url.rstrip("/") + "/chat/completions"

    headers = {
        "Authorization": f"Bearer {s.zai_api_key}",
        "Content-Type": "application/json",
        "Accept-Language": "fr-FR,fr",
    }

    payload: dict[str, Any] = {
        "model": s.zai_model,
        "messages": [
            {"role": "system", "content": "Tu réponds en français (fr-FR)."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 900,
    }
    if user_id:
        payload["user_id"] = user_id

    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.post(url, headers=headers, json=payload)

    if r.status_code != 200:
        raise ZaiApiError(_pretty_zai_http_error("Z.ai Chat", r.status_code, r.text))

    try:
        data = r.json()
    except json.JSONDecodeError:
        raise ZaiApiError("Z.ai Chat: réponse JSON invalide")

    try:
        return (data["choices"][0]["message"]["content"] or "").strip()
    except Exception:
        raise ZaiApiError(f"Z.ai Chat: format de réponse inattendu: {data}")
