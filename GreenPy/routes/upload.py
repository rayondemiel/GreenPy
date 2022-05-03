from flask import request, redirect, flash, url_for
import os
from werkzeug.utils import secure_filename
from flask_login import login_required

from ..app import app, statics
from ..modeles.donnees import Image, Objet_contest
from ..constantes import ALLOWED_EXTENSIONS

def autorisation_files(filename):
    """
    Fonction de limitation des fichiers autorisés
    :param filename: str, nom du fichier uploadé
    :return:
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_required
@app.route('/upload_image', methods=["Get", "POST"])
def upload_image():
    """
    Route de récupération de l'upload d'un ficbier au sein de l'application
    :return: redirection route objContest
    """
    #Récupération des données
    obj_id = request.form.get("objet_id")
    #Si pas de fichiers récupérés
    if 'file' not in request.files:
        flash("Impossible de télécharger l'image", "danger")
        return redirect(url_for('objContest', objContest_id=obj_id))
    #récupération fichier
    file = request.files['file']
    #Si fichier vide
    if file.filename == '':
        flash("Aucun fichier sélectionné.", "danger")
        return redirect(url_for('objContest', objContest_id=obj_id))
    #Si présence d'un fichier avec les bonnes extensions
    if file and autorisation_files(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(statics, "images/upload", filename))
        #Recuperation données
        if request.method == "POST":
            statut, informations = Image.ajout_image(
                nom=request.form.get("nom", None),
                legende=request.form.get("legende", None),
                lien=filename,
                objet_id=Objet_contest.query.get(request.form["objet_id"])
            )
            #Validation
            if statut is True:
                flash("Ajout d'une nouvelle image !", "success")
                return redirect(url_for('objContest', objContest_id=obj_id))
            #echec
            else:
                flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
                #Suppression du fichiers
                os.remove(os.path.join(statics, "images/upload", filename))
                return redirect(url_for('objContest', objContest_id=obj_id))
        else:
            flash("Les types d'images autorisés sont : png, jpg, jpeg")
            return redirect(url_for('objContest', objContest_id=obj_id))
