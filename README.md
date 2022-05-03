[![License: MIT](https://img.shields.io/badge/License-MIT--Licence-lightgrey.svg)](https://mit-license.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-red.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![made-with-python](https://img.shields.io/badge/Made%20with-python-1f425f.svg)](https://www.python.org/)

# GreenPy

Ce prototype d'application Flask vise à recenser et collecter les participations, les témoignages, les traces et les mémoires d'une écologie politique et sociale retrançant l'histoire des luttes environnementales, systémiques ou territoriales. L'application donne accès à une base de données participative et agrégative sur une histoire des mouvements de contestations écologique ou intersectionnelles, essentiellement tournées sur l'espace européen au XXe et XXIe siècle. Le projet se concencentre sur la coordination entre 3 axes structurant :

- Les individus : acteur et sujet de ces luttes environnementales. Le degré d'activité est relativement variable
- Les luttes environnementales : traces des participations et histoire des luttes
- Les organisations : structures de pensées et de regroupement des répertoires d'actions

Cette application a été conçue dans le cadre du cours 'Introduction au dévéloppement applicatif' dispensé par M. Thibault Clérice [@ponteineptique](https://github.com/PonteIneptique) à l'Ecole nationale des chartes - PSL.

---

## :gear: Installation

*Nota : commandes à exécuter dans le terminal (Linux ou macOS).*

  * Cloner le dossier : ```git clone https://github.com/Chartes-TNAH/Actes_Charles_Ier```
  
  * Installer l'environnement virtuel :
  
    * Vérifier que la version de Python est bien 3.x : ```python --version```;
    
    * Si vous ne possédez pas python, veuillez exécuter cette commande : ``` sudo apt-get install python3 python3-pip python3-virtualenv ```;
    
    * Aller dans le dossier : ```cd GreenPy```;
    
    * Installer l'environnement : ```python3 -m venv [nom de l'environnement]```.
  
  * Installer les packages et librairies :
  
    * Activer l'environnement : ```source [nom de l'environnement]/bin/activate```;
    
    * Installer les différentes librairies ```pip install -r requirements.txt```;
    
    * Installer les dépendances pour le NLP ```python -m nltk.downloader stopwords```;
    
    * Vérifier que tout est installé : ```pip freeze``` ;
    
    * Sortir de l'environnement : ```deactivate``` .

---

## :rocket: Lancement
  
  * Activer l'environnement : ```source [nom de l'environnement]/bin/activate``` ;
    
  * Lancement : ```python run.py``` ;
    
  * Aller sur ```http://127.0.0.1:5000/``` ;
    
  * Désactivation : ```ctrl + c``` ;
    
  * Sortir de l'environnement : ```deactivate```.
  
  Si vous souhaitez lancer les tests, vous pouvez executer cette commande : ```python3 -m unittest discover tests```
  
  ---
  
  ## Recommendations
  
  Certains variables d'environnement ne sont pas accessibles directement via ce dépôt. Il vous exporter une valeur ```SECRET_KEY```.
Le module mail nécessite la varaible ```G_KEY``` pour la configuration `MAIL_PASSWORD`. Vous pouvez configurer l'application avec `TESTING=TRUE` si vous ne possédez la valeur de la variable d'environnement.
