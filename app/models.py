# coding: utf-8
from os import urandom
from hashlib import sha1
from app import db
from datetime import datetime

class Beta(db.Model):
    __tablename__ = 'beta'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    icon = db.Column(db.String(120))
    team = db.Column(db.String(64))
    link = db.Column(db.String(120))
    version = db.Column(db.String(64))
    build = db.Column(db.String(64))
    stable = db.Column(db.Boolean, default=False)
    bundle_id = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime)
    notes = db.Column(db.String(120))
    qrcode = db.Column(db.String(120))
    is_deleted = db.Column(db.Boolean, default=False)

    def __init__(self, name, icon, team, link, version, build, bundle_id, qrcode):
        self.name = name
        self.icon = icon
        self.team = team
        self.link = link
        self.version = version
        self.build = build
        self.bundle_id = bundle_id
        self.timestamp = datetime.now()
        self.notes = ''
        self.qrcode = qrcode

    def __repr__(self):
        return '<%r : Version %r : Build %r>' % (
            self.name, self.version, self.build)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, index=True)
    secret_password = db.Column(db.String(40))
    salt = db.Column(db.String(12))
    nickname = db.Column(db.String(10))
    email = db.Column(db.String(50), unique=True, index=True)
    group = db.Column(db.String(50))
    apps = db.Column(db.String(240), index=True)
    level = db.Column(db.Integer)
    registered_on = db.Column(db.DateTime)

    def __init__(self, username, secret_password, email, salt):
        self.username = username
        self.secret_password = secret_password
        self.salt = salt
        self.email = email
        self.nickname = ''
        self.group = ''
        self.apps = '[]'
        self.level = 1
        self.registered_on = datetime.now()

    def is_admin(self):
        return self.level == 2
 
    def is_active(self):
        return self.level >= 1

    def is_authenticated(self):
        return self.level >= 0
 
    def is_anonymous(self):
        return False

    def set_level(self, level):
        self.level = level
        return level
 
    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)
