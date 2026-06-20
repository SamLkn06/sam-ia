import os
import json
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

def calculer_score(profil_utilisateur: dict, mission: dict) -> dict:
    """
    Utilise Claude pour évaluer la compatibilité entre un profil
    et une mission. Retourne un score et une explication.
    """
    prompt = f"""
Tu es SAM, un assistant IA qui aide les Africains à trouver du travail en ligne.

PROFIL UTILISATEUR:
- Nom: {profil_utilisateur.get('nom', 'Inconnu')}
- Langues: {', '.join(profil_utilisateur.get('langues', ['Français']))}
- Compétences: {', '.join(profil_utilisateur.get('competences', []))}
- Disponibilité: {profil_utilisateur.get('disponibilite', 'Temps partiel')} heures/semaine
- Pays: {profil_utilisateur.get('pays', 'Bénin')}
- Niveau: {profil_utilisateur.get('niveau', 'Débutant')}

MISSION DISPONIBLE:
- Titre: {mission.get('titre')}
- Plateforme: {mission.get('plateforme')}
- Catégorie: {mission.get('categorie')}
- Langue requise: {mission.get('langue')}
- Rémunération: {mission.get('remuneration')}
- Description: {mission.get('description', '')[:200]}

Évalue la compatibilité et réponds UNIQUEMENT en JSON valide:
{{
  "score": <entier 0-100>,
  "recommande": <true/false>,
  "raison": "<explication courte en français, max 2 phrases>",
  "conseil": "<conseil pratique pour postuler, max 1 phrase>"
}}
"""
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        texte = response.content[0].text.strip()
        return json.loads(texte)
    except Exception as e:
        print(f"[SAM Matcher] Erreur Claude: {e}")
        return {
            "score": 50,
            "recommande": True,
            "raison": "Analyse automatique indisponible.",
            "conseil": "Consulte la mission directement sur la plateforme."
        }

def filtrer_missions(profil: dict, missions: list, seuil: int = 60) -> list:
    """
    Filtre et classe les missions pour un utilisateur donné.
    Ne retourne que celles avec un score >= seuil.
    """
    resultats = []
    for mission in missions:
        evaluation = calculer_score(profil, mission)
        if evaluation.get("score", 0) >= seuil:
            resultats.append({**mission, "evaluation": evaluation})

    resultats.sort(key=lambda m: m["evaluation"]["score"], reverse=True)
    print(f"[SAM Matcher] {len(resultats)}/{len(missions)} missions retenues pour {profil.get('nom')}")
    return resultats
