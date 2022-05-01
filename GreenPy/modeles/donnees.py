import geopy.exc
from flask_login import current_user
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut
import re

from ..app import db
from .authorship import AuthorshipActeur, Authorship_ObjetContest, Authorship_Orga
from ..constantes import REGEX_ANNEE, REGEX_DATE

geolocator = Nominatim(user_agent="GreenPy")

class Acteur(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    nom = db.Column(db.Text, nullable=False)
    prenom = db.Column(db.Text, nullable=False)
    date_naissance = db.Column(db.DateTime, nullable=False)
    date_deces = db.Column(db.DateTime)
    ville_naissance = db.Column(db.Text, nullable=False)
    pays_naissance = db.Column(db.Integer, db.ForeignKey('pays.id'))
    profession = db.Column(db.Text)
    biographie = db.Column(db.Text, nullable=False)
    #Relations
    authorships = db.relationship("AuthorshipActeur", back_populates="acteur")
    participation = db.relationship("Participation", back_populates="acteur")
    militer = db.relationship("Militer", back_populates="acteur")
    pays = db.relationship("Pays", back_populates="acteur")

    @staticmethod
    def ajout_acteur(nom, prenom, date_naissance, date_deces, ville_naissance, pays_naissance, profession, biographie):
        erreurs = []
        if not nom:
            erreurs.append("Veuillez renseigner le nom de la personne.")
        if not prenom:
            erreurs.append("Veuillez renseigner le prénom de la personne.")
        if not date_naissance:
            erreurs.append("Veuillez renseigner la date de naissance de la personne.")
        if not ville_naissance:
            erreurs.append("Veuillez renseigner la ville de naissance de la personne.")
        if not pays_naissance:
            erreurs.append("Veuillez renseigner le pays de naissance de la personne.")
        if not biographie:
            erreurs.append("Veuillez renseigner la biographie de la personne.")
        if date_naissance:
            if not re.match(REGEX_DATE, date_naissance):
                erreurs.append("Les dates doivent être sous le format AAAA-MM-DD et supérieur à 1800")
        if date_deces:
            if not re.match(REGEX_DATE, date_deces):
                erreurs.append("Les dates doivent être sous le format AAAA-MM-DD et supérieur à 1800")

        unique = Acteur.query.filter(db.and_(
            Acteur.nom == nom,
            Acteur.prenom == prenom,
            Acteur.date_naissance == date_naissance
            )).count()
        if unique > 0:
            erreurs.append("Cette personne est déjà présente au sein de la base de données.")

            # S'il y a au moins une erreur, afficher un message d'erreur.
        if len(erreurs) > 0:
            return False, erreurs

            # Si aucune erreur n'a été détectée, ajout d'une nouvelle entrée dans la table Acteur
        nouveau_acteur = Acteur(nom = nom,
                                prenom = prenom,
                                date_naissance = date_naissance,
                                date_deces = date_deces,
                                ville_naissance = ville_naissance,
                                profession = profession,
                                biographie = biographie,
                                pays=pays_naissance)

        try:
            db.session.add(nouveau_acteur)
            db.session.add(AuthorshipActeur(acteur=nouveau_acteur, user=current_user, createur="True"))
            db.session.commit()
            return True, nouveau_acteur

        except Exception as erreur:
            return False, [str(erreur)]

class Participation(db.Model):
    participation_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    acteur_id = db.Column(db.Integer, db.ForeignKey('acteur.id'))
    contest_id = db.Column(db.Integer, db.ForeignKey('objet_contest.id'))
    creation_instance = db.Column(db.Boolean, nullable=False, default=0)
    participation_instance = db.Column(db.Boolean, nullable=False, default=0)
    appel_instance_decision = db.Column(db.Boolean, nullable=False, default=0)
    diffusion = db.Column(db.Boolean, nullable=False, default=0)
    participation_decision = db.Column(db.Boolean, nullable=False, default=0)
    rassemblement = db.Column(db.Boolean, nullable=False, default=0)
    production = db.Column(db.Boolean, nullable=False, default=0)
    illegalisme = db.Column(db.Boolean, nullable=False, default=0)
    autre = db.Column(db.Boolean, nullable=False, default=0)
    #Relations
    acteur = db.relationship("Acteur", back_populates="participation")
    objet = db.relationship("Objet_contest", back_populates="participation")

    @staticmethod
    def ajout_participation(acteur_id, contest_id, check):
        erreurs = []
        if not acteur_id:
            erreurs.append("Veuillez renseigner la personne.")
        if not contest_id:
            erreurs.append("Veuillez renseigner l'objet contesté'")

        unique = Participation.query.filter(db.and_(
            Participation.acteur == acteur_id,
            Participation.objet == contest_id
        )).count()
        if unique > 0:
            erreurs.append("Cette participation est déjà présente au sein de la base de données.")

        if len(check) < 1:
            erreurs.append("Vous devez sélectionner au moins un élément")
            # S'il y a au moins une erreur, afficher un message d'erreur.
        if len(erreurs) > 0:
            return False, erreurs

        #Fonction permettant de verifier l'existence dans la valeur au sein de la getlist des checkbox
        #Valeur de 1 si présente, 0 si absente
        repertoire = ["creation_instance", "participation_instance", "appel_instance_decision", "diffusion",
                      "participation_decision", "rassemblement", "production", "illegalisme", "autre"]
        list_check = {}
        for values in repertoire:
            if values in check:
                list_check[values] = 1
            else:
                list_check[values] = 0
            # Si aucune erreur n'a été détectée, ajout d'une nouvelle entrée dans la table Participation
        nouvelle_participation = Participation(acteur=acteur_id,
                                               objet=contest_id,
                                               **list_check)

        try:
            db.session.add(nouvelle_participation)
            # Necessite user_id, sinon bug de current_user
            db.session.add(AuthorshipActeur(acteur=acteur_id, authorship_user_id=current_user.user_id))
            db.session.commit()
            return True, nouvelle_participation

        except Exception as erreur:
            return False, [str(erreur)]

class Objet_contest(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    nom = db.Column(db.Text, nullable=False)
    categ_id = db.Column(db.Integer, db.ForeignKey('categorie.id'))
    description = db.Column(db.Text)
    date_debut = db.Column(db.Text, nullable=False)
    date_fin = db.Column(db.Text)
    ville = db.Column(db.Text, nullable=False)
    dpt = db.Column(db.Text)
    pays_id = db.Column(db.Integer, db.ForeignKey('pays.id'))
    ressources = db.Column(db.Text)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    #Relations
    authorships = db.relationship("Authorship_ObjetContest", back_populates="objet_contest")
    participation = db.relationship("Participation", back_populates="objet")
    categorie = db.relationship("Categorie", back_populates="objet_contest")
    pays = db.relationship("Pays", back_populates="objet_contest")
    image = db.relationship("Image", back_populates="objet")

    @staticmethod
    def ajout_lutte(nom, categorie, date_debut, date_fin, ville, dpt, pays, description, ressources):
        erreurs = []
        if not nom:
            erreurs.append("Veuillez renseigner un intitulé.")
        if not categorie:
            erreurs.append("Veuillez renseigner une catégorie.")
        if not date_debut:
            erreurs.append("Veuillez renseigner une date de début.")
        if not ville:
            erreurs.append("Veuillez renseigner la ville.")
        if not pays:
            erreurs.append("Veuillez renseigner le pays.")
        if date_debut:
            if not re.match(REGEX_ANNEE, date_debut):
                erreurs.append("Les dates doivent être sous le format AAAA et supérieur à 1800")
        if date_fin:
            if not re.match(REGEX_ANNEE, date_fin):
                erreurs.append("Les dates doivent être sous le format AAAA et supérieur à 1800")

        unique = Objet_contest.query.filter(db.and_(
            Objet_contest.categorie == categorie,
            Objet_contest.date_debut == date_debut,
            Objet_contest.ville == ville
        )).count()
        if unique > 0:
            erreurs.append("Cette page est déjà présente au sein de la base de données.")

        #Géolocalisation automatique
        try:
            if dpt:
                location = geolocator.geocode("{ville}, {dpt}, {pays}".format(ville=ville, dpt=dpt, pays=pays.nom))
                if location is None:
                    erreurs.append("Le lieu n'a pas pu être géolocaliser. Veuillez préciser les données du formulaire.")
            else:
                location = geolocator.geocode("{ville}, {pays}".format(ville=ville, pays=pays.nom))
                if location is None:
                    erreurs.append("Le lieu n'a pas pu être géolocalisé. Veuillez préciser les données du formulaire.")
        except (GeocoderTimedOut, GeocoderUnavailable):
            erreurs.append("Les services API n'ont pu être activés. Veuillez verifier votre connexion réseau.")


            # S'il y a au moins une erreur, afficher un message d'erreur.
        if len(erreurs) > 0:
            return False, erreurs
        # Si aucune erreur n'a été détectée, ajout d'une nouvelle entrée dans la table Acteur
        nouvelle_lutte = Objet_contest(nom=nom,
                                       categorie=categorie,
                                       date_debut=date_debut,
                                       date_fin=date_fin,
                                       ville=ville,
                                       dpt=dpt,
                                       description=description,
                                       ressources=ressources,
                                       pays=pays,
                                       latitude=location.latitude,
                                       longitude=location.longitude)

        try:
            db.session.add(nouvelle_lutte)
            db.session.add(Authorship_ObjetContest(objet_contest=nouvelle_lutte, user=current_user, createur="True"))
            db.session.commit()
            return True, nouvelle_lutte

        except Exception as erreur:
            return False, [str(erreur)]

class Categorie(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    nom = db.Column(db.Text, nullable=False)
    #Relations
    objet_contest = db.relationship("Objet_contest", back_populates="categorie")

class Orga(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    nom = db.Column(db.Text, nullable=False)
    pays_id = db.Column(db.Integer, db.ForeignKey('pays.id'))
    type_orga = db.Column(db.Text)
    date_fondation = db.Column(db.Text)
    description = db.Column(db.Text)
    #Relations
    militer = db.relationship("Militer", back_populates="orga")
    pays = db.relationship("Pays", back_populates="orga")
    authorships = db.relationship("Authorship_Orga", back_populates="orga")

    @staticmethod
    def ajout_orga(nom, date_fondation, type_orga, pays, description):
        erreurs = []
        if not nom:
            erreurs.append("Veuillez renseigner un intitulé.")
        if not pays:
            erreurs.append("Veuillez renseigner le pays.")
        if date_fondation:
            if not re.match(REGEX_ANNEE, date_fondation):
                erreurs.append("Les dates doivent être sous le format AAAA et supérieur à 1800")

        unique = Orga.query.filter(Orga.nom).count()
        if unique > 0:
            erreurs.append("Cette personne est déjà présente au sein de la base de données.")

            # S'il y a au moins une erreur, afficher un message d'erreur.
        if len(erreurs) > 0:
            return False, erreurs

            # Si aucune erreur n'a été détectée, ajout d'une nouvelle entrée dans la table Acteur
        nouvelle_orga = Orga(nom=nom,
                             date_fondation=date_fondation,
                             type_orga=type_orga,
                             description=description,
                             pays=pays)

        try:
            db.session.add(nouvelle_orga)
            db.session.add(Authorship_Orga(orga=nouvelle_orga, user=current_user, createur="True"))
            db.session.commit()
            return True, nouvelle_orga

        except Exception as erreur:
            return False, [str(erreur)]

class Militer(db.Model):
    militer_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    acteur_id = db.Column(db.Integer, db.ForeignKey('acteur.id'))
    orga_id = db.Column(db.Integer, db.ForeignKey('orga.id'))
    date_debut = db.Column(db.Text)
    date_fin = db.Column(db.Text)
    statut = db.Column(db.Text)
    #Relations
    orga = db.relationship("Orga", back_populates="militer")
    acteur = db.relationship("Acteur", back_populates="militer")

    @staticmethod
    def ajout_militer(acteur_id, orga_id, date_debut, date_fin, statut):
        erreurs = []
        if not acteur_id:
            erreurs.append("Veuillez renseigner la personne.")
        if not orga_id:
            erreurs.append("Veuillez renseigner l'organisation.")
        if date_debut:
            if not re.match(REGEX_ANNEE, date_debut):
                erreurs.append("Les dates doivent être sous le format AAAA et supérieur à 1800")
        if date_fin:
            if not re.match(REGEX_ANNEE, date_fin):
                erreurs.append("Les dates doivent être sous le format AAAA et supérieur à 1800")

        unique = Militer.query.filter(db.and_(
            Militer.acteur == acteur_id,
            Militer.orga == orga_id
        )).count()
        if unique > 0:
            erreurs.append("Cette participation est déjà présente au sein de la base de données.")

            # S'il y a au moins une erreur, afficher un message d'erreur.
        if len(erreurs) > 0:
            return False, erreurs

            # Si aucune erreur n'a été détectée, ajout d'une nouvelle entrée dans la table Militer
        nouvelle_participation = Militer(date_debut=date_debut,
                                         date_fin=date_fin,
                                         statut=statut,
                                         orga=orga_id,
                                         acteur=acteur_id)

        try:
            db.session.add(nouvelle_participation)
            # Necessite user_id, sinon bug de current_user
            db.session.add(AuthorshipActeur(acteur=acteur_id, authorship_user_id=current_user.user_id))
            db.session.commit()
            return True, nouvelle_participation

        except Exception as erreur:
            return False, [str(erreur)]

class Pays(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    nom = db.Column(db.Text, nullable=False)
    #Relations
    acteur = db.relationship("Acteur", back_populates="pays")
    objet_contest = db.relationship("Objet_contest", back_populates="pays")
    orga = db.relationship("Orga", back_populates="pays")

    @staticmethod
    def ajout_pays(nom):
        erreurs = []
        if not nom:
            erreurs.append("Veuillez renseigner un intitulé.")

        unique = Pays.query.filter(Pays.nom).count()
        if unique > 0:
            erreurs.append("Ce pays est déjà présente au sein de la base de données.")

            # S'il y a au moins une erreur, afficher un message d'erreur.
        if len(erreurs) > 0:
            return False, erreurs

            # Si aucune erreur n'a été détectée, ajout d'une nouvelle entrée dans la table Pays
        nouveau_pays = Pays(nom=nom)

        try:
            db.session.add(nouveau_pays)
            db.session.commit()
            return True, nouveau_pays

        except Exception as erreur:
            return False, [str(erreur)]

class Image(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    nom = db.Column(db.Text, nullable=False)
    legende = db.Column(db.Text)
    lien = db.Column(db.Text, nullable=False)
    objet_id = db.Column(db.Integer, db.ForeignKey('objet_contest.id'))
    # Relations
    objet = db.relationship("Objet_contest", back_populates="image")

    @staticmethod
    def ajout_image(nom, legende, lien, objet_id):
        erreurs = []
        if not nom:
            erreurs.append("Veuillez renseigner un intitulé.")
        if not lien:
            erreurs.append("Le lien n'est pas accepté au sein de la base de données, veuillez réesayer.")
        unique = Image.query.filter(db.and_(
            Image.nom == nom,
            Image.lien == lien
        )).count()
        if unique > 0:
            erreurs.append("Cette participation est déjà présente au sein de la base de données.")

            # S'il y a au moins une erreur, afficher un message d'erreur.
        if len(erreurs) > 0:
            return False, erreurs

            # Si aucune erreur n'a été détectée, ajout d'une nouvelle entrée dans la table Image
        nouvelle_image = Image(nom=nom,
                               legende=legende,
                               lien=lien,
                               objet=objet_id)
        try:
            db.session.add(nouvelle_image)
            #Necessite user_id, sinon bug de current_user
            db.session.add(Authorship_ObjetContest(objet_contest=objet_id, authorship_user_id=current_user.user_id))
            db.session.commit()
            return True, nouvelle_image

        except Exception as erreur:
            return False, [str(erreur)]