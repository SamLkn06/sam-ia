import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def envoyer_message(chat_id: str, texte: str) -> bool:
    """Envoie un message Telegram à un utilisateur."""
    try:
        r = requests.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": texte,
            "parse_mode": "Markdown",
        }, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[SAM Notifier] Erreur Telegram: {e}")
        return False

def notifier_missions(utilisateur: dict, missions_filtrees: list) -> None:
    """
    Envoie une alerte Telegram avec les meilleures missions du jour.
    """
    chat_id = utilisateur.get("telegram_id")
    if not chat_id or not missions_filtrees:
        return

    nom = utilisateur.get("nom", "ami(e)")
    nb   = len(missions_filtrees)
    top  = missions_filtrees[:3]

    message = f"*SAM IA* - Bonjour {nom} ! 👋\n"
    message += f"J'ai trouvé *{nb} mission(s)* pour toi aujourd'hui.\n\n"

    for i, m in enumerate(top, 1):
        score  = m["evaluation"]["score"]
        raison = m["evaluation"]["raison"]
        message += f"*{i}. {m['titre']}*\n"
        message += f"   Plateforme: {m['plateforme']}\n"
        message += f"   Revenu: {m['remuneration']}\n"
        message += f"   Score SAM: {score}/100\n"
        message += f"   {raison}\n"
        message += f"   Lien: {m['lien']}\n\n"

    if nb > 3:
        message += f"_+ {nb - 3} autre(s) mission(s) disponible(s) sur ton tableau de bord._\n"

    message += "\n💡 _SAM IA — Travailler en ligne, gagner en Afrique._"

    envoyer_message(chat_id, message)
    print(f"[SAM Notifier] Alerte envoyée à {nom} ({chat_id})")
