
Concernant le projet python, j'ai contacté mon ancien directeur de mémoire, Alexis Vrignon qui s'intéresse au potentiel des humanités numériques pour ses recherches sur l'écologie politique et les enjeux énergétiques. Dans le cadre de la mise en place d'un prototype très primaire, l'idée est venue de mettre en place un site participatif sur la participation aux projets et luttes environnementales locales. La volonté du site est que ces anciens acteurs puissent écrire leur témoignage et leur vie militante sur ce site de collecte. L'intérêt est donc de rendre accessible une collecte de sources souvent invisibles dans les sources manuscrites. Techniquement le projet s'appuie donc sur trois volets :

- Bases de données avec articulation avec deux grandes entités acteurs (nom, prénom, date de naissance, date de décès, sexe, profession, adresse (ville),organisation ou association, description bibliographique ou sur certains évènements particuliers) et les luttes/projets (lieu, objet de contestation, dates de début et de fins de la contestation, descriptions, liens bibliographiques). La navigation s'appuie sur une recherche simple ou complexe ainsi que par filtre (ex: thématique -> nucléaire, barrage hydroélectrique; pays -> France, Allemagne etc.)
- Mise en place d'une cartographie dynamique sur 3 niveaux : une se situant sur la page de la personne une carte indique les lieux de participations (avec infobulles et hyperlien) / une carte situant les projets contestés recensés par cette collecte / sur la page d'un évènement particulier, une carte indiquant la situation des militants recensés participant et renvoyant vers leur page.
-Un formulaire permettant l'ajout des témoignages avec validation de l'administrateur (pour des raisons de sécurité et de cohérence de l'information), possibilité d'ajouter des photos ou autres informations. Système de validation juridique de l'utilisation des données.

Pour des raisons de RGPD, les informations personnelles seront fictives.




--------------------------------------------------------------------------------------------------------------------

structuration appli ( recommendation chap 8,1)

			→ modeles de données
			→ les routes
			→ création de l’application

The Flask Mega-Tutorial Part III: Web Forms→ site avec plein d’options d’amelioration de site


---

*question*

Est-ce que je constitue une liste de pays ? Zet leurs départements ? → car peut etre un proble pour la géolocaisation ensuite ou alors corriger les données. Car ces codes peuvent etre noramlisés


Faire un genre de citation de témoignage → genre extrait sur la page de lutte


rep action https://123dok.net/article/r%C3%A9pertoire-de-l-action-collective-typologie-repertoireactioncollective.eqowe4jy
---


idee bio 

https://maitron.fr/spip.php?article243660

https://maitron.fr/spip.php?article153734

https://maitron.fr/spip.php?article155122



---
# Problème a regler

-> modal militer (def militer) dans template militant -> bug clé

-> def suppression -> prob avec les jointures associés

-> faire la jointure de participation avec les booleens

---

---
## Gestion photos

https://roytuts.com/upload-and-display-image-using-python-flask/
https://github.com/roytuts/flask/tree/master/python-flask-upload-display-image
https://getbootstrap.com/docs/4.0/components/forms/#file-browser

https://stackoverflow.com/questions/44861182/how-to-render-image-from-flask-sqlalchemy-on-page

https://flask-appbuilder.readthedocs.io/en/latest/quickfiles.html

https://stackoverflow.com/questions/63507504/python-flask-app-upload-image-and-display

https://www.youtube.com/watch?v=pPSZpCVRbvQ

https://pythonhosted.org/Flask-Uploads/ -> voir les tests

## pdf

https://pypi.org/project/pdfkit/
https://stackoverflow.com/questions/28165704/convert-html-to-pdf-using-python-flask

https://stackoverflow.com/questions/51206880/how-to-use-python-pdfkit-with-python-flask-webapp


#scrollspy -> idee pour menu militant

https://www.w3schools.com/bootstrap/bootstrap_scrollspy.asp

#Ajouter dynamiquement
https://getbootstrap.com/docs/5.1/components/modal/

https://getbootstrap.com/docs/5.1/components/close-button/

# valeur bouton
https://python.tutorialink.com/get-the-value-of-a-checkbox-in-flask/


https://docs.sqlalchemy.org/en/14/core/type_basics.html#sqlalchemy.types.Boolean

https://stackoverflow.com/questions/38226607/python-flask-sqlalchemy-query-filter-by-boolean-values-ignore-false
https://stackoverflow.com/questions/12045698/sqlalchemy-boolean-value-is-none
https://stackoverflow.com/questions/20941539/how-to-get-if-checkbox-is-checked-on-flask?noredirect=1&lq=1
https://stackoverflow.com/questions/44600601/get-a-list-of-values-from-checkboxes-using-flask-through-python

#Multi forms

essayer de passer pra la jointure -> dans le form -> faire Acteur.militer.nom ect, ca peut peut marcher ?


https://stackoverflow.com/questions/52007908/flask-multiple-submit-button
https://www.codeproject.com/Questions/5313251/Parametrizing-routes-in-flask-by-multiple-submit-b


https://stackoverflow.com/questions/12502646/access-multiselect-form-field-in-flask -> recuperer plusieurs requetes





## Icons
https://www.w3schools.com/Css/css_icons.asp


## Adminsitrateur (osef)

https://www.youtube.com/watch?v=ysdShEL1HMM


#Recherche a facette et multi class

https://stackoverflow.com/questions/64243594/sqlalchemy-query-based-on-2-other-classes-tables-with-association-table

librairie woosh

https://whoosh.reathedocs.io/en/latest/searching.html#the-searcher-object
https://pythonhosted.org/Flask-WhooshAlchemy/

https://stackoverflow.com/questions/24204118/flask-request-form-getlist-wont-return-any-entries


##geo json (inutile)

https://github.com/gabays/32M7129 -voir cours 10 à 12**

---

## search plugins (done)
https://python-visualization.github.io/folium/plugins.html
https://github.com/python-visualization/folium/issues/464

## Map tuto (done)


ex: **https://github.com/jeandamien-genero/actes-bourbon**


Ca peut etre bien de faire geopy en asynchrone -> pas de changement de page, script qui se lance en silence je crois

https://programminghistorian.org/en/lessons/mapping-with-python-leaflet#transforming-data-with-python


https://github.com/flask-extensions/Flask-GoogleMaps

https://python-visualization.github.io/folium/quickstart.html

https://towardsdatascience.com/making-simple-maps-with-folium-and-geopy-4b9e8ab98c00  ->** lien entre geopy et folium**

https://towardsdatascience.com/represent-your-geospatial-data-using-folium-c2a0d8c35c5c    idem


https://developer.here.com/blog/understanding-geocoding-with-python

https://geopy.readthedocs.io/en/stable/

https://www.developer.here.com/blog/an-introduction-to-geojson

voir chap 13 API python
geoJSON
---
##style side bar
https://github.com/maelfabien/AutoHome/blob/master/app.py


plein idees
https://www.w3schools.com/howto/howto_css_stacked_form.asp
---
##Medadonnées 

voir systeme POSH dans métadonnées  (voir cours SQPARQL et web semantique)



---
##AUtres

https://atomiks.github.io/tippyjs/   -> pour tooltip javascript

https://github.com/MarkHjorth/nedry

## test

https://openclassrooms.com/fr/courses/4425066-concevez-un-site-avec-flask/4526533-testez-le-parcours-utilisateur-avec-les-tests-fonctionnels