from flask import Flask, url_for, get_flashed_messages
from config import Config
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

login = LoginManager()
login.login_view='auth.login'
login.login_message='Please login to see that page'
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

from app import models
from app.main import bp as main_bp
from app.auth import bp as auth_bp
from app.admin import bp as admin_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    login.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    app.app_context().push()
    db.create_all()

    return app


