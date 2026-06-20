from .base import BaseScraper

APPEN_URL = "https://connect.appen.com/qrp/public/jobs"

class AppenScraper(BaseScraper):
    """
    Scraper pour Appen Connect.
    Appen est l'une des meilleures plateformes accessibles depuis l'Afrique
    francophone, avec des missions en annotation de données et évaluation IA.
    """

    def scrape(self):
        missions = []
        soup = self.fetch(APPEN_URL)
        if not soup:
            return missions

        job_cards = soup.select(".job-card, .opportunity-card, article.job")
        if not job_cards:
            job_cards = soup.select("div[class*='job'], li[class*='job']")

        for card in job_cards:
            try:
                titre_el = card.select_one("h2, h3, .job-title, .title")
                desc_el  = card.select_one("p, .description, .summary")
                lien_el  = card.select_one("a[href]")
                pay_el   = card.select_one(".pay, .rate, .compensation, [class*='pay']")
                lang_el  = card.select_one(".language, [class*='lang']")

                titre = titre_el.get_text(strip=True) if titre_el else "Mission Appen"
                desc  = desc_el.get_text(strip=True)[:300] if desc_el else ""
                lien  = lien_el["href"] if lien_el else APPEN_URL
                if lien.startswith("/"):
                    lien = "https://connect.appen.com" + lien

                pay  = pay_el.get_text(strip=True) if pay_el else None
                lang = lang_el.get_text(strip=True) if lang_el else None

                missions.append(self.build_mission(
                    titre=titre,
                    description=desc,
                    lien=lien,
                    plateforme="Appen",
                    remuneration=pay,
                    langue=lang,
                    categorie="Annotation IA / Évaluation",
                ))
            except Exception as e:
                print(f"[Appen] Erreur parsing carte: {e}")
                continue

        print(f"[Appen] {len(missions)} missions trouvées")
        return missions
