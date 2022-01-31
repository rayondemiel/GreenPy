from flask import render_template


from .app import app
from .modeles.donnees import Acteur, Objet_contest

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