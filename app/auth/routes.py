from flask import render_template, request, url_for, flash
from flask_login import current_user, logout_user, login_user, login_required
from werkzeug.utils import redirect
from werkzeug.urls import url_parse
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email, send_confirmation_email

@bp.route('/login', methods=["GET", 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        if not user.is_checked:
            flash('Your email is not verified, please check your inbox for confirmation links')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc !='':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already taken
        if User.query.filter_by(username=form.username.data).first() or User.query.filter_by(email=form.email.data).first():
            flash('User with username or email already taken')
            return redirect(url_for('auth.register'))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.send_confirm', userid=user.id))
    return render_template('register.html', form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Email was sent.')
            return redirect(url_for('auth.login'))
        else:
            flash('Email not found')
    return render_template('restore.html', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('auth.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('reset.html', form=form)

@bp.route('/send_confirm/<userid>')
def send_confirm(userid: int):
    user = User.query.get(userid)
    if not user:
        flash('User is not found')
        return redirect(url_for('main.index'))
    send_confirmation_email(user)
    flash('Confirmation was sent.')
    return redirect(url_for('auth.login'))

@bp.route('/confirm/<token>', methods=['GET', 'POST'])
def confirm(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_confirmation_token(token)
    if user:
        user.is_checked = True
        db.session.commit()
        return render_template('confirm.html')
    flash('User is not found or token was expired')
    return redirect(url_for('main.index'))

@bp.route('/resend_confirm', methods=['GET', 'POST'])
def resend_confirm():
    if current_user.is_authenticated:
        return redirect(url_for('main.login'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            return redirect(url_for('auth.send_confirm', userid=user.id))
    flash('Wrong email')
    return render_template('resend_confirm.html', form=form)

