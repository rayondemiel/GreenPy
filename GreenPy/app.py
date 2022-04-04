from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os

from .constantes import SECRET_KEY

chemin_actuel = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(chemin_actuel, "templates")
statics = os.path.join(chemin_actuel, "static")



app = Flask("GreenPy",
    template_folder=templates,
    static_folder=statics)
#Configuration SECRET KEY
app.config['SECRET_KEY'] = SECRET_KEY

#image
app.config['MAX_CONTENT_LENGTH'] = 24 * 1024 * 1024 # taille max 10mb

#Configuration BDD
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/env.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#Configuration serveur mail
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = 1
app.config['MAIL_USERNAME'] = 'greenpy.project@gmail.com'
app.config['MAIL_PASSWORD'] = '' #os.getenv['G_KEY']

#Initiation extensions
db = SQLAlchemy(app)
login = LoginManager(app)
mail = Mail(app)

from .routes import routes, email, map, upload