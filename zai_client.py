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
            return "Crédits/solde IA insuffisants (code 1113)."

        if status_code == 429:
            details = f" (code {code})" if code else ""
            return f"❌︱Limite / quota IA atteint{details}. Réessaie plus tard"

        details = f" (code {code})" if code else ""
        if msg:
            return f"{prefix} HTTP {status_code}{details}: {msg}"

    return f"{prefix} HTTP {status_code}: {text}"


def _extract_message_text(message: Any) -> str:
    if not isinstance(message, dict):
        return ""

    content = message.get("content")

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, dict):
        t = content.get("text") or content.get("content")
        if isinstance(t, str):
            return t.strip()

    if isinstance(content, list):
        chunks: list[str] = []
        for part in content:
            if isinstance(part, str):
                if part.strip():
                    chunks.append(part.strip())
                continue

            if isinstance(part, dict):
                t = part.get("text") or part.get("content")
                if isinstance(t, str) and t.strip():
                    chunks.append(t.strip())
        return "\n\n".join(chunks).strip()

    return ""


def _extract_tool_calls(message: Any) -> list[dict[str, Any]]:
    if not isinstance(message, dict):
        return []
    tc = message.get("tool_calls")
    if isinstance(tc, list):
        return [x for x in tc if isinstance(x, dict)]
    return []


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


async def _zai_chat_completions(
    *,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None,
    tool_choice: str | None,
    user_id: str | None,
) -> dict[str, Any]:
    s = get_settings()
    url = s.zai_base_url.rstrip("/") + "/chat/completions"

    headers = {
        "Authorization": f"Bearer {s.zai_api_key}",
        "Content-Type": "application/json",
        "Accept-Language": "fr-FR,fr",
    }

    payload: dict[str, Any] = {
        "model": s.zai_model,
        "messages": messages,
        "temperature": 0.6,
        "top_p": 0.9,
        "max_tokens": 900,
        "stream": False,
        "response_format": {"type": "text"},
    }
    if tools is not None:
        payload["tools"] = tools
    if tool_choice is not None:
        payload["tool_choice"] = tool_choice
    if user_id:
        payload["user_id"] = user_id

    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.post(url, headers=headers, json=payload)

    if r.status_code != 200:
        raise ZaiApiError(_pretty_zai_http_error("Z.ai Chat", r.status_code, r.text))

    try:
        return r.json()
    except json.JSONDecodeError:
        raise ZaiApiError("Z.ai Chat: réponse JSON invalide")


def _web_search_function_tool_schema() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Recherche web pour obtenir des infos récentes (match, blessures, compositions probables, forme).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "La requête à rechercher"},
                    "count": {"type": "integer", "description": "Nombre de résultats (1-10)"},
                },
                "required": ["query"],
            },
        },
    }


def _parse_tool_args(raw_args: Any) -> dict[str, Any]:
    if isinstance(raw_args, dict):
        return raw_args
    if isinstance(raw_args, str) and raw_args.strip():
        try:
            j = json.loads(raw_args)
            if isinstance(j, dict):
                return j
        except Exception:
            return {}
    return {}


async def zai_prono(prompt: str, *, user_id: str | None = None) -> str:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": "Tu réponds en français (fr-FR)."},
        {"role": "user", "content": prompt},
    ]

    tools = [_web_search_function_tool_schema()]

    last_request_id: str | None = None
    last_finish_reason: str | None = None

    for _round in range(3):
        data = await _zai_chat_completions(
            messages=messages,
            tools=tools,
            tool_choice="auto",
            user_id=user_id,
        )

        if isinstance(data, dict):
            rid = data.get("request_id")
            if isinstance(rid, str) and rid.strip():
                last_request_id = rid.strip()

        choices = data.get("choices") if isinstance(data, dict) else None
        choice0 = choices[0] if isinstance(choices, list) and choices else None

        message = choice0.get("message") if isinstance(choice0, dict) else None
        finish_reason = choice0.get("finish_reason") if isinstance(choice0, dict) else None
        last_finish_reason = str(finish_reason or "").strip() or None

        text = _extract_message_text(message)
        if text:
            return text

        tool_calls = _extract_tool_calls(message)
        if tool_calls:
            messages.append({"role": "assistant", "content": "", "tool_calls": tool_calls})

            for tc in tool_calls:
                tc_id = tc.get("id")
                fn = tc.get("function") if isinstance(tc.get("function"), dict) else {}
                name = fn.get("name")
                args = _parse_tool_args(fn.get("arguments"))

                if name != "web_search":
                    tool_msg: dict[str, Any] = {
                        "role": "tool",
                        "content": f"Tool non supporté: {name}",
                    }
                    if isinstance(tc_id, str) and tc_id.strip():
                        tool_msg["tool_call_id"] = tc_id
                    messages.append(tool_msg)
                    continue

                query = str(args.get("query") or "").strip()
                if not query:
                    tool_msg = {"role": "tool", "content": "Erreur: query manquante"}
                    if isinstance(tc_id, str) and tc_id.strip():
                        tool_msg["tool_call_id"] = tc_id
                    messages.append(tool_msg)
                    continue

                count_raw = args.get("count")
                try:
                    count = int(count_raw) if count_raw is not None else None
                except Exception:
                    count = None

                results = await zai_web_search(query, count=count, user_id=user_id)
                tool_content = format_web_results(results)

                tool_msg = {"role": "tool", "content": tool_content}
                if isinstance(tc_id, str) and tc_id.strip():
                    tool_msg["tool_call_id"] = tc_id

                messages.append(tool_msg)

            continue

        break

    fr = last_finish_reason or "unknown"
    rid = f" request_id={last_request_id}" if last_request_id else ""
    raise ZaiApiError(
        f"❌︱L'IA a renvoyé une réponse vide (finish_reason={fr}{rid}). Relance la commande; si ça persiste, change de MODEL"
    )
