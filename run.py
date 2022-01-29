from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask("GreenPY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data.db'
db = SQLAlchemy(app)

class Acteur(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    nom = db.Column(db.Text, nullable=False)
    prenom = db.Column(db.Text, nullable=False)
    date_naissance = db.Column(db.string(4), nullable=False)
    date_deces = db.Column(db.string(4))
    ville_naissance = db.Column(db.Text, nullable=False)
    pays_naissance = db.Column(db.Integer, nullable=False)
    profession = db.Column(db.string(45))
    biographie = db.Column(db.Text, nullable=False)

@app.route("/")
@app.route("/accueil")
def accueil():
    return render_template("pages/accueil.html", name="accueil", militants=militants, projets_contest=projets_contest)

@app.route("/militant/<int:name_id>")
def militant(name_id):
    return render_template("pages/militant.html", name="militant", militant=militants[name_id])

@app.route("/projet_contest/<int:objContest_id>")
def objContest(objContest_id):
    return render_template("pages/objet_contest.html", name="objet_contest", projet_contest=projets_contest[objContest_id])

if __name__ == "__main__":
    app.run(debug=True)
