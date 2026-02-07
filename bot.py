import discord
from discord import app_commands

from config import get_settings
from prompts import build_prompt
from zai_client import zai_prono, ZaiApiError

RISK_CHOICES = [
    app_commands.Choice(name="Petit (1.2 - 1.9)", value="petit"),
    app_commands.Choice(name="Moyen (1.9 - 3.0)", value="moyen"),
    app_commands.Choice(name="Haut (3.0 - 6.0)", value="haut"),
]

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

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
    # On confirme qu'on traite la demande (sinon Discord timeout)
    await interaction.response.defer(thinking=True)

    risk_value = risque.value if risque else None
    prompt = build_prompt(cote=cote, risk=risk_value, demande=demande)

    try:
        prono_txt = await zai_prono(prompt)
    except ZaiApiError as e:
        await interaction.followup.send(f"Erreur IA (Z.ai): {e}", ephemeral=True)
        return
    except Exception as e:
        await interaction.followup.send(f"Erreur inconnue: {e}", ephemeral=True)
        return

    # Envoi du DM
    try:
        await interaction.user.send(
            "Voici ton pronostic :\n\n"
            f"{prono_txt}\n\n"
            "⚠️ Pronostic non garanti. Mise responsable."
        )
    except discord.Forbidden:
        await interaction.followup.send(
            "Impossible de t'envoyer un DM (messages privés fermés). Active tes MP puis réessaie.",
            ephemeral=True,
        )
        return

    await interaction.followup.send("Pronostique envoyé en message privé.")

@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Connecté: {client.user} (ID={client.user.id})")

def main():
    s = get_settings()
    client.run(s.discord_token)

if __name__ == "__main__":
    main()
