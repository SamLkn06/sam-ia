from flask import Blueprint, request, jsonify
from .models import db, Utilisateur, Mission
from scraper import run_all_scrapers
from matcher.engine import filtrer_missions
from notifier.telegram import notifier_missions
from retrait.guide import get_guide, get_methode_recommandee, afficher_comparaison

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "sam": "en ligne"})

@api.route("/utilisateurs", methods=["POST"])
def creer_utilisateur():
    data = request.json or {}
    for champ in ["nom", "email"]:
        if champ not in data:
            return jsonify({"erreur": f"Champ requis: {champ}"}), 400
    if Utilisateur.query.filter_by(email=data["email"]).first():
        return jsonify({"erreur": "Email déjà enregistré"}), 409
    u = Utilisateur(
        nom=data["nom"], email=data["email"],
        telegram_id=data.get("telegram_id"),
        pays=data.get("pays", "Bénin"),
        langues=data.get("langues", "Français"),
        competences=data.get("competences", ""),
        disponibilite=data.get("disponibilite", 20),
        niveau=data.get("niveau", "Débutant"),
    )
    db.session.add(u)
    db.session.commit()
    return jsonify({"message": "Utilisateur créé", "id": u.id}), 201

@api.route("/utilisateurs/<int:user_id>", methods=["GET"])
def get_utilisateur(user_id):
    u = Utilisateur.query.get_or_404(user_id)
    return jsonify(u.to_dict())

@api.route("/missions", methods=["GET"])
def lister_missions():
    missions = Mission.query.filter_by(active=True).order_by(Mission.date_scraping.desc()).limit(50).all()
    return jsonify([m.to_dict() for m in missions])

@api.route("/missions/sync", methods=["POST"])
def synchroniser_missions():
    nouvelles = run_all_scrapers()
    nb = 0
    for m in nouvelles:
        if not Mission.query.filter_by(lien=m["lien"]).first():
            db.session.add(Mission(
                titre=m["titre"], description=m["description"],
                lien=m["lien"], plateforme=m["plateforme"],
                remuneration=m["remuneration"], langue=m["langue"],
                categorie=m["categorie"],
            ))
            nb += 1
    db.session.commit()
    return jsonify({"message": f"{nb} nouvelles missions", "total": len(nouvelles)})

@api.route("/match/<int:user_id>", methods=["GET"])
def matcher_utilisateur(user_id):
    u = Utilisateur.query.get_or_404(user_id)
    missions = [m.to_dict() for m in Mission.query.filter_by(active=True).all()]
    seuil = int(request.args.get("seuil", 60))
    resultats = filtrer_missions(u.to_dict(), missions, seuil=seuil)
    return jsonify({"utilisateur": u.nom, "missions": resultats})

@api.route("/notifier/<int:user_id>", methods=["POST"])
def notifier_utilisateur(user_id):
    u = Utilisateur.query.get_or_404(user_id)
    missions = [m.to_dict() for m in Mission.query.filter_by(active=True).all()]
    resultats = filtrer_missions(u.to_dict(), missions, seuil=60)
    profil = u.to_dict()
    profil["telegram_id"] = u.telegram_id
    notifier_missions(profil, resultats)
    return jsonify({"message": f"Notification envoyée à {u.nom}", "nb": len(resultats)})

@api.route("/retrait/guide/<methode>", methods=["GET"])
def retrait_guide(methode):
    guide = get_guide(methode)
    if not guide:
        return jsonify({"erreur": "Méthode inconnue. Choix: paypal_wise_momo, usdt_binance, wave"}), 404
    return jsonify(guide)

@api.route("/retrait/recommandation", methods=["GET"])
def retrait_recommandation():
    revenus = float(request.args.get("revenus", 50))
    methode = get_methode_recommandee(revenus)
    guide = get_guide(methode)
    return jsonify({"revenus_mensuels": revenus, "methode_recommandee": methode, "guide": guide})

@api.route("/retrait/comparaison", methods=["GET"])
def retrait_comparaison():
    return jsonify(afficher_comparaison())
