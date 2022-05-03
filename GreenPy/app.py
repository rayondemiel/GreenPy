from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os

from .settings import CONFIG, chemin_actuel

#appel module
db = SQLAlchemy()
login = LoginManager()
mail = Mail()
#Path
templates = os.path.join(chemin_actuel, "templates")
statics = os.path.join(chemin_actuel, "static")

#Instanciation Application
app = Flask("GreenPy",
    template_folder=templates,
    static_folder=statics)

from .routes import routes, email, map, upload

def config_app(config_name="test"):
    # Init config
    app.config.from_object(CONFIG[config_name])
    # Initiation extensions
    db.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    return app