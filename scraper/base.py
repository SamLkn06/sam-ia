import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
}

class BaseScraper:
    """Classe de base pour tous les scrapers SAM."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch(self, url, timeout=15):
        try:
            r = self.session.get(url, timeout=timeout)
            r.raise_for_status()
            return BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            print(f"[SAM Scraper] Erreur fetch {url}: {e}")
            return None

    def build_mission(self, titre, description, lien, plateforme,
                      remuneration=None, langue=None, categorie=None):
        return {
            "titre": titre,
            "description": description,
            "lien": lien,
            "plateforme": plateforme,
            "remuneration": remuneration or "Non précisé",
            "langue": langue or "Toutes",
            "categorie": categorie or "Général",
            "date_scraping": datetime.utcnow().isoformat(),
        }
