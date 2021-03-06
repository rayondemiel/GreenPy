from flask import render_template, request, redirect, flash, url_for
from sqlalchemy import or_, and_
from flask_login import login_user, current_user, logout_user, login_required
import folium
from folium.plugins import MarkerCluster, Search, Fullscreen
import pandas as pd
import numpy as np
import re, os
from datetime import datetime



#Whoosh
from whoosh import index, query
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.query import Term, And, Every
from ..modeles.whoosh import Search_Orga, Search_Lutte, Search_Militant

#App
from .email import inscription_mail
from ..app import app, login, db, statics
from ..modeles.donnees import Acteur, Objet_contest, Pays, Militer, Categorie, Participation, Orga, Image
from ..modeles.utilisateurs import User
from ..modeles.authorship import AuthorshipActeur, Authorship_Orga, Authorship_ObjetContest
from ..constantes import RESULTATS_PAR_PAGES, REGEX_ANNEE, REGEX_DATE



#Fonctions systèmes
def times_spent(date_debut, date_fin, detail=False):
    """
    Fonction de calcul du temps entre deux dates en années. Si date_fin
    :param date_debut: String
    :param date_fin: String or none
    :param detail: Booleen pour definir si le format est AAAA-MM-DD ou AAAA
    :return: Différence de temps
    """

    current_date = datetime.today()
    #Sans date de fin
    if date_fin is not None:
        #Format YYYY
        if not detail:
            date_fin = datetime.strptime(date_fin, "%Y")
            date_debut = datetime.strptime(date_debut, "%Y")
            date_spent = date_fin - date_debut
        #Format YYYY-MM-DD
        else:
            date_fin = datetime.strptime(date_fin, "%Y-%m-%d")
            date_debut = datetime.strptime(date_debut, "%Y-%m-%d")
            date_spent = date_fin - date_debut
            date_spent = date_spent.total_seconds()
            date_spent = divmod(date_spent, 31536000)[0]
            return "Décédé(e) à l'âge de " + str(date_spent) + " ans"
    else:
        if not detail:
            date_debut = datetime.strptime(date_debut, "%Y")
            date_spent = current_date - date_debut
            date_spent = date_spent.total_seconds()
            date_spent = divmod(date_spent, 31536000)[0]
            return "En cours : " + str(date_spent) + " ans"
        else:
            date_debut = datetime.strptime(date_debut, "%Y-%m-%d")
            date_spent = current_date - date_debut
    date_spent = date_spent.total_seconds()
    date_spent = divmod(date_spent, 31536000)[0]
    if date_spent < 1:
        date_spent = "Moins d'une année"
        return date_spent
    return str(date_spent) + " années"

#Accueil

@app.route("/")
@app.route("/accueil")
def accueil():
    """
    Page d'accueil de l'application contenant des informations sur un l'élément de la table Acteur et quelque données sur l'application elle-même.
    :return: Html templates
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
    """
    Page contenant un petit à propos
    :return: Html templates
    """
    return render_template("pages/apropos.html")

#Accès aux données

@app.route("/militant")
@app.route("/militant")
def index_militant():
    """
    Index avec système de pagination de l'ensemble des acteurs écologistes recensés.
    :return: HTML
    """
    #paramètres pagination
    page = request.args.get("page", 1)
    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    #Resultat sql avec pagination
    militants = Acteur.query.order_by(Acteur.nom).paginate(page=page, per_page=RESULTATS_PAR_PAGES)
    return render_template("pages/militant.html", name="Index des militants", militants=militants)

@app.route("/militant/<int:name_id>")
def militant(name_id):
    """
    Route individuelle donnant les informations attachées à la personne identifiée. La page recense les participations aux
    projets écologistes et à différentes organisations. Une carte leaflet généré par folium permet de visualiser l'ensemble
    des participations à des luttes environnementales selon la personne. Il y a aussi quelques métadonnées concernant
     la création ou la modification de l'élément.
    :param name_id: Int ID, attribut de la classe Acteur
    :return: HTML avec resultats de requetes SQL (table Acteur, Orga, Objet_contest, Participation et Militer), de la date
    et d'une carte.
    """
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
    #Date
    date_militant = times_spent(unique_militants.date_naissance, unique_militants.date_deces, detail=True)
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
                           participer=participer, liste_orga=liste_orga, contest=contest, date_militant=date_militant)

@app.route("/projet_contest")
def index_objContest():
    """
        Cette fonction permet de retourner un index des données présentes au sein de la table Objet_contest.
        :return: index HTML
        """
    #paramètre pagination
    page = request.args.get("page", 1)
    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    #SQL et pagination
    projets_contest = Objet_contest.query.order_by(Objet_contest.nom).paginate(page=page, per_page=RESULTATS_PAR_PAGES)
    return render_template("pages/objet_contest.html", name="Index des projets contestés", projets_contest=projets_contest)

@app.route("/projet_contest/<int:objContest_id>")
def objContest(objContest_id):
    """
    Route individuelle donnant les informations attachées à la lutte identifiée. Une carte leaflet généré par folium permet de visualiser l'ensemble
    des participations à des luttes environnementales selon la personne. Il y a aussi quelques métadonnées concernant
     la création ou la modification de l'élément.
    :param objContest_id: Int, id de l'élément sélectionné.
    :return: HTML avec resultats de requetes SQL (table Objet_contest, Authorship, Image), de la date
    et d'une carte.
    """
    # Requete SQL
    unique_contest = Objet_contest.query.get(objContest_id)
    createur = Authorship_ObjetContest.query.filter(
        and_(Authorship_ObjetContest.createur == "True",
             Authorship_ObjetContest.authorship_objet_id == objContest_id)).first()
    images = Image.query \
        .join(Objet_contest, Image.objet_id == Objet_contest.id) \
        .filter(Objet_contest.id == objContest_id) \
        .order_by(Image.nom) \
        .all()
    #Date
    date = times_spent(unique_contest.date_debut, unique_contest.date_fin)

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
    :return: index HTML templates
    """
    #paramètres pagination
    page = request.args.get("page", 1)
    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    #SQL et pagination
    organisations = Orga.query.order_by(Orga.nom).paginate(page=page, per_page=RESULTATS_PAR_PAGES)
    return render_template("pages/organisation.html", name="Index des organisations", organisations=organisations)

#Gestion des données
##Militants
@app.route("/inscription_militant", methods=["GET", "POST"])
@login_required
def inscription_militant():
    """
    Route d'ajout de données concernant la table Acteur à travers la méthode POST. Cette fonction renvoie les données à la méthode statique
    de la classe Acteur permettant d'ajouter les données.
    :return: Html templates
    """

    #Requetes SQL tables associés
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
        #Validation
        if statut is True:
            generate_index(classe=Acteur)
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
    """
    Route de modification de données contenues au sein de la classe Acteur à travers la méthode POST.
    :param name_id: Int, id du militant sélectionné
    :return: Html templates
    """

    #Selection SQL
    militant = Acteur.query.get_or_404(name_id)
    #Table associée SQL
    pays = Pays.query.all()

    erreurs = []
    updated = False

    #Condition de modifications
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

        if request.form.get("date_naissance") and not re.match(REGEX_DATE, request.form.get("date_naissance")):
            erreurs.append("Les dates doivent être sous le format AAAA ou AAAA-MM-DD et supérieur à 1800")
        if request.form.get("date_deces") and not re.match(REGEX_DATE, request.form.get("date_deces")):
            erreurs.append("Les dates doivent être sous le format AAAA ou AAAA-MM-DD et supérieur à 1800")
        if datetime.strptime(request.form.get("date_naissance"), "%Y-%m-%d") > datetime.strptime(request.form.get("date_deces"), "%Y-%m-%d"):
            erreurs.append("La date de naissance est supérieur à la date de décès")

        #Récupération des données
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
            #Ajoute à la base
            db.session.add(militant)
            db.session.add(AuthorshipActeur(acteur=militant, user=current_user))
            db.session.commit()
            generate_index(classe=Acteur)
            updated = True
        #Renvoie d'erreurs
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
    """
    Route d'ajout de données concernant la table Objet_contest à travers la méthode POST. Cette fonction renvoie les données à la méthode statique
    de la classe Objet_contest permettant d'ajouter les données.
    :return: Html templates
    """

    #SQL des tables associées
    pays = Pays.query.all()
    categorie = Categorie.query.all()

    # Ajout d'une d'une lutte
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
        #Validation
        if statut is True:
            generate_index(classe=Objet_contest)
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
    """
        Route de modification de données contenues au sein de la classe Objet_contest à travers la méthode POST.
        :param objContest_id: Int, id de la lutte sélectionné
        :return: Html templates
        """

    #Selection SQL
    lutte = Objet_contest.query.get_or_404(objContest_id)
    #SQL tables associées
    pays = Pays.query.all()
    categorie = Categorie.query.all()

    erreurs = []
    updated = False

    #Conditions de modification
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

        if request.form.get("date_debut") and not re.match(REGEX_ANNEE, request.form.get("date_debut")):
            erreurs.append("Les dates doivent être sous le format AAAA")
        if request.form.get("date_fin") and not re.match(REGEX_ANNEE, request.form.get("date_fin")):
            erreurs.append("Les dates doivent être sous le format AAAA")
        if datetime.strptime(request.form.get("date_debut") , "%Y") > datetime.strptime(request.form.get("date_fin"), "%Y"):
            erreurs.append("La date de début est supérieure à la date de décès")

        #Recupération des données
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
            #Ajout des données
            db.session.add(lutte)
            db.session.add(Authorship_ObjetContest(objet_contest=lutte, user=current_user))
            db.session.commit()
            generate_index(classe=Objet_contest)
            updated = True
        #Renvoie d'erreurs
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

    #SQL table associée
    pays = Pays.query.all()

    # Ajout d'une organisation
    if request.method == "POST":
        statut, informations = Orga.ajout_orga(
            nom=request.form.get("nom", None),
            date_fondation=request.form.get("date_fondation", None),
            type_orga=request.form.get("type_orga", None),
            pays=Pays.query.get(request.form["pays"]),
            description=request.form.get("description", None)
        )
        #Validation
        if statut is True:
            generate_index(classe=Orga)
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
        Retourne vers la page avec les notifications de modification si l'ajout à fonctionner, sinon retourne vers la
        page. Les metadata de la modification sont enregistrés via Authorship_Orga.
        :param orga_id: Int, id de l'organisation sélectionné
        :return: HTML updated, ensemble des query de la table Pays
    """

    #SQL
    orga = Orga.query.get_or_404(orga_id)
    pays = Pays.query.all()

    erreurs = []
    updated = False

    #Condition de modifications
    if request.method == "POST":
        if not request.form.get("nom", "").strip():
            erreurs.append("Veuillez renseigner un intitulé.")
        if not request.form.get("pays", "").strip():
            erreurs.append("Veuillez renseigner le pays.")
        elif not Pays.query.get(request.form["pays"]):
            erreurs.append("Veuillez renseigner le pays.")
        if request.form.get("date_fondation") and not re.match(REGEX_ANNEE, request.form.get("date_fondation")):
            erreurs.append("Les dates doivent être sous le format AAAA et supérieur à 1800")
        #Récupération des données
        if not erreurs:
            print("Faire ma modifications")
            orga.nom = request.form["nom"]
            orga.date_fondation = request.form["date_fondation"]
            orga.type_orga = request.form["type_orga"]
            orga.description = request.form["description"]
            orga.pays = Pays.query.get(request.form["pays"])
            #Validation modification
            db.session.add(orga)
            db.session.add(Authorship_Orga(orga=orga, user=current_user))
            db.session.commit()
            updated = True
        else:
            generate_index(classe=Orga)
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
    """
     Route permettant d'ajouter des données dans la Table Militer dans le cadre d'un formulaire avec la méthode POST. Retourne vers l'acceuil
     si l'ajout à fonctionner, sinon retourne vers la page initiale.
     :return: HTML templates
     """
    #SQL selection
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
        #Validation
        if statut is True:
            generate_index(classe=Militer)
            flash("Ajout d'une nouvelle participation à une organisation", "success")
            return redirect(url_for('militant', name_id=name_id))
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return redirect(url_for('militant', name_id=name_id))

@login_required
@app.route("/militant/<int:militer_id>/update_militer", methods=["GET", "POST"])
def modification_militer(militer_id):
    """
        Route permettant de modifier des données dans la Table Militer dans le cadre d'un formulaire avec la méthode POST.
        Retourne vers la page avec les notifications de modification si l'ajout à fonctionner, sinon retourne vers la
        page. Les metadata de la modification sont enregistrés via Authorship_Orga.
        :param militer_id: Int, id de la lutte sélectionné
        :return: HTML updated, ensemble des query de la table Orga
    """
    #Selection SQL
    militer = Militer.query.get_or_404(militer_id)
    #Table associée
    liste_orga = Orga.query.all()

    erreurs = []
    updated = False
    #Conditions de modification
    if request.method == "POST":
        if not request.form.get("orga", "").strip():
            erreurs.append("Veuillez renseigner l'organisation.")
        elif not Orga.query.get(request.form["orga"]):
            erreurs.append("Veuillez renseigner l'organisation.")
        if request.form.get("date_debut") and not re.match(REGEX_ANNEE, request.form.get("date_debut")):
            erreurs.append("Les dates doivent être sous le format AAAA et supérieur à 1800")
        if request.form.get("date_fin") and not re.match(REGEX_ANNEE, request.form.get("date_fin")):
            erreurs.append("Les dates doivent être sous le format AAAA et supérieur à 1800")
        if datetime.strptime(request.form.get("date_debut") , "%Y") > datetime.strptime(request.form.get("date_fin"), "%Y"):
            erreurs.append("La date de début est supérieure à la date de décès")
        #Recupération des données
        if not erreurs:
            print("Faire ma modifications")
            militer.acteur_id = militer.acteur_id
            militer.orga = Orga.query.get(request.form["orga"])
            militer.date_debut = request.form.get("date_debut", None)
            militer.date_fin = request.form.get("date_fin", None)
            militer.statut = request.form.get("statut", None)
            #Validation
            db.session.add(militer)
            db.session.add(AuthorshipActeur(authorship_acteur_id=militer.acteur_id, user=current_user))
            db.session.commit()
            updated = True
        else:
            generate_index(classe=Militer)
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
    """
     Route permettant d'ajouter des données dans la Table Participation dans le cadre d'un formulaire avec la méthode POST. Retourne vers l'acceuil
     si l'ajout à fonctionner, sinon retourne vers la page initiale.
     :return: HTML templates, ensemble des query de la table Acteur et Objet_COntest
     """
    #Selection SQL
    name_id = request.form.get("acteur")
    # Ajout d'une participation
    if request.method == "POST":
        statut, informations = Participation.ajout_participation(
            contest_id=Objet_contest.query.get(request.form["objet_contest"]),
            acteur_id=Acteur.query.get(request.form["acteur"]),
            check=request.form.getlist("check")
        )
        #Validation
        if statut is True:
            generate_index(classe=Participation)
            flash("Ajout d'une nouvelle participation environnementale", "success")
            return redirect(url_for('militant', name_id=name_id))
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return redirect(url_for('militant', name_id=name_id))

@login_required
@app.route("/militant/<int:participer_id>/update_participer", methods=["GET", "POST"])
def modification_participer(participer_id):
    """
           Route permettant de modifier des données dans la Table Participation dans le cadre d'un formulaire avec la méthode POST.
           Retourne vers la page avec les notifications de modification si l'ajout à fonctionner, sinon retourne vers la
           page. Les metadata de la modification sont enregistrés via Authorship_Orga.
           :param participer_id: Int, id de la participation sélectionné
           :return: HTML updated, ensemble des query de la table Pays
       """

    #SQL selection
    participer = Participation.query.get_or_404(participer_id)
    #Tables associés
    contest = Objet_contest.query.all()

    erreurs = []
    updated = False

    #Condition de récupération
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
        #Validation des modifications
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
            generate_index(classe=Participation)
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
    """
    Ajout de données dans la table Pays depuis un modal et renvoie vers la page d'origine de cet ajout.
    :param page: Str, nom de la page d'origine
    :param obj_id: int, ID de la page d'origine
    :return: redirection vers la page d'origine ou l'acceuil en cas d'erreurs
    """

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
    """
    Fonction de suppression d'une données au sein d'une table et des tables associés.

    :param page: str, indique la page html de la donnée
    :param table: str, nom de la classe associée
    :param obj_id: int, id de l'objet devant être supprimé
    :return: redirect
    """

    #dict identifiant la classe
    liste_table = {
        "acteur": Acteur,
        "objet_contest": Objet_contest,
        "orga": Orga,
        "participation": Participation,
        "militer": Militer,
        "image": Image
    }
    #recuperation de la query
    suppr = liste_table[table].query.get(obj_id)
    if request.method:
        try:
            #Suppression pour données avec données associées
            if table == "acteur":
                for dep_parti in suppr.participation:
                    db.session.delete(dep_parti)
                for dep_milit in suppr.militer:
                    db.session.delete(dep_milit)
                for dep_author in suppr.authorships:
                    db.session.delete(dep_author)
                db.session.delete(suppr)
            if table == "orga":
                for dep_milit in suppr.militer:
                    db.session.delete(dep_milit)
                for dep_author in suppr.authorships:
                    db.session.delete(dep_author)
                db.session.delete(suppr)
            if table == "objet_contest":
                for dep_parti in suppr.participation:
                    db.session.delete(dep_parti)
                for dep_author in suppr.authorships:
                    db.session.delete(dep_author)
                if suppr.image:
                    os.remove(os.path.join(statics, "images/upload", suppr.image.filename))
                    db.session.delete(suppr.image.id)
                db.session.delete(suppr)
            #Suppression sans données asso
            else:
                db.session.delete(suppr)
            if page == "militant" and table != "acteur":
                #ajout trace de la modification
                db.session.add(AuthorshipActeur(authorship_acteur_id=suppr.acteur_id, user=current_user))
            if page == "projet_contest":
                if table == "image":
                    db.session.add(Authorship_ObjetContest(authorship_objet_id=suppr.objet.id, user=current_user))
            #maj
            db.session.commit()
            generate_index(classe=None)
            print("Suppression de l'entité réussie !:")
            flash("Suppression réussie", "success")
            return redirect("/")
        #Redirect selon la page d'origine
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
    resultatsObjet = []
    resultatsOrga = []
    resultats = None
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
             )).with_entities(Acteur.__name__, Acteur.id, Acteur.full.label("nom"))

        resultatsObjet = Objet_contest.query.filter(or_(
            Objet_contest.nom.like("%{}%".format(motclef)),
            Objet_contest.description.like("%{}%".format(motclef)),
            Objet_contest.ville.like("%{}%".format(motclef))
        )).with_entities(Objet_contest.__name__, Objet_contest.id, Objet_contest.nom.label("nom"))

        resultatsOrga = Orga.query.filter(or_(
            Orga.nom.like("%{}%".format(motclef)),
            Orga.description.like("%{}%".format(motclef))
        )).with_entities(Orga.__name__, Orga.id, Orga.nom.label("nom"))

        resultats = resultatsActeur.union(resultatsObjet, resultatsOrga) \
            .order_by(Acteur.full.asc()).paginate(page=page, per_page=RESULTATS_PAR_PAGES)

        titre = "Résultat pour la recherche `" + motclef + "`"
    return render_template("pages/recherche.html", resultats=resultats, titre=titre, keyword=motclef)

#Recherche whoosh non fonctionelle
"""
@app.route("/recherche")
def recherche():
    motclef = request.args.get("keyword", None)
    page = request.args.get("page", 1)
    titre = "Recherche"

    liste = ["identite", "profession", "intitulé", "description", "biographie", "ville", "pays"]

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    ix = index.open_dir(app.config["WHOOSH_SCHEMA_DIR"], schema=Search_Militant)
    q = QueryParser("profession", ix.schema).parse(motclef)
    with ix.searcher() as s:
        results = s.search_page(q, page, pagelen=RESULTATS_PAR_PAGES, terms=True)
        titre = "Résultat pour la recherche `" + motclef + "`"
    return render_template("pages/recherche.html", resultats=results, titre=titre, keyword=motclef)
"""

#Whoosh
@app.route("/generate_index")
def generate_index(classe=None):
    """
    Route permettant l'indexation whoosh grâce aux différentes statiques méthodes appelant des schémas particuliers.
    :param classe: Class, nom de la classe souhaitant être appelée
    :return: redirect
    """
    list_classe = [Acteur, Objet_contest, Orga, Militer, Participation]
    #generation totale de l'index
    if classe is None:
        i = 0
        for classe in list_classe:
           statut = classe.generate_index()
           if statut is True:
               i+=1
        #Si indexation de toutes les tables, validation
        if i == 4 :
            flash("Indexation faite", "info")
            return redirect('/')
        else:
            flash("Echec de l'indexation", "danger")
            return redirect('/')
    #generation index par schema
    else:
        statut = classe.generate_index()
        if statut is False:
            flash("Echec de l'indexation", "danger")
            return redirect('/')



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
        #Validation
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
    """
    Route de déconnexion
    :return:
    """
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté-e", "info")
    return redirect("/")
