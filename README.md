# SAM IA — Smart African Money

> L'IA qui trouve du travail en ligne et te permet de gagner de l'argent depuis l'Afrique.

## Lancer le projet

```bash
# 1. Cloner et installer
pip install -r requirements.txt

# 2. Configurer les variables
cp .env.example .env
# Remplis ANTHROPIC_API_KEY et TELEGRAM_BOT_TOKEN

# 3. Démarrer
python -m api.app
```

## Structure
```
sam/
├── scraper/        # Collecte automatique des missions
│   ├── base.py     # Classe commune
│   ├── appen.py    # Scraper Appen Connect
│   └── remotasks.py # Scraper Remotasks
├── matcher/        # IA de matching (Claude)
│   └── engine.py
├── notifier/       # Alertes Telegram
│   └── telegram.py
├── api/            # Serveur Flask + base de données
│   ├── app.py
│   ├── models.py
│   └── routes.py
└── requirements.txt
```

## Déploiement Railway

1. Push sur GitHub (dépôt: amany-stores ou nouveau dépôt sam-ia)
2. Connecter Railway à ton GitHub
3. Ajouter les variables d'environnement dans Railway
4. Railway déploie automatiquement 🚀

## Développé par LOKONON Amany Auguste — Cotonou, Bénin 🇧🇯
