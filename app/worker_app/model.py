from app.db_app import db
from app.db_app.model import User
from werkzeug.security import generate_password_hash
import uuid

class Worker(User):
    __abstract__ = False
    __tablename__ = "worker"
    progress = db.Column(db.Float, nullable=False)
    Stores = db.relationship('Store', backref='worker', lazy='dynamic',cascade='all, delete-orphan')

    def __init__(self, account, username, pwd):
        self.account = account
        self.username = username
        self.password = generate_password_hash(pwd)
        self.uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, account))
        self.progress = 0

    def __repr__(self):
        return '<Worker %r>' % self.account