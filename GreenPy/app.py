from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import flask.ext.whooshalchemy as whooshalchemy

chemin_actuel = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(chemin_actuel, "templates")
statics = os.path.join(chemin_actuel, "static")

app = Flask("GreenPy",
    template_folder=templates,
    static_folder=statics)
# On configure la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/env.db'
# On initie l'extension
db = SQLAlchemy(app)

from .routes import accueil, militant, objContest, index_objContest, index_militant, recherche