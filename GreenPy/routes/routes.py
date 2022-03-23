from flask import render_template, request, redirect, flash, url_for
from sqlalchemy import or_, and_
from flask_login import login_user, current_user, logout_user, login_required

from .email import mdp_mail, inscription_mail
from ..app import app, login, db
from ..modeles.donnees import Acteur, Objet_contest, Pays, Militer, Categorie, Participation, Orga
from ..modeles.utilisateurs import User
from ..modeles.authorship import AuthorshipActeur, Authorship_Orga, Authorship_ObjetContest
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

@app.route("/militant")
@app.route("/militant")
def index_militant():
    page = request.args.get("page", 1)
    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    militants = Acteur.query.order_by(Acteur.nom).paginate(page=page, per_page=RESULTATS_PAR_PAGES)
    return render_template("pages/militant.html", name="Index des militants", militants=militants)

@app.route("/militant/<int:name_id>")
def militant(name_id):
    unique_militants = Acteur.query.get(name_id)
    createur = AuthorshipActeur.query.filter(and_(AuthorshipActeur.createur=="True", AuthorshipActeur.authorship_acteur_id==name_id)).first()
    organisation = Militer.query\
        .join(Orga, Militer.orga_id == Orga.id)\
        .join(Acteur, Militer.acteur_id == Acteur.id)\
        .filter(Acteur.id == name_id)\
        .order_by(Militer.date_debut)\
        .all()
    participer = Participation.query\
        .join(Objet_contest, Participation.contest_id == Objet_contest.id)\
        .join(Acteur, Participation.acteur_id == Acteur.id)\
        .filter(Acteur.id == name_id)\
        .order_by(Objet_contest.nom)\
        .all()
    #def pour que si il pas de id, aller page accueil des militants. Par contre
    #def age()
    return render_template("pages/militant.html", militant=unique_militants, createur=createur, organisation=organisation, participer=participer)

@app.route("/projet_contest")
def index_objContest():
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
    createur = Authorship_ObjetContest.query.filter(
        and_(Authorship_ObjetContest.createur == "True", Authorship_ObjetContest.authorship_objet_id == objContest_id)).first()
    if Objet_contest.date_fin is not None :
        date = Objet_contest.date_fin-Objet_contest.date_debut
    else :
        date = "En cours"
    return render_template("pages/objet_contest.html", projet_contest=unique_contest, date=date, createur=createur)

#Organisation

@app.route("/organisation/<int:orga_id>")
def organisation(orga_id):
    organisation = Orga.query.get(orga_id)
    createur = Authorship_Orga.query.filter(
        and_(Authorship_Orga.createur == "True",
             Authorship_Orga.authorship_orga_id == orga_id)).first()
    militants = Militer.query \
        .join(Orga, Militer.orga_id == Orga.id) \
        .join(Acteur, Militer.acteur_id == Acteur.id) \
        .filter(Orga.id == orga_id) \
        .order_by(Militer.date_debut) \
        .all()
    return render_template("pages/organisation.html", organisation=organisation, createur=createur, militants=militants)

@app.route("/organisation")
def index_organisation():
    page = request.args.get("page", 1)
    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    organisations = Orga.query.order_by(Orga.nom).paginate(page=page, per_page=RESULTATS_PAR_PAGES)
    return render_template("pages/organisation.html", name="Index des organisations", organisations=organisations)

#Gestion des données
##Militants
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

@app.route("/militant/<int:name_id>/update", methods=["GET", "POST"])
@login_required
def modification_militant(name_id):

    militant = Acteur.query.get_or_404(name_id)
    pays = Pays.query.all()

    erreurs = []
    updated = False

    if request.method == "POST":
        if not request.form.get("nom", "").strip():
            erreurs.append("Veuillez renseigner le nom de la personne.")
        if not request.form.get("prenom", "").strip():
            erreurs.append("Veuillez renseigner le prénom de la personne.")
        if not request.form.get("date_naissance", "").strip():
            erreurs.append("Veuillez renseigner la date de naissance de la personne.")
        if not request.form.get("ville_naissance", "").strip():
            erreurs.append("Veuillez renseigner la ville de naissance de la personne.")
        if not request.form.get("biographie", "").strip():
            erreurs.append("Veuillez renseigner la biographie de la personne.")

        if not request.form.get("pays_naissance", "").strip():
            erreurs.append("Veuillez renseigner le pays de naissance de la personne.")
        elif not Pays.query.get(request.form["pays_naissance"]):
            erreurs.append("Veuillez renseigner le pays de naissance de la personne.")


        if not erreurs:
            print("Faire ma modifications")
            militant.nom = request.form["nom"]
            militant.prenom = request.form["prenom"]
            militant.date_naissance = request.form["date_naissance"]
            militant.date_deces = request.form["date_deces"]
            militant.ville_naissance = request.form["ville_naissance"]
            militant.profession = request.form["profession"]
            militant.biographie = request.form["biographie"]
            militant.pays = Pays.query.get(request.form["pays_naissance"])

            db.session.add(militant)
            db.session.add(AuthorshipActeur(acteur=militant, user=current_user))
            db.session.commit()
            updated = True
    return render_template(
        "pages/ajout_militant.html",
        militant=militant,
        pays=pays,
        erreurs=erreurs,
        updated=updated
    )

#Gestion des données
##Luttes environnementales

@app.route("/inscription_lutte", methods=["GET", "POST"])
@login_required
def inscription_lutte():

    pays = Pays.query.all()
    categorie = Categorie.query.all()

    # Ajout d'une personne
    if request.method == "POST":
        statut, informations = Objet_contest.ajout_lutte(
            nom=request.form.get("nom", None),
            categorie=Categorie.query.get(request.form["categorie"]),
            date_debut=request.form.get("date_debut", None),
            date_fin=request.form.get("date_fin", None),
            ville=request.form.get("ville", None),
            dpt=request.form.get("departement", None),
            pays=Pays.query.get(request.form["pays"]),
            description=request.form.get("description", None),
            ressources=request.form.get("ressources", None)
        )

        if statut is True:
            flash("Ajout d'une nouvelle lutte environnementale", "success")
            return redirect("/")
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return render_template("pages/ajout_lutte.html")
    else:
        return render_template("pages/ajout_lutte.html", pays=pays, categorie=categorie)

@app.route("/projet_contest/<int:objContest_id>/update", methods=["GET", "POST"])
@login_required
def modification_lutte(objContest_id):

    lutte = Objet_contest.query.get_or_404(objContest_id)
    pays = Pays.query.all()
    categorie = Categorie.query.all()

    erreurs = []
    updated = False

    if request.method == "POST":
        if not request.form.get("nom", "").strip():
            erreurs.append("Veuillez renseigner un intitulé.")
        if not request.form.get("date_debut", "").strip():
            erreurs.append("Veuillez renseigner une date de début.")
        if not request.form.get("ville", "").strip():
            erreurs.append("Veuillez renseigner la ville.")

        if not request.form.get("pays", "").strip():
            erreurs.append("Veuillez renseigner le pays.")
        elif not Pays.query.get(request.form["pays"]):
            erreurs.append("Veuillez renseigner le pays.")
        if not request.form.get("categorie", "").strip():
            erreurs.append("Veuillez renseigner la categorie.")
        elif not Pays.query.get(request.form["categorie"]):
            erreurs.append("Veuillez renseigner la categorie.")


        if not erreurs:
            print("Faire ma modifications")
            lutte.nom = request.form["nom"]
            lutte.date_debut = request.form["date_debut"]
            lutte.date_fin = request.form["date_fin"]
            lutte.ville = request.form["ville"]
            lutte.dpt = request.form["departement"]
            lutte.description = request.form["description"]
            lutte.ressources = request.form["ressources"]
            lutte.categorie = Categorie.query.get(request.form["categorie"])
            lutte.pays = Pays.query.get(request.form["pays"])

            db.session.add(lutte)
            db.session.add(Authorship_ObjetContest(objet_contest=lutte, user=current_user))
            db.session.commit()
            updated = True
    return render_template(
        "pages/ajout_lutte.html",
        lutte=lutte,
        pays=pays,
        categorie=categorie,
        erreurs=erreurs,
        updated=updated)

#Gestion des données
##Organisations

@app.route("/inscription_orga", methods=["GET", "POST"])
@login_required
def inscription_orga():

    pays = Pays.query.all()

    # Ajout d'une personne
    if request.method == "POST":
        statut, informations = Orga.ajout_orga(
            nom=request.form.get("nom", None),
            date_fondation=request.form.get("date_fondation", None),
            type_orga=request.form.get("type_orga", None),
            pays=Pays.query.get(request.form["pays"]),
            description=request.form.get("description", None)
        )

        if statut is True:
            flash("Ajout d'une nouvelle organisation", "success")
            return redirect("/")
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return render_template("pages/ajout_orga.html")
    else:
        return render_template("pages/ajout_orga.html", pays=pays)

@app.route("/organisation/<int:orga_id>/update", methods=["GET", "POST"])
@login_required
def modification_orga(orga_id):

    orga = Orga.query.get_or_404(orga_id)
    pays = Pays.query.all()

    erreurs = []
    updated = False

    if request.method == "POST":
        if not request.form.get("nom", "").strip():
            erreurs.append("Veuillez renseigner un intitulé.")
        if not request.form.get("pays", "").strip():
            erreurs.append("Veuillez renseigner le pays.")
        elif not Pays.query.get(request.form["pays"]):
            erreurs.append("Veuillez renseigner le pays.")


        if not erreurs:
            print("Faire ma modifications")
            orga.nom = request.form["nom"]
            orga.date_fondation = request.form["date_fondation"]
            orga.type_orga = request.form["type_orga"]
            orga.description = request.form["description"]
            orga.pays = Pays.query.get(request.form["pays"])

            db.session.add(orga)
            db.session.add(Authorship_Orga(orga=orga, user=current_user))
            db.session.commit()
            updated = True
    return render_template(
        "pages/ajout_orga.html",
        orga=orga,
        pays=pays,
        erreurs=erreurs,
        updated=updated)

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