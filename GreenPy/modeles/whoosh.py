from whoosh.fields import SchemaClass, STORED, TEXT, DATETIME, ID, BOOLEAN, Schema
from whoosh.analysis import StemmingAnalyzer


class Search_Militant(SchemaClass):
    id = STORED
    nom = TEXT(stored=True)
    prenom = TEXT(stored=True)
    date_naissance = DATETIME(stored=True)
    date_deces = DATETIME(stored=True)
    profession = TEXT(stored=True)
    biographie = TEXT(stored=True)
    pays = ID(stored=True, sortable=True)


class Search_Lutte(SchemaClass):
    id = STORED
    intitule = TEXT(stored=True)
    categorie = ID(stored=True, sortable=True)
    description = TEXT(analyzer=StemmingAnalyzer(), stored=True)
    date_debut = DATETIME(stored=True)
    date_fin = DATETIME(stored=True)
    ville = TEXT(stored=True)
    dpt = TEXT(stored=True)
    pays = ID(stored=True, sortable=True)


class Search_Orga(SchemaClass):
    id = STORED
    intitule = TEXT(stored=True)
    date_fondation = DATETIME(stored=True)
    description = TEXT(analyzer=StemmingAnalyzer(), stored=True)
    pays = ID(stored=True, sortable=True)

class Search_Participer(SchemaClass):
    id = STORED
    acteur_id = ID(stored=True, sortable=True)
    contest_id = ID(stored=True, sortable=True)
    creation_instance = BOOLEAN(stored=True)
    participation_instance = BOOLEAN(stored=True)
    appel_instance_decision = BOOLEAN(stored=True)
    diffusion = BOOLEAN(stored=True)
    participation_decision = BOOLEAN(stored=True)
    rassemblement = BOOLEAN(stored=True)
    production = BOOLEAN(stored=True)
    illegalisme = BOOLEAN(stored=True)
    autre = BOOLEAN(stored=True)

class Search_Militer(SchemaClass):
    militer_id = STORED
    acteur_id = ID(stored=True, sortable=True)
    orga_id =ID(stored=True, sortable=True)
    date_debut = DATETIME(stored=True)
    date_fin = DATETIME(stored=True)
    statut = TEXT(stored=True)
