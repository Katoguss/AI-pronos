from __future__ import annotations

import discord
from discord import app_commands

from config import get_settings
from prompts import build_prompt
from zai_client import ZaiApiError, format_web_results, zai_prono, zai_web_search

RISK_CHOICES = [
    app_commands.Choice(name="Petit (1.2 - 1.9)", value="petit"),
    app_commands.Choice(name="Moyen (1.9 - 3.0)", value="moyen"),
    app_commands.Choice(name="Haut (3.0 - 6.0)", value="haut"),
]

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def _split_for_discord(text: str, limit: int = 1900) -> list[str]:
    t = (text or "").strip()
    if not t:
        return ["(vide)"]

    parts: list[str] = []
    buf: list[str] = []
    size = 0

    for line in t.splitlines(keepends=True):
        if size + len(line) > limit and buf:
            parts.append("".join(buf).rstrip())
            buf = []
            size = 0

        if len(line) > limit:
            for i in range(0, len(line), limit):
                chunk = line[i : i + limit]
                if chunk.strip():
                    parts.append(chunk.rstrip())
            continue

        buf.append(line)
        size += len(line)

    if buf:
        parts.append("".join(buf).rstrip())

    return parts


def _build_search_query(demande: str | None) -> str:
    if demande and demande.strip():
        d = demande.strip()
        return f"{d} preview blessures composition probable forme enjeux".strip()
    return "matchs football aujourd'hui preview blessures composition probable forme enjeux".strip()


@tree.command(name="prono", description="Génère un pronostic football et l'envoie en DM.")
@app_commands.describe(
    cote="(optionnel) Cote visée (ex: 2.4, 'entre 2 et 3')",
    risque="(optionnel) Niveau du risque",
    demande="(optionnel) Match/compétition (ex: 'PSG-OM', 'Ligue 1 aujourd’hui')",
)
@app_commands.choices(risque=RISK_CHOICES)
async def prono(
    interaction: discord.Interaction,
    cote: str | None = None,
    risque: app_commands.Choice[str] | None = None,
    demande: str | None = None,
):
    await interaction.response.defer(thinking=True)

    s = get_settings()
    risk_value = risque.value if risque else None
    user_id = f"discord:{interaction.user.id}"

    sources_block: str | None = None
    try:
        q = _build_search_query(demande)
        results = await zai_web_search(q, user_id=user_id)
        sources_block = format_web_results(results[: s.zai_search_count])
    except Exception:
        sources_block = None

    prompt = build_prompt(cote=cote, risk=risk_value, demande=demande, sources_block=sources_block)

    try:
        prono_txt = await zai_prono(prompt, user_id=user_id)
    except ZaiApiError as e:
        await interaction.followup.send(f"Erreur IA (Z.ai): {e}", ephemeral=True)
        return
    except Exception as e:
        await interaction.followup.send(f"Erreur inconnue: {e}", ephemeral=True)
        return

    try:
        chunks = _split_for_discord("Voici ton pronostic :\n\n" + prono_txt)
        for c in chunks:
            await interaction.user.send(c)
    except discord.Forbidden:
        await interaction.followup.send(
            "Impossible de t'envoyer un DM (messages privés fermés). Active tes MP puis réessaie.",
            ephemeral=True,
        )
        return
    except discord.HTTPException as e:
        await interaction.followup.send(f"Erreur Discord lors de l'envoi du DM: {e}", ephemeral=True)
        return

    await interaction.followup.send("Pronostique envoyé en message privé")


@client.event
async def on_ready():
    s = get_settings()

    if s.discord_guild_id:
        guild = discord.Object(id=s.discord_guild_id)
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)
    else:
        await tree.sync()

    print(f"✅ Connecté: {client.user} (ID={client.user.id})")


def main():
    s = get_settings()
    client.run(s.discord_token)


if __name__ == "__main__":
    main()
