import os
from dotenv import load_dotenv

from app import chemin_actuel

#Initialisation secret .env
load_dotenv()

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
    # Whoosh
    WHOOSH_SCHEMA_DIR = os.path.join(chemin_actuel, "data/index", "whoosh")
    if not os.path.exists(WHOOSH_SCHEMA_DIR):
        os.makedirs(WHOOSH_SCHEMA_DIR, exist_ok=True)

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