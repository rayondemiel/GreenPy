from flask import render_template
from flask_mail import Message
from ..app import mail, app
from ..modeles import utilisateurs

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def inscription_mail(addr_mail: str):
    send_email("Validation inscription",
               sender=app.config['MAIL_USERNAME'],
               recipients=addr_mail,
               text_body=render_template('email/pages/inscription_mail.txt'),
               html_body=render_template("email/pages/inscription_mail.html",
                                         titre="Inscription GreenPY"))

def mdp_mail(user):
    token = user.get_reset_password_token()
    send_email('GreenPy | Demande de mot de passe',
               sender=app.config['MAIL_USERNAME'],
               recipients=[user.user_email],
               text_body=render_template('email/pages/reset_mdp_requete.txt',
                                         user=user, token=token),
               html_body=render_template('email/pages/reset_mdp_requete.txt',
                                         user=user, token=token, titre="Reset Password"))