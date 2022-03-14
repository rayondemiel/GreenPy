from ..app import db

class Acteur(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    nom = db.Column(db.Text, nullable=False)
    prenom = db.Column(db.Text, nullable=False)
    date_naissance = db.Column(db.Text, nullable=False)
    date_deces = db.Column(db.Text)
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

        unique = Acteur.query.filter(db.and_(
            Acteur.nom == nom,
            Acteur.prenom == prenom,
            Acteur.date_naissance == date_naissance,
            Acteur.pays_naissance == pays_naissance
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
                                pays_naissance = pays_naissance,
                                profession = profession,
                                biographie = biographie)

        try:
            db.session.add(nouveau_acteur)
            db.session.commit()
            return True, nouveau_acteur

        except Exception as erreur:
            return False, [str(erreur)]

class Participation(db.Model):
    participation_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    acteur_id = db.Column(db.Integer, db.ForeignKey('acteur.id'))
    contest_id = db.Column(db.Integer, db.ForeignKey('objet_contest.id'))
    creation_instance = db.Column(db.Text)
    participation_instance = db.Column(db.Text)
    appel_instance_decision = db.Column(db.Text)
    diffusion = db.Column(db.Text)
    participation_decision = db.Column(db.Text)
    rassemblement = db.Column(db.Text)
    production = db.Column(db.Text)
    illegalisme = db.Column(db.Text)
    autre = db.Column(db.Text)
    #Relations
    acteur = db.relationship("Acteur", back_populates="participation")
    objet = db.relationship("Objet_contest", back_populates="participation")

class Objet_contest(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    nom = db.Column(db.Text, nullable=False)
    categ_id = db.Column(db.Integer, db.ForeignKey('categorie.id'))
    description = db.Column(db.Text, nullable=False)
    date_debut = db.Column(db.Text, nullable=False)
    date_fin = db.Column(db.Text)
    ville = db.Column(db.Text, nullable=False)
    dpt = db.Column(db.Text)
    pays_id = db.Column(db.Integer, db.ForeignKey('pays.id'))
    ressources = db.Column(db.Text)
    img_id = db.Column(db.Integer)
    #Relations
    authorships = db.relationship("Authorship_ObjetContest", back_populates="objet_contest")
    participation = db.relationship("Participation", back_populates="objet")
    categorie = db.relationship("Categorie", back_populates="objet_contest")
    pays = db.relationship("Pays", back_populates="objet_contest")

    #ajouter une fonction deverification unique (avec and_ dans ville et nom) -> si les deux sont deja present alors refus -> voir dans creer() de USER

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

class Pays(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    nom = db.Column(db.Text, nullable=False)
    #Relations
    acteur = db.relationship("Acteur", back_populates="pays")
    objet_contest = db.relationship("Objet_contest", back_populates="pays")
    orga = db.relationship("Orga", back_populates="pays")

class Image(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    nom = db.Column(db.Text, nullable=False)
    legende = db.Column(db.Text, nullable=False)
    lien = db.Column(db.Text)