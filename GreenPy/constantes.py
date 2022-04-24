from warnings import warn
import re

from config import Config

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

if Config.SECRET_KEY == "Pensez Printemps, les amis !!!":
    warn("Le secret par défaut n'a pas été changé, vous devriez le faire", Warning)