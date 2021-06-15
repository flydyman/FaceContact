from flask_mail import Message
from flask import render_template, current_app
from threading import Thread
from app import mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    app = current_app._get_current_object()
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[TEST] PassReset',
        sender=current_app._get_current_object().config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt', user=user, token=token),
        html_body=render_template('email/reset_password.html', user=user, token=token))

def send_confirmation_email(user):
    token = user.get_confirm_token()
    send_email('[TEST] Confirmation',
        sender=current_app._get_current_object().config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template('email/confirmation.txt', user=user, token=token),
        html_body=render_template('email/confirmation.html', user=user, token=token)
    )

