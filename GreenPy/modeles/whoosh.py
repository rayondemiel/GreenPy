from whoosh.fields import SchemaClass, STORED, TEXT, DATETIME, ID, BOOLEAN
from whoosh.analysis import StemmingAnalyzer, analyzers
from whoosh.index import create_in
import os

from ..app import chemin_actuel
from .donnees import Acteur,Objet_contest,Participation,Militer, Orga

corpus = os.path.join(chemin_actuel, "data/index", "whoosh")

class Search_Militant(SchemaClass):
    id = STORED,
    nom = TEXT(stored=True),
    prenom = TEXT(stored=True),
    date_naissance = DATETIME(stored=True),
    date_deces = DATETIME(stored=True),
    description = TEXT(analyzer=StemmingAnalyzer(), stored=True),
    profession = TEXT(stored=True),
    biographie = TEXT(stored=True),
    pays = ID(stored=True, sortable=True)

    def generate_index(self):
        ix_acteur = create_in(corpus, self)
        writer = ix_acteur.writer()
        objets = Acteur.query.order_by(Acteur.id).all()
        for objet in objets:
            writer.add_document(
                id=objet.id,
                nom=objets.nom,
                prenom=objet.prenom,
                date_naissance=objet.date_naissance,
                date_deces=objet.date_deces,
                description=objet.description,
                profession=objet.profession,
                biographie=objet.biographie,
                pays=objet.pays
            )
        writer.commit()
        return True


class Search_Lutte(SchemaClass):
    id = STORED,
    intitule = TEXT(stored=True),
    categorie = ID(stored=True, sortable=True),
    description = TEXT(analyzer=StemmingAnalyzer(), stored=True),
    date_debut = DATETIME(stored=True),
    date_fin = DATETIME(stored=True),
    ville = TEXT(stored=True),
    dpt = TEXT(stored=True),
    pays = ID(stored=True, sortable=True)

    def generate_index(self):
        ix_lutte = create_in(corpus, self)
        writer = ix_lutte.writer()
        objets = Objet_contest.query.order_by(Objet_contest.id).all()
        for objet in objets:
            writer.add_document(
                id=objet.id,
                intitule=objets.nom,
                categorie=objet.categorie,
                description=objet.description,
                date_debut=objet.date_debut,
                date_fin=objet.date_fin,
                ville=objet.ville,
                dpt=objet.dpt,
                pays=objet.pays
            )
        writer.commit()
        return True

class Search_Orga(SchemaClass):
    id = STORED,
    intitule = TEXT(stored=True),
    date_fondation = DATETIME(stored=True),
    description = TEXT(analyzer=StemmingAnalyzer(), stored=True)
    def generate_index(self):
        ix_orga = create_in(corpus, self)
        writer = ix_orga.writer()
        objets = Orga.query.order_by(Orga.id).all()
        for objet in objets:
            writer.add_document(
                id=objet.id,
                intitule=objets.nom,
                date_fondation=objet.date_fondation,
                description=objet.description
            )
        writer.commit()
        return True

class Search_Participer(SchemaClass):
    id = STORED
    acteur_id = ID(stored=True, sortable=True)
    contest_id = ID(stored=True, sortable=True)
    creation_instance = BOOLEAN(stored=True),
    participation_instance = BOOLEAN(stored=True),
    appel_instance_decision = BOOLEAN(stored=True),
    diffusion = BOOLEAN(stored=True),
    participation_decision = BOOLEAN(stored=True),
    rassemblement = BOOLEAN(stored=True),
    production = BOOLEAN(stored=True),
    illegalisme = BOOLEAN(stored=True),
    autre = BOOLEAN(stored=True)

    def generate_index(self):
        ix_particip = create_in(corpus, self)
        writer = ix_particip.writer()
        objets = Participation.query.order_by(Participation.id).all()
        for objet in objets:
            writer.add_document(
                id=objet.participation_id,
                acteur_id=objets.acteur_id,
                contest_id=objet.contest_id,
                creation_instance=objet.creation_instance,
                participation_instance=objet.participation_instance,
                appel_instance_decision=objet.appel_instance_decision,
                diffusion=objet.diffusion,
                participation_decision=objet.participation_decision,
                rassemblement=objet.rassemblement,
                production=objet.production,
                illegalisme=objet.illegalisme,
                autre=objet.autre
            )
        writer.commit()
        return True

class Search_Militer(SchemaClass):
    militer_id = STORED
    acteur_id = ID(stored=True, sortable=True)
    orga_id =ID(stored=True, sortable=True)
    date_debut = DATETIME(stored=True)
    date_fin = DATETIME(stored=True)
    statut = TEXT(stored=True)

    def generate_index(self):
        ix_particip = create_in(corpus, self)
        writer = ix_particip.writer()
        objets = Militer.query.order_by(Militer.id).all()
        for objet in objets:
            writer.add_document(
                id=objet.participation_id,
                acteur_id=objets.acteur_id,
                orga_id=objet.orga_id,
                date_debut=objet.date_debut,
                date_fin=objet.date_fin,
                statut=objet.statut
            )
        writer.commit()
        return True
