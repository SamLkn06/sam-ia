import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, ConversationHandler, filters
)

# États de la conversation d'inscription
NOM, EMAIL, PAYS, LANGUES, COMPETENCES, DISPONIBILITE, NIVEAU = range(7)

NIVEAUX = ["Débutant", "Intermédiaire", "Avancé"]
LANGUES_DISPO = ["Français", "Anglais", "Mandarin", "Portugais", "Arabe", "Haoussa"]
PAYS_AFRIQUE = ["Bénin", "Côte d'Ivoire", "Sénégal", "Mali", "Burkina Faso",
                "Togo", "Niger", "Cameroun", "RDC", "Congo", "Ghana", "Nigeria", "Autre"]

def menu_principal():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Voir mes missions", callback_data="mes_missions")],
        [InlineKeyboardButton("👤 Mon profil", callback_data="mon_profil")],
        [InlineKeyboardButton("💰 Guide retrait", callback_data="guide_retrait")],
        [InlineKeyboardButton("📊 Statistiques", callback_data="stats")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    texte = (
        f"👋 Bonjour *{user.first_name}* !\n\n"
        "Je suis *SAM* — ton assistant IA pour travailler en ligne depuis l'Afrique.\n\n"
        "Je recherche automatiquement les meilleures missions sur :\n"
        "• Appen Connect\n• Remotasks\n• Et bientôt d'autres plateformes\n\n"
        "Je te notifie dès qu'une mission correspond à ton profil 🎯\n\n"
        "Tape /inscription pour créer ton profil et commencer."
    )
    await update.message.reply_text(texte, parse_mode="Markdown")

async def inscription_debut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 *Inscription à SAM*\n\nCommençons ! Quel est ton prénom et nom complet ?",
        parse_mode="Markdown"
    )
    return NOM

async def inscription_nom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nom"] = update.message.text.strip()
    await update.message.reply_text(
        f"Parfait *{context.user_data['nom']}* ! 👍\n\nQuel est ton email ?",
        parse_mode="Markdown"
    )
    return EMAIL

async def inscription_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    if "@" not in email:
        await update.message.reply_text("❌ Email invalide. Réessaie :")
        return EMAIL
    context.user_data["email"] = email

    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton(p, callback_data=f"pays_{p}")] for p in PAYS_AFRIQUE
    ])
    await update.message.reply_text("🌍 Choisis ton pays :", reply_markup=clavier)
    return PAYS

async def inscription_pays(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["pays"] = query.data.replace("pays_", "")

    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{'✅' if l in context.user_data.get('langues_sel', []) else '○'} {l}",
                              callback_data=f"lang_{l}")] for l in LANGUES_DISPO
    ] + [[InlineKeyboardButton("✔️ Confirmer les langues", callback_data="langues_ok")]])
    await query.edit_message_text("🗣 Choisis tes langues (plusieurs possibles) :", reply_markup=clavier)
    return LANGUES

async def inscription_langues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "langues_ok":
        langues = context.user_data.get("langues_sel", ["Français"])
        context.user_data["langues"] = ", ".join(langues)
        await query.edit_message_text(
            f"Langues sélectionnées : *{context.user_data['langues']}*\n\n"
            "💼 Quelles sont tes compétences principales ?\n"
            "(Ex: Traduction, Annotation, Rédaction, Programmation, Design...)",
            parse_mode="Markdown"
        )
        return COMPETENCES

    langue = query.data.replace("lang_", "")
    sel = context.user_data.get("langues_sel", [])
    if langue in sel:
        sel.remove(langue)
    else:
        sel.append(langue)
    context.user_data["langues_sel"] = sel

    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{'✅' if l in sel else '○'} {l}",
                              callback_data=f"lang_{l}")] for l in LANGUES_DISPO
    ] + [[InlineKeyboardButton("✔️ Confirmer les langues", callback_data="langues_ok")]])
    await query.edit_message_reply_markup(reply_markup=clavier)
    return LANGUES

async def inscription_competences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["competences"] = update.message.text.strip()
    await update.message.reply_text(
        "⏰ Combien d'heures par semaine peux-tu travailler ?\n(Tape un nombre, ex: 20)"
    )
    return DISPONIBILITE

async def inscription_disponibilite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        heures = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Entre un nombre svp (ex: 20) :")
        return DISPONIBILITE
    context.user_data["disponibilite"] = heures

    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton(n, callback_data=f"niveau_{n}")] for n in NIVEAUX
    ])
    await update.message.reply_text("📈 Quel est ton niveau d'expérience en travail en ligne ?",
                                    reply_markup=clavier)
    return NIVEAU

async def inscription_niveau(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["niveau"] = query.data.replace("niveau_", "")
    context.user_data["telegram_id"] = str(query.from_user.id)

    import requests as req
    profil = context.user_data.copy()

    try:
        base_url = os.getenv("SAM_API_URL", "http://localhost:5000")
        r = req.post(f"{base_url}/api/utilisateurs", json={
            "nom": profil["nom"],
            "email": profil["email"],
            "telegram_id": profil["telegram_id"],
            "pays": profil["pays"],
            "langues": profil["langues"],
            "competences": profil["competences"],
            "disponibilite": profil["disponibilite"],
            "niveau": profil["niveau"],
        }, timeout=10)
        if r.status_code == 201:
            user_id = r.json().get("id")
            context.user_data["user_id"] = user_id
            statut = "✅ Profil créé avec succès !"
        elif r.status_code == 409:
            statut = "ℹ️ Email déjà enregistré — profil existant."
        else:
            statut = "⚠️ Profil sauvegardé localement."
    except Exception:
        statut = "⚠️ Serveur temporairement indisponible."

    resume = (
        f"{statut}\n\n"
        f"👤 *{profil['nom']}*\n"
        f"🌍 {profil['pays']}\n"
        f"🗣 {profil['langues']}\n"
        f"💼 {profil['competences']}\n"
        f"⏰ {profil['disponibilite']}h/semaine · {profil['niveau']}\n\n"
        "SAM va maintenant chercher les meilleures missions pour toi ! 🚀\n"
        "Tu recevras une alerte dès qu'une mission correspond à ton profil."
    )
    await query.edit_message_text(resume, parse_mode="Markdown", reply_markup=menu_principal())
    return ConversationHandler.END

async def mes_missions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = context.user_data.get("user_id", 1)

    import requests as req
    try:
        base_url = os.getenv("SAM_API_URL", "http://localhost:5000")
        r = req.get(f"{base_url}/api/match/{user_id}?seuil=50", timeout=15)
        if r.status_code == 200:
            data = r.json()
            missions = data.get("missions", [])
            if not missions:
                texte = "😔 Aucune mission disponible pour l'instant.\nSAM va continuer à chercher pour toi !"
            else:
                texte = f"🎯 *{len(missions)} missions trouvées pour toi :*\n\n"
                for i, m in enumerate(missions[:5], 1):
                    score = m.get("evaluation", {}).get("score", "?")
                    texte += f"*{i}. {m['titre']}*\n"
                    texte += f"   📌 {m['plateforme']} · Score: {score}/100\n"
                    texte += f"   💵 {m['remuneration']}\n"
                    texte += f"   🔗 {m['lien']}\n\n"
        else:
            texte = "⚠️ Impossible de charger les missions. Réessaie dans quelques minutes."
    except Exception:
        texte = "⚠️ Serveur en pause. Les missions seront disponibles sous peu."

    await query.edit_message_text(texte, parse_mode="Markdown", reply_markup=menu_principal())

async def guide_retrait(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texte = (
        "💰 *Guide Retrait d'Argent — Afrique de l'Ouest*\n\n"
        "*Option 1 — MTN / Moov Mobile Money*\n"
        "Appen/Remotasks → PayPal → Wise → Mobile Money\n"
        "Délai : 3–5 jours · Frais : ~3%\n\n"
        "*Option 2 — Crypto USDT (Recommandé)*\n"
        "Appen/Remotasks → Coinbase/Skrill → Binance P2P → Mobile Money\n"
        "Délai : 1–2 jours · Frais : ~1.5%\n\n"
        "*Option 3 — Wave*\n"
        "Wise → Wave (Bénin/Côte d'Ivoire)\n"
        "Délai : 24h · Frais : ~2%\n\n"
        "📌 *Conseil SAM :* Commence par PayPal + Wise.\n"
        "Dès que tes revenus dépassent 100$/mois, passe au USDT via Binance P2P.\n\n"
        "Tape /aide_retrait pour un guide détaillé étape par étape."
    )
    await query.edit_message_text(texte, parse_mode="Markdown", reply_markup=menu_principal())

async def annuler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Inscription annulée. Tape /inscription pour recommencer.")
    return ConversationHandler.END

def build_application():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("[SAM Bot] ⚠️ TELEGRAM_BOT_TOKEN manquant dans .env")
        return None

    app = Application.builder().token(token).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("inscription", inscription_debut)],
        states={
            NOM:          [MessageHandler(filters.TEXT & ~filters.COMMAND, inscription_nom)],
            EMAIL:        [MessageHandler(filters.TEXT & ~filters.COMMAND, inscription_email)],
            PAYS:         [CallbackQueryHandler(inscription_pays, pattern="^pays_")],
            LANGUES:      [CallbackQueryHandler(inscription_langues, pattern="^lang_|^langues_ok$")],
            COMPETENCES:  [MessageHandler(filters.TEXT & ~filters.COMMAND, inscription_competences)],
            DISPONIBILITE:[MessageHandler(filters.TEXT & ~filters.COMMAND, inscription_disponibilite)],
            NIVEAU:       [CallbackQueryHandler(inscription_niveau, pattern="^niveau_")],
        },
        fallbacks=[CommandHandler("annuler", annuler)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(mes_missions,    pattern="^mes_missions$"))
    app.add_handler(CallbackQueryHandler(guide_retrait,   pattern="^guide_retrait$"))

    return app

if __name__ == "__main__":
    application = build_application()
    if application:
        print("[SAM Bot] Démarrage du bot Telegram...")
        application.run_polling()
