from .appen import AppenScraper
from .remotasks import RemotasksScraper

def run_all_scrapers():
    """Lance tous les scrapers et retourne la liste combinée de missions."""
    missions = []
    for ScraperClass in [AppenScraper, RemotasksScraper]:
        try:
            scraper = ScraperClass()
            missions.extend(scraper.scrape())
        except Exception as e:
            print(f"[SAM] Erreur scraper {ScraperClass.__name__}: {e}")
    print(f"[SAM] Total missions collectées: {len(missions)}")
    return missions
