from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Utilisateur(db.Model):
    __tablename__ = "utilisateurs"
    id             = db.Column(db.Integer, primary_key=True)
    nom            = db.Column(db.String(100), nullable=False)
    email          = db.Column(db.String(150), unique=True, nullable=False)
    telegram_id    = db.Column(db.String(50))
    pays           = db.Column(db.String(80), default="Bénin")
    langues        = db.Column(db.String(200), default="Français")
    competences    = db.Column(db.Text, default="")
    disponibilite  = db.Column(db.Integer, default=20)
    niveau         = db.Column(db.String(50), default="Débutant")
    actif          = db.Column(db.Boolean, default=True)
    date_creation  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "email": self.email,
            "telegram_id": self.telegram_id,
            "pays": self.pays,
            "langues": [l.strip() for l in self.langues.split(",")],
            "competences": [c.strip() for c in self.competences.split(",") if c.strip()],
            "disponibilite": self.disponibilite,
            "niveau": self.niveau,
        }

class Mission(db.Model):
    __tablename__ = "missions"
    id             = db.Column(db.Integer, primary_key=True)
    titre          = db.Column(db.String(200), nullable=False)
    description    = db.Column(db.Text)
    lien           = db.Column(db.String(500))
    plateforme     = db.Column(db.String(100))
    remuneration   = db.Column(db.String(100))
    langue         = db.Column(db.String(100))
    categorie      = db.Column(db.String(100))
    date_scraping  = db.Column(db.DateTime, default=datetime.utcnow)
    active         = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "titre": self.titre,
            "description": self.description,
            "lien": self.lien,
            "plateforme": self.plateforme,
            "remuneration": self.remuneration,
            "langue": self.langue,
            "categorie": self.categorie,
        }
