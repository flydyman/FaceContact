from flask import Blueprint, url_for
from flask_login import current_user

bp = Blueprint('main', __name__, template_folder='templates')

from app.main import routes
