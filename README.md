# FabioPronos (Discord Bot) — /prono via Z.ai

## Ce que fait le bot
Commande slash `/prono`:
- l’utilisateur (optionnel) indique une cote visée, un niveau de risque, et/ou une demande (match / compétition)
- Z.ai fait la recherche web via `web_search` (tool-calls) en se basant sur ta demande
- le bot envoie ta demande à Z.ai `chat/completions` et exécute les tool-calls si nécessaire
- le bot envoie le pronostic en DM
- le bot répond dans le salon: `Pronostique envoyé en message privé`

## Commande
`/prono` (serveur uniquement)
- Salon autorisé: `1469765893943988224`
- Accès: uniquement les membres ayant l’un de ces rôles (IDs): `1469711683277557833` ou `1466017041977966632`
- `cote` (optionnel, texte) : ex `2.4` / `entre 2 et 3`
- `risque` (optionnel, sélection) :
  - `Petit (1.2 - 1.9)`
  - `Moyen (1.9 - 3.0)`
  - `Haut (3.0 - 6.0)`
- `demande` (optionnel, texte) : ex `PSG-OM`, `Ligue 1 aujourd’hui`, `matchs de Serie A ce soir`

## Prérequis
- Python 3.10+
- Token bot Discord
- API Key Z.ai

## Installation (PC/VPS)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuration (.env)
1) Copier le template:
```bash
cp .env.example .env
```
2) Remplir `.env`:
- `DISCORD_TOKEN` (obligatoire)
- `ZAI_API_KEY` (obligatoire)
- `DISCORD_GUILD_ID` (optionnel mais recommandé en dev): ID du serveur Discord de test

Note: `.env` ne doit pas être commit (il est ignoré par `.gitignore`).

## Lancer
```bash
python bot.py
```

## Ajouter le bot à un serveur
Invite URL (remplace `CLIENT_ID`):
```
https://discord.com/oauth2/authorize?client_id=CLIENT_ID&scope=bot%20applications.commands&permissions=2048
```
- `permissions=2048` = Send Messages (minimum pour répondre dans le salon)

## Synchronisation des commandes
- Si `DISCORD_GUILD_ID` est défini, la commande est synchronisée instantanément sur ce serveur.
- Sinon, sync globale (peut prendre du temps à apparaître).

## Dépannage
- Si le bot ne peut pas envoyer de DM: l’utilisateur doit autoriser les messages privés du serveur.
- Si `/prono` n’apparaît pas: vérifier que le bot a le scope `applications.commands` et relancer le bot.
- Erreur `HTTP 429` avec message `余额不足...` / code `1113`: ça veut dire *crédits Z.ai insuffisants*. Il faut recharger ton compte Z.ai / activer un pack, ou utiliser une API key d’un compte avec du solde.
- Si tu reçois en DM seulement `Voici ton pronostic :` (vide): Z.ai renvoie parfois une réponse vide. Le bot affiche maintenant une erreur explicite au lieu d’envoyer un DM vide. Si ça arrive encore, relance la commande ou teste un autre modèle (`ZAI_MODEL`).

## Références Z.ai
- Chat Completions: https://docs.z.ai/api-reference/llm/chat-completion
- Web Search: https://docs.z.ai/api-reference/tools/web-search
