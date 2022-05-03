from whoosh.fields import SchemaClass, STORED, TEXT, DATETIME, ID, BOOLEAN
from whoosh.analysis import KeywordAnalyzer, StopFilter, LowercaseFilter, RegexTokenizer, StemFilter
from nltk.corpus import stopwords

#Analyseur personnalisé
french_analyser = RegexTokenizer() | LowercaseFilter() | StemFilter(lang="fr") | StopFilter(stoplist=frozenset(stopwords.words('french')))

class Search_Militant(SchemaClass):
    """
    Classe pour la table Acteur
    """
    id = STORED
    identite = ID(stored=True, sortable=True)
    date_naissance = DATETIME(stored=True)
    date_deces = DATETIME(stored=True)
    profession = TEXT(analyzer=KeywordAnalyzer(), stored=True)
    biographie = TEXT(analyzer=french_analyser, stored=True)
    pays = TEXT(stored=True)


class Search_Lutte(SchemaClass):
    """
    Classe pour la table Objet_contest
    """
    id = STORED
    intitule = ID(stored=True, sortable=True)
    categorie = ID(stored=True, sortable=True)
    description = TEXT(analyzer=french_analyser, stored=True)
    date_debut = DATETIME(stored=True)
    date_fin = DATETIME(stored=True)
    ville = TEXT(stored=True)
    dpt = TEXT(stored=True)
    pays = TEXT(stored=True)


class Search_Orga(SchemaClass):
    """
    Classe pour la table orga
    """
    id = STORED
    intitule = ID(stored=True, sortable=True)
    date_fondation = DATETIME(stored=True)
    description = TEXT(analyzer=french_analyser, stored=True)
    type_orga = TEXT(analyzer=KeywordAnalyzer(), stored=True)
    pays = TEXT(stored=True)

class Search_Participer(SchemaClass):
    """
    Classe pour la table participer
    """
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
    """
    Classe pour la table militer
    """
    militer_id = STORED
    acteur_id = ID(stored=True, sortable=True)
    orga_id = ID(stored=True, sortable=True)
    date_debut = DATETIME(stored=True)
    date_fin = DATETIME(stored=True)
    statut = TEXT(analyzer=KeywordAnalyzer(), stored=True)
