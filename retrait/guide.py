METHODES = {
    "paypal_wise_momo": {
        "nom": "PayPal → Wise → Mobile Money",
        "delai": "3-5 jours", "frais_estimes": "3-5%", "minimum": "10 USD",
        "etapes": [
            {"num": 1, "titre": "Créer un compte PayPal",
             "detail": "paypal.com → Compte Personnel → Vérifie ton identité avec CNI."},
            {"num": 2, "titre": "Lier PayPal à Appen/Remotasks",
             "detail": "Paramètres paiement de la plateforme → entre ton email PayPal."},
            {"num": 3, "titre": "Créer un compte Wise",
             "detail": "wise.com → Créer compte → Reçois en USD, convertis en XOF."},
            {"num": 4, "titre": "Transférer PayPal → Wise",
             "detail": "PayPal : Envoyer → email Wise. Frais ~3%. Délai 1-3 jours."},
            {"num": 5, "titre": "Retirer Wise → Mobile Money",
             "detail": "Wise : Retrait → Numéro MTN ou Moov Bénin. Délai 24-48h."},
        ]
    },
    "usdt_binance": {
        "nom": "USDT → Binance P2P → Mobile Money",
        "delai": "24-48 heures", "frais_estimes": "1-2%", "minimum": "20 USD",
        "etapes": [
            {"num": 1, "titre": "Créer un compte Coinbase",
             "detail": "Coinbase app → Créer compte → Vérifie CNI ou passeport."},
            {"num": 2, "titre": "Créer un compte Binance",
             "detail": "binance.com → Créer compte → Vérifie identité → Active 2FA."},
            {"num": 3, "titre": "Transférer USDT vers Binance",
             "detail": "Binance : Wallet → Dépôt → Copie adresse USDT (TRC20). Délai ~30min."},
            {"num": 4, "titre": "Vendre via Binance P2P",
             "detail": "Binance P2P → Vendre → USDT → Cherche offres MTN/Moov Bénin (>95% rep)."},
            {"num": 5, "titre": "Recevoir sur Mobile Money",
             "detail": "IMPORTANT: Confirme dans Binance SEULEMENT après réception sur Mobile Money."},
        ]
    },
    "wave": {
        "nom": "Wise → Wave",
        "delai": "24 heures", "frais_estimes": "2-3%", "minimum": "5 USD",
        "etapes": [
            {"num": 1, "titre": "Avoir Wave actif",
             "detail": "App Wave → Inscription avec CNI. Disponible Bénin, CI, Sénégal, Mali."},
            {"num": 2, "titre": "Recevoir via Wise",
             "detail": "Wise → Envoyer → Bénin → Numéro Wave. Frais ~2%."},
            {"num": 3, "titre": "Retirer ou payer",
             "detail": "Retrait cash chez agent Wave, payer factures, recharger données."},
        ]
    }
}

def get_guide(methode):
    return METHODES.get(methode, {})

def get_methode_recommandee(revenus_mensuels_usd):
    if revenus_mensuels_usd < 50:
        return "paypal_wise_momo"
    elif revenus_mensuels_usd < 200:
        return "wave"
    return "usdt_binance"

def afficher_comparaison():
    return [{"methode": v["nom"], "delai": v["delai"], "frais": v["frais_estimes"],
             "minimum": v["minimum"], "cle": k} for k, v in METHODES.items()]
