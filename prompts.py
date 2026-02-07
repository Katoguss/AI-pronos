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


def build_prompt(cote: str | None, risk: str | None, demande: str | None, *, sources_block: str | None) -> str:
    cote_line = f"Cote visée (texte utilisateur): {cote}" if cote else "Cote visée: non spécifiée."
    demande_line = (
        f"Demande utilisateur: {demande}"
        if demande
        else "Demande: propose un prono pertinent (matchs du jour si possible)."
    )

    sources = sources_block.strip() if sources_block else "(Aucune source web fournie.)"

    return f"""
Tu es un expert en pronostics football.
Tu dois être clair, prudent et transparent.

Contraintes de risque:
- {odds_constraints_from_risk(risk)}
- {cote_line}
- {demande_line}

Sources web (résumés + liens) à utiliser pour l'analyse (ne pas inventer de stats, n'utiliser que ce qui est cohérent avec ces sources):
{sources}

Exigences:
1) Base-toi sur les sources ci-dessus (forme, blessures, enjeu, probable XI, dynamique, H2H si pertinent).
2) Donne UN ticket maximum (simple OU combiné selon le risque).
3) Justification courte et factuelle, sans inventer de statistiques.
4) Donne une estimation de probabilité (approx), une cote estimée (approx), et un niveau de confiance.
5) Dans ANALYSE, ajoute une puce "Sources:" avec 2-4 URLs utilisées.
6) Termine par un avertissement: "Pronostic non garanti, mise responsable."

Format EXACT à respecter:
TITRE:
TICKET:
- Match 1: ...
- Pari: ...
(si combiné, liste chaque match)
ANALYSE (puces):
- ...
COTE ESTIMÉE:
PROBABILITÉ ESTIMÉE:
CONFIANCE:
AVERTISSEMENT:
""".strip()
