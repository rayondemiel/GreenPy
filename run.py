from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask("GreenPY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/env.db'
db = SQLAlchemy(app)

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

@app.route("/")
@app.route("/accueil")
def accueil():
    militants = Acteur.query.all()
    projets_contest = Objet_contest.query.all()
    return render_template("pages/accueil.html", name="accueil", militants=militants, projets_contest=projets_contest)

@app.route("/militant/<int:name_id>")
def militant(name_id):
    unique_militants = Acteur.query.get(name_id)
    #def age()
    return render_template("pages/militant.html", name="militant", militant=unique_militants)

@app.route("/projet_contest/<int:objContest_id>")
def objContest(objContest_id):
    unique_contest = Objet_contest.query.get(objContest_id)
    return render_template("pages/objet_contest.html", name="objet_contest", projet_contest=unique_contest)

if __name__ == "__main__":
    app.run(debug=True)
