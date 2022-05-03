from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo

#Classe pour WTFform utilisé pour la gestion des mails

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Demander un  nouveau mot de passe')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repétez le mot de passe', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Changez votre mot de passe')