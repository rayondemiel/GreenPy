from ..app import db

class Acteur(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    nom = db.Column(db.Text, nullable=False)
    prenom = db.Column(db.Text, nullable=False)
    date_naissance = db.Column(db.Text, nullable=False)
    date_deces = db.Column(db.Text)
    ville_naissance = db.Column(db.Text, nullable=False)
    pays_naissance = db.Column(db.Integer, nullable=False)
    profession = db.Column(db.Text)
    biographie = db.Column(db.Text, nullable=False)

all_results_acteur = Acteur.query.all()

class Objet_contest(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    nom = db.Column(db.Text, nullable=False)
    categ_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_debut = db.Column(db.Text, nullable=False)
    date_fin = db.Column(db.Text)
    ville = db.Column(db.Text, nullable=False)
    dpt = db.Column(db.Text)
    pays_id = db.Column(db.Integer, nullable=False)
    ressources = db.Column(db.Text)
    img_id = db.Column(db.Integer)