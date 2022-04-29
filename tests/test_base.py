from unittest import TestCase

from GreenPy.app import db, login, config_app, app
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
                      description="""La liaison ferroviaire transalpine Lyon - Turin est un projet de ligne de chemin de fer mixte voyageurs/fret à travers les Alpes, entre la France et l\'Italie. Comme les nouvelles lignes ferroviaires à travers les Alpes suisses, elle est destinée à la fois à accélérer les transports par trains de voyageurs et à transférer le trafic de fret de la route vers le rail. Le projet est très contesté en raison de son impact sur l’environnement et la géologie particulière des Alpes""",
                      date_debut='2012',
                      date_fin=None,
                      ville='Lyon',
                      dpt='Rhônes',
                      pays_id=1,
                      ressources=None,
                      latitude=45.7588,
                      longitude=4.8333
                  )
              ],
    orga = [
                Orga(
                    nom='CGT',
                    pays_id=1,
                    type_orga='Syndicat',
                    date_fondation='1895',
                    description="""La Confédération générale du travail, abrégé en CGT, est un syndicat français de salariés créé le 23 septembre 1895 à Limoges. Elle faisait partie des cinq confédérations de syndicats de salariés français considérées, par présomption irréfragable, comme représentatives par l'État avant la réforme de 2008. A son origine, la CGT fut l’aboutissement du syndicalisme révolutionnaire jusqu’au Congrès d’Amiens en 1906 ou se construit le syndicalisme paritaire Après la Seconde Guerre Mondiale, la CGT se rapprocha fortement du Parti Communiste Français. Toujours situé à gauche politiquement et soutenant un combat socialise, le syndicat s’est considérablement éloigné du PCF.""",
                ),
               Orga(
                   nom='NPA',
                   pays_id=1,
                   type_orga="Association",
                   date_fondation=None,
                   description="""Le Nouveau Parti anticapitaliste (NPA) est un parti politique français d'extrême gauche créé en février 2009 à l'issue d'un processus de fondation lancé par la Ligue communiste révolutionnaire (LCR) après l'élection présidentielle de 2007. """,
               ),
               Orga(
                   nom='Comité Malville',
                   pays_id=1,
                   type_orga='Association',
                   date_fondation='1975',
                   description=None,
               )
           ],
    participation = [
                Participation(
                    acteur_id=2,
                    contest_id=6,
                    creation_instance=0,
                    participation_instance=0,
                    appel_instance_decision=1,
                    diffusion=1,
                    participation_decision=0,
                    rassemblement=1,
                    production=0,
                    illegalisme=0,
                    autre=0
                ),
                Participation(
                    acteur_id=5,
                    contest_id=8,
                    creation_instance=0,
                    participation_instance=0,
                    appel_instance_decision=1,
                    diffusion=1,
                    participation_decision=1,
                    rassemblement=1,
                    production=0,
                    illegalisme=0,
                    autre=0
                ),
                Participation(
                    acteur_id=3,
                    contest_id=6,
                    creation_instance=0,
                    participation_instance=0,
                    appel_instance_decision=0,
                    diffusion=1,
                    participation_decision=0,
                    rassemblement=1,
                    production=0,
                    illegalisme=0,
                    autre=0
                ),
    ],
    image = [
                Image(
                    nom="""ZAD de Notre-Dame-des-Landes""",
                    legende='2018',
                    lien='ZAD2018.jpg',
                    objet_id=6,
                ),
                Image(
                    nom="""Manifestation Nantes""",
                    legende='novembre 2014',
                    lien='NantesZAD2014.jpg',
                    objet_id=6,
                ),
                Image(
                    nom="""Heurts à Plogoff""",
                    legende='La Gueule Ouverte, 1979',
                    lien='Nukleel_02-52139.jpg',
                    objet_id=1,
                )
    ],
    militer = [
                Militer(
                    acteur_id=1,
                    orga_id=1,
                    date_debut='1972',
                    date_fin='1973',
                    statut='Syndicaliste',
                ),
                Militer(
                    acteur_id=3,
                    orga_id=7,
                    date_debut='1978',
                    date_fin='1981',
                    statut=None,
                ),
                Militer(
                    acteur_id=6,
                    orga_id=12,
                    date_debut=None,
                    date_fin=None,
                    statut=None,
                )
    ]

    def setUp(self):
        self.app = config_app("test")
        self.db = db
        self.client = self.app.test_client()
        self.db.create_all(app=self.app)

    def tearDown(self):
        self.db.drop_all(app=self.app)

    def test_app_is_testing(self):
        """
        Verification si l'app est configuré en mode Test
        :return: True
        """
        self.assertTrue(app.config['TESTING'])

    def insert_all(self, personne=True, objet=True, orga=True, image=True, participation=True, militer=True):
        with self.app.app_context():
            if personne:
                for fixture in self.personne:
                    self.db.session.add(fixture)
            if objet:
                for fixture in self.objet:
                    self.db.session.add(fixture)
            if orga:
                for fixture in self.orga:
                    self.db.session.add(fixture)
            if image:
                for fixture in self.image:
                    self.db.session.add(fixture)
            if participation:
                for fixture in self.participation:
                    self.db.session.add(fixture)
            if militer:
                for fixture in self.militer:
                    self.db.session.add(fixture)
            self.db.session.commit()
