from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os

from config import config

chemin_actuel = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(chemin_actuel, "templates")
statics = os.path.join(chemin_actuel, "static")

app = Flask("GreenPy",
    template_folder=templates,
    static_folder=statics)
#Initiation extensions
db = SQLAlchemy(app)
login = LoginManager(app)
mail = Mail(app)


def config_app(config_name="test"):
    app.config.from_object(config[config_name])
    db.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    return app