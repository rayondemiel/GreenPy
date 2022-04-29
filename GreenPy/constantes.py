import os
from dotenv import load_dotenv
from warnings import warn
import re
#Initialisation secret .env
load_dotenv()

#Constantes des résultats de recherche
RESULTATS_PAR_PAGES = 10

#Autorisation format image
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

#Regex time
REGEX_ANNEE = re.compile(r"^(18|19|20)\d{2}$")
REGEX_DATE = re.compile(r"^(18|19|20)\d{2}-\d{2}-\d{2}$")
REGEX_MAJ = re.compile(r"[A-Z]+")
REGEX_NB = re.compile(r"\d+")
REGEX_CAR = re.compile(r"""[`~!@#$%^&*()_|+=?;:'".<>]+""")

class Config(object):
    TESTING = False
    #Clé
    SECRET_KEY = os.getenv('SECRET_KEY')
    # Configuration image
    MAX_CONTENT_LENGTH = 24 * 1024 * 1024  # taille max 10mb
    # Configuration email server
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = 'greenpy.project@gmail.com'
    MAIL_PASSWORD = os.getenv('G_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class _TEST(Config):
    """Configuration des paramètres pour le mode test avec la génération d'une bdd adaptée. TESTING permet d'indiquer aux
    différents modules que l'application est en mode test et donc de ne pas générer d'erreurs avec les paramètres basiques (ex: Server error)."""
    # On configure la base de données
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/env_test.db'
    # Testing
    TESTING = True

class _PRODUCTION(Config):
    """
    Configuration des paramètres pour le fonctionnement de l'application pour l'experience utilisateur avec la génération
    de la base de données native et des paramètres de fonctionnalités pour la fonction mail.
    """
    # On configure la base de données
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/env.db'
    DEBUG = True

CONFIG = {
        "test": _TEST,
        "production": _PRODUCTION
    }

if Config.SECRET_KEY == "Pensez Printemps, les amis !!!":
    warn("Le secret par défaut n'a pas été changé, vous devriez le faire", Warning)

