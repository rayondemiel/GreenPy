from warnings import warn

#Constantes des résultats de recherche
RESULTATS_PAR_PAGES = 10

#Autorisation format image
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

#Secret Key
SECRET_KEY = "Pensez Printemps, les amis !!!"

if SECRET_KEY == "Pensez Printemps, les amis !!!":
    warn("Le secret par défaut n'a pas été changé, vous devriez le faire", Warning)