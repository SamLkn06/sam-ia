import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from .models import db
from .routes import api

load_dotenv()

def scraping_auto():
    """Tâche planifiée: scrape toutes les 6h et sauvegarde en base."""
    try:
        from scraper import run_all_scrapers
        from api.models import Mission
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
        print(f"[SAM Auto] {nb} nouvelles missions ajoutées")
    except Exception as e:
        print(f"[SAM Auto] Erreur scraping: {e}")

def create_app():
    app = Flask(__name__, template_folder="../templates")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "sam-secret-2025")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///sam.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.register_blueprint(api)

    with app.app_context():
        db.create_all()
        print("[SAM] Base de données initialisée")

    @app.route("/")
    def index():
        return render_template("index.html")

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=scraping_auto, trigger="interval", hours=6, id="scraping_auto")
    scheduler.start()
    print("[SAM] Scraping automatique activé (toutes les 6h)")

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"[SAM] Démarrage sur http://0.0.0.0:{port}")
    app.run(debug=False, host="0.0.0.0", port=port)
