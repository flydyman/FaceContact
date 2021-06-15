from app import db, login
from flask import current_app
from flask_login import UserMixin
from datetime import datetime
from time import time
import jwt
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash

followers = db.Table('followers', 
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

usergroups = db.Table('user_groups',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')))

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), index=True, unique=True)
    users = db.relationship('User', secondary=usergroups,
        primaryjoin=(usergroups.c.group_id == id), 
        # secondaryjoin=(usergroups.c.group_id == id),
        backref=db.backref('usergroups', lazy='dynamic'), 
        lazy='dynamic')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), index=True, unique=True)
    email = db.Column(db.String(100), index=True, unique=True)
    password = db.Column(db.String(250))
    is_checked = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    groups = db.relationship('Group', secondary=usergroups,
        primaryjoin=(usergroups.c.user_id == id), 
        backref=db.backref('usergroups', lazy='dynamic'), 
        lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())

    def _is_admin(self):
        groups = self.groups.filter_by(name='Admins').first()
        return groups is not None

    def is_in_group(self, group):
        return self.groups.filter(usergroups.c.group_id == group.id).count() > 0

    def add_to_group(self, group):
        if not self.is_in_group(group):
            self.groups.append(group)

    def remove_from_group(self, group):
        if self.is_in_group(group):
            self.groups.remove(group)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({
            'reset_password': self.id,
            'exp': time() + expires_in
        }, current_app._get_current_object().config['SECRET_KEY'], algorithm='HS256')

    def get_confirm_token(self, expires_in=6000):
        return jwt.encode({
            'confirm': self.id,
            'exp': time() + expires_in
        }, current_app._get_current_object().config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def get_groups_ids(user):
        res = ""
        first = True
        groups = user.groups
        if groups:
            for group in groups:
                if not first:
                    res += ','
                res += str(group.id)
                first = False
        return res

    @staticmethod
    def set_group_ids(source: str):
        res = []
        sub = source.split(',')
        for s in sub:
            if s:
                res.append(int(s, base=10))
        res.sort()
        return res

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app._get_current_object().config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    @staticmethod
    def verify_confirmation_token(token):
        try:
            id = jwt.decode(token, current_app._get_current_object().config['SECRET_KEY'], algorithms=['HS256'])['confirm']
        except:
            return
        return User.query.get(id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

