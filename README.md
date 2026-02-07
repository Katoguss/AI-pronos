\# FabioPronos (Discord Bot) — Pronostics via Z.ai



\## Fonctionnement

Commande `/prono` :

1\) tu choisis (optionnel) une cote, un niveau de risque, et/ou une demande (match/compétition)

2\) le bot appelle Z.ai (chat completions)

3\) Z.ai peut utiliser son outil Web Search intégré (autorisé via `tools`)

4\) le bot envoie le pronostic en DM

5\) le bot répond dans le salon : "Pronostique envoyé en message privé"



Référence Z.ai :

\- Endpoint + auth Bearer \[https://docs.z.ai/guides/develop/http/introduction](https://docs.z.ai/guides/develop/http/introduction)

\- Paramètres `tools` incluant Web Search \[https://docs.z.ai/api-reference/llm/chat-completion](https://docs.z.ai/api-reference/llm/chat-completion)



---



\## Prérequis

\- Python 3.10+

\- Un bot Discord (token)

\- Une clé API Z.ai



---



\## Installation (PC / VPS)

```bash

python -m venv .venv

\# Windows:

\# .venv\\Scripts\\activate

\# Linux/Mac:

source .venv/bin/activate



pip install -r requirements.txt



