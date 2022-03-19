from ..app import db
import datetime

class AuthorshipActeur(db.Model):
    __tablename__ = "authorship_acteur"
    authorship_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    authorship_acteur_id = db.Column(db.Integer, db.ForeignKey('acteur.id'))
    authorship_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    authorship_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    createur = db.Column(db.Text)
    #Relations
    user = db.relationship("User", back_populates="authorships_acteur")
    acteur = db.relationship("Acteur", back_populates="authorships")

class Authorship_ObjetContest(db.Model):
    __tablename__ = "authorship_objet_contest"
    authorship_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    authorship_objet_id = db.Column(db.Integer, db.ForeignKey('objet_contest.id'))
    authorship_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    authorship_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    #Relations
    user = db.relationship("User", back_populates="authorships_objet")
    objet_contest = db.relationship("Objet_contest", back_populates="authorships")

class Authorship_Orga(db.Model):
    __tablename__ = "authorship_orga"
    authorship_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    authorship_orga_id = db.Column(db.Integer, db.ForeignKey('orga.id'))
    authorship_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    authorship_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    #Relations
    user = db.relationship("User", back_populates="authorships_orga")
    orga = db.relationship("Orga", back_populates="authorships")