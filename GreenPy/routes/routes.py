from flask import render_template, request, redirect, flash, url_for
from sqlalchemy import or_
from flask_login import login_user, current_user, logout_user, login_required

from .email import mdp_mail, inscription_mail
from ..app import app, login, db
from ..modeles.donnees import Acteur, Objet_contest, Pays, Militer, Categorie, Participation, Orga
from ..modeles.utilisateurs import User
from ..modeles.forms import ResetPasswordRequestForm, ResetPasswordForm
from ..constantes import RESULTATS_PAR_PAGES

#Accueil

@app.route("/")
@app.route("/accueil")
def accueil():
    militants = Acteur.query.all()
    projets_contest = Objet_contest.query.all()
    return render_template("pages/accueil.html", name="accueil", militants=militants, projets_contest=projets_contest)

#Accès aux données

@app.route("/militant/")
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

@app.route("/projet_contest/")
@app.route("/projet_contest")
def index_objContest():   #bug
    page = request.args.get("page", 1)
    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    projets_contest = Objet_contest.query.order_by(Objet_contest.nom).paginate(page=page, per_page=RESULTATS_PAR_PAGES)
    return render_template("pages/objet_contest.html", name="Index des projets contestés", projets_contest=projets_contest)

@app.route("/projet_contest/<int:objContest_id>")
def objContest(objContest_id):
    unique_contest = Objet_contest.query.get(objContest_id)
    return render_template("pages/objet_contest.html", name="objet_contest", projet_contest=unique_contest)

#Gestion des données

@app.route("/inscription_militant", methods=["GET", "POST"])
@login_required
def inscription_militant():

    pays = Pays.query.all()

    # Ajout d'une personne
    if request.method == "POST":
        statut, informations = Acteur.ajout_acteur(
            nom = request.form.get("nom", None),
            prenom = request.form.get("prenom", None),
            date_naissance= request.form.get("date_naissance", None),
            date_deces= request.form.get("date_deces", None),
            ville_naissance= request.form.get("ville_naissance", None),
            pays_naissance= Pays.query.get(request.form["pays_naissance"]),
            profession= request.form.get("profession", None),
            biographie= request.form.get("biographie", None)
        )

        if statut is True:
            flash("Ajout d'un nouveau militant", "success")
            return redirect("/")
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return render_template("pages/ajout_militant.html")
    else:
        return render_template("pages/ajout_militant.html", pays=pays)

#Recherche

@app.route("/recherche")
def recherche():
    motclef = request.args.get("keyword", None)
    page = request.args.get("page", 1)
    resultatsActeur = []
    titre = "Recherche"

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    if motclef:
        resultatsActeur = Acteur.query.filter(or_(
            Acteur.nom.like("%{}%".format(motclef)),
            Acteur.prenom.like("%{}%".format(motclef)),
            Acteur.biographie.like("%{}%".format(motclef)),
            Acteur.prenom.like("%{}%".format(motclef)),
            Acteur.profession.like("%{}%".format(motclef))
             )).paginate(page=page, per_page=RESULTATS_PAR_PAGES)
        titre = "Résultat pour la recherche `" + motclef + "`"
    return render_template("pages/recherche.html", resultats=resultatsActeur, titre=titre, keyword=motclef)

#Gestion des utilisateurs

@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    """ Route gérant les inscriptions
    """
    # Si on est en POST, cela veut dire que le formulaire a été envoyé
    if request.method == "POST":
        statut, donnees = User.creer(
            login=request.form.get("login", None),
            email=request.form.get("email", None),
            nom=request.form.get("nom", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if statut is True:
            if donnees:
                inscription_mail(donnees)
            flash("Enregistrement effectué. Identifiez-vous maintenant", "success")
            return redirect("/")
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/inscription.html")
    else:
        return render_template("pages/inscription.html")

@app.route("/connexion", methods=["POST", "GET"])
def connexion():
    """ Route gérant les connexions
    """
    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connecté-e", "info")
        return redirect("/")
    # Si on est en POST, cela veut dire que le formulaire a été envoyé
    if request.method == "POST":
        utilisateur = User.identification(
            login=request.form.get("login", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        print(utilisateur)
        if utilisateur:
            flash("Connexion effectuée", "success")
            login_user(utilisateur)
            return redirect("/")
        else:
            flash("Les identifiants n'ont pas été reconnus", "error")

    return render_template("pages/connexion.html")

login.login_view = 'connexion'

@app.route("/deconnexion", methods=["POST", "GET"])
def deconnexion():
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté-e", "info")
    return redirect("/")

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """
    Fonction permettant de vérifier que l'utilisateur est bien présent au sein de la base de données et d'initier la fonction mdp_mail()
    Si l'utilisateur est déjà identifier alors il redirigé vers l'accueil.
    :return: Html template
    """
    if current_user.is_authenticated:
        return redirect(url_for('/accueil'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.email.data).first()
        if user:
            mdp_mail(user)
        flash("Regardez votre boîte mail d'ici quelques instants")
        return redirect(url_for('connexion'))
    return render_template('pages/reset_password.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Fonction de reinitialisation du mot de passe de l'utilisateur à partir du formulaire de reinitialisation.
    Si l'utilisateur est déjà identifier ou n'est pas le même, alors il redirigé vers l'accueil.

    :param token: Retour de la variable de la fonction mdp_mail() ou rediction vers l'accueil
    :return: Template Html
    """
    if current_user.is_authenticated:
        return redirect(url_for('accueil'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('accueil'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Votre mot de passe a été changé')
        return redirect(url_for('connexion'))
    return render_template('pages/password_reponse.html', form=form)