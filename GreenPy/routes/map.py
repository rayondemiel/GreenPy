from flask import render_template, request, url_for
import folium
from folium.plugins import MarkerCluster, Search, Fullscreen
import pandas as pd

from ..modeles.donnees import Objet_contest, Acteur, Participation
from ..app import app
from ..constantes import RESULTATS_PAR_PAGES

@app.route("/carte_native")
def carte_native():
    """Route permettant de faire appel à la carte générée au sein d'une page html"""
    return render_template("partials/map.html")

@app.route("/carte")
def carte():
    """
    Route permettant de créer une map localisant l'ensemble des luttes environnementales recensées en prenant en compte
    les zones et donc regrouper les données. La carte est centrée automatiquement en fonction d'un dataframe de donnéess.
    Un certain nombre d'options ont été paramétrées.
    :return: html
    """
    #Requete Sql
    luttes = Objet_contest.query.all()
    #Generation dataframe pour localisation et zoom
    latitude = list(lutte.latitude for lutte in luttes)
    longitude = list(lutte.longitude for lutte in luttes)
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
    for lutte in luttes:
        nom = lutte.nom
        categ = lutte.categorie.nom
        url = request.url_root + url_for('resultat_carte', lutte_id=lutte.id)
        url_lutte = request.url_root + url_for('objContest', objContest_id=lutte.id)
        html = f"""<html> \
                    <h5><center>{lutte.nom}</a><center></h5> \
                    <p style="font-size: x-small"><a href="{url_lutte}" target="_blank">Cliquez-ici pour accéder</a></p> \
                    <ul> \
                        <span style="text-decoration: underline;">Données :</span> \
                        <li> Catégorie : {lutte.categorie.nom} </li> \
                        <li> Ville : {lutte.ville} </li> \
                        <li> Pays : {lutte.pays.nom} </li> \
                        <li> Voir les résultats associés : <a href="{url}" target="_blank">cliquez ici</a> \
                    </ul> \
                </html>"""
        iframe = folium.IFrame(html=html, width=300, height=120)
        popup = folium.Popup(iframe, max_width=650)
        folium.Marker([lutte.latitude, lutte.longitude], popup=popup, tooltip=categ + " : " + nom, name=categ + " : " + nom).add_to(marker_cluster)
    ##Options
    ###Ajout Maps
    folium.TileLayer("Stamen Terrain").add_to(map)
    folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community", name="World Imagery").add_to(map)
    folium.LayerControl().add_to(map)
    #Ajout fonction recherche
    Search(layer=marker_cluster, search_label="name", geom_type="Point", placeholder="Search", position="topleft", collapsed=True).add_to(
        map)
    ###Ajout fonction fullscreen
    Fullscreen(
        title="Fullscreen",
        title_cancel="Exit fullscreen",
        force_separate_button=True
    ).add_to(map)
    ##Save
    map.save("GreenPy/templates/partials/map.html")
    return render_template("pages/carte_globale.html", name="Carte globale des luttes environnementales")

@app.route("/carte/resultat_carte/<int:lutte_id>")
def resultat_carte(lutte_id):
    """
    Resultat de recherche à partir des tooltips de la carte indiquant les personnes recensées à une lutte
    environnementale selectionnée

    :param lutte_id: Selection d'une id au sein de la table Object_contest.
    :return: HTML, list des personnes ayant participées
    """
    page = request.args.get("page", 1)
    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    lutte = Participation.query\
        .join(Objet_contest, Participation.contest_id == Objet_contest.id)\
        .join(Acteur, Participation.acteur_id == Acteur.id)\
        .filter(Objet_contest.id == lutte_id)\
        .order_by(Acteur.nom).paginate(page=page, per_page=RESULTATS_PAR_PAGES)
    objet = Objet_contest.query.get(lutte_id)
    return render_template("pages/resultat_carte.html", lutte=lutte, objet=objet)