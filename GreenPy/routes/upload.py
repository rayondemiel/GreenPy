from flask import request, redirect, flash, url_for
import os
from werkzeug.utils import secure_filename
from flask_login import login_required

from ..app import app, statics
from ..modeles.donnees import Image, Objet_contest

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def autorisation_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_required
@app.route('/upload_image', methods=["Get", "POST"])
def upload_image():
    obj_id = request.form.get("objet_id")
    if 'file' not in request.files:
        flash("Impossible de télécharger l'image", "danger")
        return redirect(url_for('objContest', objContest_id=obj_id))
    file = request.files['file']
    if file.filename == '':
        flash("Aucun fichier sélectionné.", "danger")
        return redirect(url_for('objContest', objContest_id=obj_id))
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
            if statut is True:
                flash("Ajout d'une nouvelle image !", "success")
                return redirect(url_for('objContest', objContest_id=obj_id))
            else:
                flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
                os.remove(os.path.join(statics, app.config['UPLOAD_FOLDER'], filename))
                return redirect(request.url)
        else:
            flash("Les types d'images autorisés sont : png, jpg, jpeg")
            return redirect(url_for('objContest', objContest_id=obj_id))
