from flask import render_template, request, redirect, flash, url_for
from sqlalchemy import or_, and_
from flask_login import login_user, current_user, logout_user, login_required
import folium
from folium.plugins import MarkerCluster, Search, Fullscreen
import pandas as pd
import numpy as np
import re, os

from .email import inscription_mail
from ..app import app, login, db, statics
from ..modeles.donnees import Acteur, Objet_contest, Pays, Militer, Categorie, Participation, Orga, Image
from ..modeles.utilisateurs import User
from ..modeles.authorship import AuthorshipActeur, Authorship_Orga, Authorship_ObjetContest
from ..constantes import RESULTATS_PAR_PAGES, REGEX_ANNEE, REGEX_DATE

#Accueil

@app.route("/")
@app.route("/accueil")
def accueil():
    """

    :return:
    """
    #Random item
    query_militant = Acteur.query.all()
    list_militant = list(militant.id for militant in query_militant)
    militants = np.asarray(list_militant)
    id_random = np.random.choice(militants)
    militant = Acteur.query.get_or_404(id_random)

    #Requete count sql
    militants_count = Acteur.query.count()
    projets_contest = Objet_contest.query.count()
    organisation = Orga.query.count()
    participation = Participation.query.count()
    return render_template("pages/accueil.html", name="accueil", militants=militants_count, projets_contest=projets_contest,
                           organisation=organisation, participation=participation, militant=militant)

@app.route("/a_propos")
def about():
    return render_template("pages/apropos.html")

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
    #Requete SQL
    unique_militants = Acteur.query.get(name_id)
    liste_orga = Orga.query.all()
    contest = Objet_contest.query.all()
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
        .order_by(Objet_contest.date_debut)\
        .all()
    createur = AuthorshipActeur.query.filter(and_(AuthorshipActeur.createur=="True", AuthorshipActeur.authorship_acteur_id==name_id)).first()
    # Generation dataframe pour localisation et zoom
    latitude = list(lutte.objet.latitude for lutte in participer)
    longitude = list(lutte.objet.longitude for lutte in participer)
    compte_participer = len(participer)
    if compte_participer >= 1:
        data = {
            "lat": latitude,
            "long": longitude
        }
        df = pd.DataFrame(data)
        sw = df[['lat', 'long']].min().values.tolist()
        ne = df[['lat', 'long']].max().values.tolist()
        #Cartographie
        ##Generation carte
        map = folium.Map(df[['lat', 'long']].mean().values.tolist())
        map.fit_bounds([sw, ne], max_zoom=12)
        ##Clustering
        marker_cluster = MarkerCluster(name='Luttes environnementales')
        map.add_child(marker_cluster)
        ##Marqueurs
        for participation in participer:
            nom = participation.objet.nom
            categ = participation.objet.categorie.nom
            url = request.url_root + url_for('resultat_carte', lutte_id=participation.objet.id)
            url_lutte = request.url_root + url_for('objContest', objContest_id=participation.objet.id)
            html = f"""<html> \
                            <h5><center>{participation.objet.nom}</a><center></h5> \
                            <p style="font-size: x-small"><a href="{url_lutte}" target="_blank">Cliquez-ici pour accéder</a></p> \
                            <ul> \
                                <span style="text-decoration: underline;">Données :</span> \
                                <li> Catégorie : {participation.objet.categorie.nom} </li> \
                                <li> Ville : {participation.objet.ville} </li> \
                                <li> Pays : {participation.objet.pays.nom} </li> \
                                <li> Voir les résultats associés : <a href="{url}" target="_blank">cliquez ici</a> \
                            </ul> \
                        </html>"""
            iframe = folium.IFrame(html=html, width=300, height=120)
            popup = folium.Popup(iframe, max_width=650)
            folium.Marker([participation.objet.latitude, participation.objet.longitude], popup=popup, tooltip=categ + " : " + nom, name=categ + " : " + nom).add_to(marker_cluster)
        ##Options
        ###Ajout Maps
        folium.TileLayer("Stamen Terrain").add_to(map)
        folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",name="World Imagery").add_to(map)
        folium.LayerControl().add_to(map)
        ### Ajout fonction recherche
        Search(layer=marker_cluster, search_label="name", geom_type="Point", placeholder="Search", position="topleft",
                collapsed=True).add_to(map)
        ###Ajout fonction fullscreen
        Fullscreen(
            title="Fullscreen",
            title_cancel="Exit fullscreen",
            force_separate_button=True
        ).add_to(map)
        ##Save
        map.save("GreenPy/templates/partials/map.html")
    return render_template("pages/militant.html", militant=unique_militants, createur=createur, organisation=organisation,
                           participer=participer, liste_orga=liste_orga, contest=contest)

@app.route("/projet_contest")
def index_objContest():
    """
        Cette fonction permet de retourner un index des données présentes au sein de la table Objet_contest.
        :return: index HTML
        """
    page = request.args.get("page", 1)
    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    #requete SQL
    projets_contest = Objet_contest.query.order_by(Objet_contest.nom).paginate(page=page, per_page=RESULTATS_PAR_PAGES)
    return render_template("pages/objet_contest.html", name="Index des projets contestés", projets_contest=projets_contest)

@app.route("/projet_contest/<int:objContest_id>")
def objContest(objContest_id):
    if Objet_contest.date_fin is not None :
        date = Objet_contest.date_fin-Objet_contest.date_debut
    else :
        date = "En cours"
    #Requete SQL
    unique_contest = Objet_contest.query.get(objContest_id)
    createur = Authorship_ObjetContest.query.filter(
        and_(Authorship_ObjetContest.createur == "True", Authorship_ObjetContest.authorship_objet_id == objContest_id)).first()
    images = Image.query \
        .join(Objet_contest, Image.objet_id == Objet_contest.id) \
        .filter(Objet_contest.id == objContest_id) \
        .order_by(Image.nom) \
        .all()
    #Cartographie
    map = folium.Map(location=[unique_contest.latitude, unique_contest.longitude], zoom_start=11)
    url = request.url_root + url_for('resultat_carte', lutte_id=unique_contest.id)
    html = f"""<html> \
                    <h5><center>{unique_contest.nom}</a><center></h5> \
                    <ul> \
                        <span style="text-decoration: underline;">Données :</span>
                        <li> Ville : {unique_contest.ville} </li> \
                        <li> Pays : {unique_contest.pays.nom} </li> \
                        <li> Voir les résultats associés : <a href="{url}" target="_blank">cliquez ici</a> \
                    </ul> \
                </html>"""
    iframe = folium.IFrame(html=html, width=300, height=120)
    popup = folium.Popup(iframe, max_width=650)
    folium.Marker([unique_contest.latitude, unique_contest.longitude], popup=popup).add_to(map)
    map.save("GreenPy/templates/partials/map.html")
    return render_template("pages/objet_contest.html", projet_contest=unique_contest, date=date, createur=createur, images=images)

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
    """
    Cette fonction permet de retourner un index des données présentes au sein de la table Organisation.
    :return: index HTML
    """
    page = request.args.get("page", 1)
    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    #Requete SQL
    organisations = Orga.query.order_by(Orga.nom).paginate(page=page, per_page=RESULTATS_PAR_PAGES)
    return render_template("pages/organisation.html", name="Index des organisations", organisations=organisations)

#Gestion des données
##Militants
@app.route("/inscription_militant", methods=["GET", "POST"])
@login_required
def inscription_militant():

    pays = Pays.query.all()
    contest = Objet_contest.query.all()

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
            return render_template("pages/update/ajout_militant.html")
    else:
        return render_template("pages/update/ajout_militant.html", pays=pays, contest=contest)

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

        if request.form.get("date_naissance"):
            if not re.match(REGEX_ANNEE, request.form.get("date_naissance")) or not re.match(REGEX_DATE, request.form.get("date_naissance")):
                erreurs.append("Les dates doivent être sous le format AAAA ou AAAA-MM-DD et supérieur à 1800")
        if request.form.get("date_deces"):
            if not re.match(REGEX_ANNEE, request.form.get("date_deces")) or not re.match(REGEX_DATE, request.form.get("date_deces")):
                erreurs.append("Les dates doivent être sous le format AAAA ou AAAA-MM-DD et supérieur à 1800")


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
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(erreurs), "danger")
            return redirect(url_for('modification_militant', name_id=name_id))
    return render_template(
        "pages/update/ajout_militant.html",
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
            return render_template("pages/update/ajout_lutte.html")
    else:
        return render_template("pages/update/ajout_lutte.html", pays=pays, categorie=categorie)

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
        if not request.form.get("latitude", "").strip():
            erreurs.append("Veuillez renseigner la latitude.")
        if not request.form.get("longitude", "").strip():
            erreurs.append("Veuillez renseigner la longitude.")

        if not request.form.get("pays", "").strip():
            erreurs.append("Veuillez renseigner le pays.")
        elif not Pays.query.get(request.form["pays"]):
            erreurs.append("Veuillez renseigner le pays.")
        if not request.form.get("categorie", "").strip():
            erreurs.append("Veuillez renseigner la catégorie.")
        elif not Pays.query.get(request.form["categorie"]):
            erreurs.append("Veuillez renseigner la catégorie.")

        if request.form.get("date_debut"):
            if not re.match(REGEX_ANNEE, request.form.get("date_debut")):
                erreurs.append("Les dates doivent être sous le format AAAA")
        if request.form.get("date_fin"):
            if not re.match(REGEX_ANNEE, request.form.get("date_fin")):
                erreurs.append("Les dates doivent être sous le format AAAA")


        if not erreurs:
            print("Faire ma modifications")
            lutte.nom = request.form["nom"]
            lutte.date_debut = request.form["date_debut"]
            lutte.date_fin = request.form["date_fin"]
            lutte.ville = request.form["ville"]
            lutte.dpt = request.form["departement"]
            lutte.description = request.form["description"]
            lutte.ressources = request.form["ressources"]
            lutte.latitude = request.form["latitude"]
            lutte.longitude = request.form["longitude"]
            lutte.categorie = Categorie.query.get(request.form["categorie"])
            lutte.pays = Pays.query.get(request.form["pays"])

            db.session.add(lutte)
            db.session.add(Authorship_ObjetContest(objet_contest=lutte, user=current_user))
            db.session.commit()
            updated = True
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(erreurs), "danger")
            return redirect(url_for('modification_lutte', objContest_id=objContest_id))
    return render_template(
        "pages/update/ajout_lutte.html",
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
    """
    Route permettant d'ajouter des données dans la Table Orga dans le cadre d'un formulaire avec la méthode POST. Retourne vers l'acceuil
    si l'ajout à fonctionner, sinon retourne vers la page initiale.
    :return: HTML update, ensemble des query de la table Pays
    """

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
            return render_template("pages/update/ajout_orga.html")
    else:
        return render_template("pages/update/ajout_orga.html", pays=pays)

@app.route("/organisation/<int:orga_id>/update", methods=["GET", "POST"])
@login_required
def modification_orga(orga_id):
    """
        Route permettant de modifier des données dans la Table Orga dans le cadre d'un formulaire avec la méthode POST.
        Retourne vers l'la page avec les notifications de modification si l'ajout à fonctionner, sinon retourne vers la
        page. Les metadata de la modification sont enregistrés via Authorship_Orga.
        :return: HTML updated, ensemble des query de la table Pays
    """

    #SQL
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
        if request.form.get("date_fondation"):
            if not re.match(REGEX_ANNEE, request.form.get("date_debut")):
                erreurs.append("Les dates doivent être sous le format AAAA et supérieur à 1800")

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
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(erreurs), "danger")
            return redirect(url_for('modification_orga', orga_id=orga_id))
    return render_template(
        "pages/update/ajout_orga.html",
        orga=orga,
        pays=pays,
        erreurs=erreurs,
        updated=updated)
#Gestion des données associés
##Militer

@login_required
@app.route("/ajout_militer", methods=["Get","POST"])
def militer():
    name_id = request.form.get("acteur")
    # Ajout d'une personne
    if request.method == "POST":
        statut, informations = Militer.ajout_militer(
            date_debut=request.form.get("date_debut", None),
            date_fin=request.form.get("date_fin", None),
            statut=request.form.get("statut", None),
            orga_id=Orga.query.get(request.form["orga"]),
            acteur_id=Acteur.query.get(request.form["acteur"])
        )

        if statut is True:
            flash("Ajout d'une nouvelle participation à une organisation", "success")
            return redirect(url_for('militant', name_id=name_id))
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return redirect(url_for('militant', name_id=name_id))

@login_required
@app.route("/militant/<int:militer_id>/update_militer", methods=["GET", "POST"])
def modification_militer(militer_id):

    militer = Militer.query.get_or_404(militer_id)
    liste_orga = Orga.query.all()

    erreurs = []
    updated = False

    if request.method == "POST":
        if not request.form.get("orga", "").strip():
            erreurs.append("Veuillez renseigner l'organisation.")
        elif not Orga.query.get(request.form["orga"]):
            erreurs.append("Veuillez renseigner l'organisation.")
        if request.form.get("date_debut"):
            if not re.match(REGEX_ANNEE, request.form.get("date_debut")):
                erreurs.append("Les dates doivent être sous le format AAAA et supérieur à 1800")
        if request.form.get("date_fin"):
            if not re.match(REGEX_ANNEE, request.form.get("date_fin")):
                erreurs.append("Les dates doivent être sous le format AAAA et supérieur à 1800")

        if not erreurs:
            print("Faire ma modifications")
            militer.acteur_id = militer.acteur_id
            militer.orga = Orga.query.get(request.form["orga"])
            militer.date_debut = request.form.get("date_debut", None)
            militer.date_fin = request.form.get("date_fin", None)
            militer.statut = request.form.get("statut", None)

            db.session.add(militer)
            db.session.add(AuthorshipActeur(authorship_acteur_id=militer.acteur_id, user=current_user))
            db.session.commit()
            updated = True
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(erreurs), "danger")
            return redirect(url_for('modification_militer', militer_id=militer_id))
    return render_template(
        "pages/update/modification_autres.html",
        liste_orga=liste_orga,
        militer=militer,
        erreurs=erreurs,
        updated=updated)

@login_required
@app.route("/ajout_participer", methods=["Get", "POST"])
def participer():
    name_id = request.form.get("acteur")
    # Ajout d'une personne
    if request.method == "POST":
        statut, informations = Participation.ajout_participation(
            contest_id=Objet_contest.query.get(request.form["objet_contest"]),
            acteur_id=Acteur.query.get(request.form["acteur"]),
            check=request.form.getlist("check")
        )

        if statut is True:
            flash("Ajout d'une nouvelle participation environnementale", "success")
            return redirect(url_for('militant', name_id=name_id))
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return redirect(url_for('militant', name_id=name_id))

@login_required
@app.route("/militant/<int:participer_id>/update_participer", methods=["GET", "POST"])
def modification_participer(participer_id):

    participer = Participation.query.get_or_404(participer_id)
    contest = Objet_contest.query.all()

    erreurs = []
    updated = False

    if request.method == "POST":
        if not request.form.get("objet_contest", "").strip():
            erreurs.append("Veuillez renseigner l'objet contesté.")
        elif not Orga.query.get(request.form["objet_contest"]):
            erreurs.append("Veuillez renseigner l'objet contesté.")

        # Fonction permettant de verifier l'existence dans la valeur au sein de la getlist des checkbox
        # Valeur de 1 si présente, 0 si absente
        check = request.form.getlist("check")
        repertoire = ["creation_instance", "participation_instance", "appel_instance_decision", "diffusion",
                      "participation_decision", "rassemblement", "production", "illegalisme", "autre"]
        list_check = {}
        for values in repertoire:
            if values in check:
                list_check[values] = 1
            else:
                list_check[values] = 0

        if not erreurs:
            print("Faire ma modifications")
            participer.acteur_id = participer.acteur_id
            participer.objet = Objet_contest.query.get(request.form["objet_contest"])
            participer.creation_instance = list_check["creation_instance"]
            participer.participation_instance = list_check["participation_instance"]
            participer.appel_instance_decision = list_check["appel_instance_decision"]
            participer.diffusion = list_check["diffusion"]
            participer.participation_decision = list_check["participation_decision"]
            participer.rassemblement = list_check["rassemblement"]
            participer.production = list_check["production"]
            participer.illegalisme = list_check["illegalisme"]
            participer.autre = list_check["autre"]

            db.session.add(participer)
            db.session.add(AuthorshipActeur(authorship_acteur_id=participer.acteur_id, user=current_user))
            db.session.commit()
            updated = True
    return render_template(
        "pages/update/modification_autres.html",
        contest=contest,
        participer=participer,
        erreurs=erreurs,
        updated=updated)

#Gestion des données
#Autres

@app.route("/<page>/pays", methods=["GET", "POST"])
@login_required
def ajout_pays(page, obj_id=None):

    # Ajout d'une personne
    if request.method == "POST":
        statut, informations = Pays.ajout_pays(
            nom=request.form.get("nom", None)
        )

        if statut is True:
            flash("Ajout d'un nouveau pays", "success")
            #Redirection en fonction de la page indiquée
            if page == "acteur":
                if obj_id is not None:
                    return redirect(url_for('modification_militant', name_id=obj_id))
                else:
                    return redirect("/inscription_militant")
            if page == "objet_contest":
                if obj_id is not None:
                    return redirect(url_for('modification_lutte', objContest_id=obj_id))
                else:
                    return redirect("/inscription_lutte")
            if page == "orga":
                if obj_id is not None:
                    return redirect(url_for('modification_orga', orga_id=obj_id))
                else:
                    return redirect("/inscription_orga")
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return redirect("/")

#Delete fonction

@app.route("/<page>/<int:obj_id>/<table>/delete")
@login_required
def delete(page, table, obj_id):

    liste_table = {
        "acteur": Acteur,
        "objet_contest": Objet_contest,
        "orga": Orga,
        "participation": Participation,
        "militer": Militer,
        "image": Image
    }

    suppr = liste_table[table].query.get(obj_id)

    if request.method:
        try:
            if table is Acteur:
                print(suppr.participation)
                for dep_parti in suppr.participation:
                    db.session.delete(dep_parti)
                for dep_milit in suppr.militer:
                    db.session.delete(dep_milit)
                    print(dep_milit)
                for dep_author in suppr.authorships:
                    print(dep_author)
                    db.session.delete(dep_author)
                db.session.delete(suppr)
            if table is Orga:
                for dep_milit in suppr.militer:
                    db.session.delete(dep_milit)
                for dep_author in suppr.authorships:
                    db.session.delete(dep_author)
                db.session.delete(suppr)
            if table is Objet_contest:
                for dep_parti in suppr.participation:
                    db.session.delete(dep_parti)
                for dep_author in suppr.authorships:
                    db.session.delete(dep_author)
                if suppr.image:
                    os.remove(os.path.join(statics, "images/upload", suppr.image.filename))
                    db.session.delete(suppr.image.id)
                db.session.delete(suppr)
            else:
                db.session.delete(suppr)
            if page == "militant" and table != "acteur":
                db.session.add(AuthorshipActeur(authorship_acteur_id=suppr.acteur_id, user=current_user))
            if page == "projet_contest":
                if liste_table[table] is Image:
                    db.session.add(Authorship_ObjetContest(authorship_acteur_id=suppr.objet_id, user=current_user))
                else:
                    db.session.add(Authorship_ObjetContest(authorship_acteur_id=suppr.contest_id, user=current_user))
            db.session.commit()
            flash("Suppression réussie", "success")
            return redirect("/")
        except Exception as erreur:
            db.session.rollback()
            flash("La suppression a échoué pour les raisons suivantes : " + str(erreur), "warning")
            if page == "militant":
                return redirect(url_for('militant', name_id=obj_id))
            if page == "organisation":
                return redirect(url_for('organisation', orga_id=obj_id))
            if page == "projet_contest":
                return redirect(url_for('objContest', objContest_id=obj_id))

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
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "danger")
            return render_template("pages/user/inscription.html")
    else:
        return render_template("pages/user/inscription.html")

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
            flash("Les identifiants n'ont pas été reconnus", "warning")

    return render_template("pages/user/connexion.html")

login.login_view = 'connexion'

@app.route("/deconnexion", methods=["POST", "GET"])
def deconnexion():
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté-e", "info")
    return redirect("/")