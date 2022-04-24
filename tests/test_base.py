from unittest import TestCase

from GreenPy.app import db, login, config_app
from GreenPy.modeles.utilisateurs import User
from GreenPy.modeles.donnees import *
from GreenPy.modeles.authorship import *

#voir tuto flask migrate

class Base(TestCase):
    personne = [
                   Acteur(
                       nom='Boris',
                       prenom='Boris',
                       date_naissance='12/03/1948',
                       date_deces='12/03/1948',
                       ville_naissance='Brest',
                       pays_naissance=1,
                       profession='Facteur',
                       biographie='syndicaliste CGT (1972-1973), CFDT (1973-1989) puis SUD-PTT (1989-2005) ; cofondateur et membre du conseil scientifique de l’association ATTAC (1998-2021) militant libertaire et écologiste engagé dans la lutte contre les pesticides et le soutien aux victimes.'
                    ),
                   Acteur(
                       nom='Pomme',
                       prenom='Louise',
                       date_naissance='02/06/1985',
                       date_deces='12/03/1948',
                       ville_naissance='Strasbourg',
                       pays_naissance=1,
                       profession='Journaliste',
                       biographie='Journaliste et documentaliste sur les thèmes de l’écologie politique et le développement durable. Elle est une militante active de Greenpeace promouvant une agriculture durable. Elle a participé à la construction de l’opposition des élus locaux et agriculteurs contre le projet d’un barrage hydroélectrique en Isère. Elle a participé à la mise en place d’un forum sur l’écologie lors des évènements du G8 à Gênes en 2008.'
                   ),
                   Acteur(
                       nom='Martin',
                       prenom='Georges',
                       date_naissance='1978-03-22',
                       date_deces=None,
                       ville_naissance='1978-03-22',
                       pays_naissance=5,
                       profession='Ouvrier du batiment',
                       biographie='Lutte contre un projet de barrage hydroélectrique sur la rivière du Doubs. '
                   )
                ],
    objet = [
                  Objet_contest(
                      nom='Projet de carrière de granit',
                      categ_id=3,
                      description=None,
                      date_debut='2004',
                      date_fin='2006',
                      ville='Luhan',
                      dpt='Morbihan',
                      pays_id=1,
                      ressources=None,
                      latitude=47.7104,
                      longitude=-2.6618
                  ),
                  Objet_contest(
                      nom='Protection des baleines en mer du Nord',
                      categ_id=4,
                      description=None,
                      date_debut='1985',
                      date_fin='1990',
                      ville='Le Havre',
                      dpt='Seine-Maritime',
                      pays_id=1,
                      ressources=None,
                      latitude=49.4951,
                      longitude=0.1195
                  ),
                  Objet_contest(
                      nom='Projet de ligne ferroviaire Lyon-Turin',
                      categ_id=5,
                      description='La liaison ferroviaire transalpine Lyon - Turin est un projet de ligne de chemin de fer mixte voyageurs/fret à travers les Alpes, entre la France et l\'Italie. Comme les nouvelles lignes ferroviaires à travers les Alpes suisses, elle est destinée à la fois à accélérer les transports par trains de voyageurs et à transférer le trafic de fret de la route vers le rail. Le projet est très contesté en raison de son impact sur l’environnement et la géologie particulière des Alpes',
                      date_debut='2012',
                      date_fin=None,
                      ville='Lyon',
                      dpt='Rhônes',
                      pays_id=1,
                      ressources=None,
                      latitude=45.7588,
                      longitude=4.8333
                  ),
              ],

    def setUp(self):
        self.app = config_app("test")
        self.db = db
        self.client = self.app.test_client()
        self.db.create_all(app=self.app)

    def tearDown(self):
        self.db.drop_all(app=self.app)