from flask import render_template
from flask_login import current_user
from datetime import datetime
from app.main import bp
from app import db

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/')
def index():
    return render_template('index.html')

