from app.db_app import db
from werkzeug.security import generate_password_hash
import uuid

class adminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password
    def __repr__(self):
        return '<Admin %r>' % self.username
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username

class User(db.Model):
    """定义数据模型"""
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    account = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    uuid = db.Column(db.String(40), unique=True, nullable=False)
 
    def __init__(self, account, username, pwd):
        self.account = account
        self.username = username
        self.password = generate_password_hash(pwd)
        self.uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, account))
 
    def __repr__(self):
        return '<User %r>' % self.account