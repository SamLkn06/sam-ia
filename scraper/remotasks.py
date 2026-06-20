from .base import BaseScraper

REMOTASKS_URL = "https://www.remotasks.com/en/tasks"

class RemotasksScraper(BaseScraper):
    """
    Scraper pour Remotasks (Scale AI).
    Très accessible depuis le Bénin, paiement via PayPal/Coinbase.
    Missions : labelling images, transcription audio, traduction.
    """

    CATEGORIES_AFRICA = [
        "Image annotation",
        "Audio transcription",
        "Translation",
        "Data collection",
        "Video annotation",
    ]

    def scrape(self):
        missions = []
        soup = self.fetch(REMOTASKS_URL)
        if not soup:
            return missions

        task_cards = soup.select(".task-card, .project-card, [class*='task-item']")
        if not task_cards:
            task_cards = soup.select("div[data-testid*='task'], article")

        for card in task_cards:
            try:
                titre_el = card.select_one("h2, h3, h4, .task-name, .project-name")
                desc_el  = card.select_one("p, .task-description, .description")
                lien_el  = card.select_one("a[href]")
                pay_el   = card.select_one(".pay-rate, .earning, [class*='earn']")

                titre = titre_el.get_text(strip=True) if titre_el else "Mission Remotasks"
                desc  = desc_el.get_text(strip=True)[:300] if desc_el else ""
                lien  = lien_el["href"] if lien_el else REMOTASKS_URL
                if lien.startswith("/"):
                    lien = "https://www.remotasks.com" + lien
                pay   = pay_el.get_text(strip=True) if pay_el else None

                categorie = "Général"
                for cat in self.CATEGORIES_AFRICA:
                    if cat.lower() in titre.lower() or cat.lower() in desc.lower():
                        categorie = cat
                        break

                missions.append(self.build_mission(
                    titre=titre,
                    description=desc,
                    lien=lien,
                    plateforme="Remotasks",
                    remuneration=pay,
                    langue="Multilingue",
                    categorie=categorie,
                ))
            except Exception as e:
                print(f"[Remotasks] Erreur parsing: {e}")
                continue

        print(f"[Remotasks] {len(missions)} missions trouvées")
        return missions
