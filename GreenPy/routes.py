from flask import render_template, request
from sqlalchemy import and_, or_

from .app import app
from .modeles.donnees import Acteur, Objet_contest

@app.route("/")
@app.route("/accueil")
def accueil():
    militants = Acteur.query.all()
    projets_contest = Objet_contest.query.all()
    return render_template("pages/accueil.html", name="accueil", militants=militants, projets_contest=projets_contest)

@app.route("/militant")
def index_militant():
    militants = Acteur.query.all()
    return render_template("pages/militant.html", name="Index des militants", militants=militants)

@app.route("/militant/<int:name_id>")
def militant(name_id):
    unique_militants = Acteur.query.get(name_id)
    #def pour que si il pas de id, aller page accueil des militants. Par contre
    #def age()
    return render_template("pages/militant.html", name="militant", militant=unique_militants)

@app.route("/projet_contest")
def index_objContest():
    projets_contest = Objet_contest.query.all()
    return render_template("pages/objet_contest.html", name="Index des projets contestés", projets_contest=projets_contest)

@app.route("/projet_contest/<int:objContest_id>")
def objContest(objContest_id):
    unique_contest = Objet_contest.query.get(objContest_id)
    return render_template("pages/objet_contest.html", name="objet_contest", projet_contest=unique_contest)

@app.route("/recherche")
def recherche():
    motclef = request.args.get("keyword", None)
    resultats = []
    titre = "Recherche"
    ##ne marche que pour une classe, il faut faire une table d'autorité pour jointure
    if motclef:
        resultatsActeur = Acteur.query.filter(
            or_(
            Acteur.nom.like("%{}%".format(motclef)),
            Acteur.prenom.like("%{}%".format(motclef)),
            Acteur.biographie.like("%{}%".format(motclef))
        )
        ).all()
        """resultatsObj = Acteur.query.filter(
            Acteur.nom.like("%{}%".format(motclef))
        ).all()"""
        titre = "Résultat pour la recherche `" + motclef + "`"
    return render_template("pages/recherche.html", resultats=resultatsActeur, titre=titre)