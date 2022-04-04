from flask import render_template, redirect, url_for, flash
from flask_mail import Message
from flask_login import current_user

from ..app import mail, app, db
from ..modeles.forms import ResetPasswordRequestForm, ResetPasswordForm
from ..modeles.utilisateurs import User

def send_email(subject, sender, recipients, text_body, html_body):
    """
    Fonction décrivant le modèle de la fonction d'envoie d'un mail

    :param subject: Objet du mail
    :param sender: Adresse mail émettrice
    :param recipients: Adresse mail réceptrice
    :param text_body: Contenu en texte simple
    :param html_body: Contenu au format html
    :return: None
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def inscription_mail(donnees):
    """
    Fonction envoyant un mail notifiant de l'inscription

    :param donnees: ensemble des attributs de classes enregistrées lors de la fonction inscription()
    :return: None
    """
    send_email("Validation inscription",
               sender=app.config['MAIL_USERNAME'],
               recipients=[donnees.user_email],
               text_body=render_template('email/pages/inscription_mail.txt', user=donnees),
               html_body=render_template("email/pages/inscription_mail.html", user=donnees))

def mdp_mail(user):
    """
    Fonction permettant d'envoyer un mail de réinitialisation de mot de passe

    :param user: utilisateur capturé
    :return: None
    """
    token = user.get_reset_password_token()
    send_email('GreenPy | Demande de mot de passe',
               sender=app.config['MAIL_USERNAME'],
               recipients=[user.user_email],
               text_body=render_template('email/pages/reset_mdp_requete.txt', user=user, token=token),
               html_body=render_template('email/pages/reset_mdp_requete.html', user=user, token=token))

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """
    Fonction permettant de vérifier que l'utilisateur est bien présent au sein de la base de données et d'initier la fonction mdp_mail()
    Si l'utilisateur est déjà identifier alors il redirigé vers l'accueil.
    :return: Html template
    """
    if current_user.is_authenticated:
        return redirect(url_for('/accueil'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.email.data).first()
        if user:
            mdp_mail(user)
        flash("Regardez votre boîte mail d'ici quelques instants")
        return redirect(url_for('connexion'))
    return render_template('email/reset_password.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Fonction de reinitialisation du mot de passe de l'utilisateur à partir du formulaire de reinitialisation.
    Si l'utilisateur est déjà identifier ou n'est pas le même, alors il redirigé vers l'accueil.

    :param token: Retour de la variable de la fonction mdp_mail() ou rediction vers l'accueil
    :return: Template Html
    """
    if current_user.is_authenticated:
        return redirect(url_for('accueil'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('accueil'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Votre mot de passe a été changé')
        return redirect(url_for('connexion'))
    return render_template('email/password_reponse.html', form=form)
