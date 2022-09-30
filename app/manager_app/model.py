import imp
from app.db_app import db
from app.db_app.model import User

class Manager(User):
    __abstract__ = False
    __tablename__ = "manager"
    def __repr__(self):
        return '<Manager %r>' % self.account