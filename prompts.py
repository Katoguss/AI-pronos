def odds_constraints_from_risk(risk: str | None) -> str:
    if not risk:
        return "Aucune contrainte stricte sur la cote. Propose une cote cohérente."

    r = risk.lower().strip()
    if r == "haut":
        return "Cote totale visée entre 3.0 et 6.0 (risque HAUT)."
    if r == "moyen":
        return "Cote totale visée entre 1.9 et 3.0 (risque MOYEN)."
    if r == "petit":
        return "Cote totale visée entre 1.2 et 1.9 (risque PETIT)."
    return "Aucune contrainte stricte sur la cote. Propose une cote cohérente."


def build_prompt(cote: str | None, risk: str | None, demande: str | None) -> str:
    cote_line = f"Cote visée (texte utilisateur): {cote}" if cote else "Cote visée: non spécifiée."
    demande_line = (
        f"Demande utilisateur: {demande}"
        if demande
        else "Demande: propose un prono pertinent (matchs du jour si possible)."
    )

    return f"""
Tu es un expert en pronostics football.
Tu dois être clair, prudent et transparent.

Tu as accès à un outil `web_search`.
Avant de proposer un ticket, utilise `web_search` pour récupérer des infos récentes et vérifiables (forme, blessures, compositions probables, enjeu, dynamique, H2H si pertinent).
Ne prétends pas avoir des stats exactes si tu ne les as pas.

Contraintes de risque:
- {odds_constraints_from_risk(risk)}
- {cote_line}
- {demande_line}

Exigences:
1) Fais 1 à 2 recherches web maximum avec `web_search` (requêtes courtes et ciblées).
2) Donne UN ticket maximum (simple OU combiné selon le risque).
3) Justification courte et factuelle, sans inventer de statistiques.
4) Donne une estimation de probabilité (approx), une cote estimée (approx), et un niveau de confiance.
5) Dans ANALYSE, ajoute une puce "Sources:" avec 2-4 URLs utilisées.
6) Termine par un avertissement: "Pronostic non garanti, mise responsable."

Format EXACT à respecter:
TITRE: ...
TICKET:
- Match : ...
(si combiné, liste chaque match, Match 1, Match 2, etc...)
- Pari : ...
- Cote estimée : ...
ANALYSE (puces):
- ...
SOURCES:
- ...
""".strip()
