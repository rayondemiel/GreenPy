import os
from dotenv import load_dotenv

#Initialisation secret .env
load_dotenv()

class Config(object):
    """
    Configuration des paramètres basiques pour le fonctionnement de l'application.
    """
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    #image
    MAX_CONTENT_LENGTH = 24 * 1024 * 1024 # taille max 10mb

class TestingConfig(Config):
    """
    Configuration des paramètres pour le mode test avec la génération d'une bdd adaptée. TESTING permet d'indiquer aux
    différents modules que l'application est en mode test et donc de ne pas générer d'erreurs avec les paramètres basiques (ex: Server error).
    """
    # On configure la base de données
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/env_test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Testing
    TESTING = True

class ProductionConfig(Config):
    """
    Configuration des paramètres pour le fonctionnement de l'application pour l'experience utilisateur avec la génération
    de la base de données native et des paramètres de fonctionnalités pour la fonction mail.
    """
    # On configure la base de données
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/env.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #Configuration mail server
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = 'greenpy.project@gmail.com'
    MAIL_PASSWORD = os.getenv('G_KEY')


CONFIG = {
    "test": TestingConfig,
    "production": ProductionConfig
}