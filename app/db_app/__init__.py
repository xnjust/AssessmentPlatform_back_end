from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

bp = Blueprint('db', __name__, url_prefix='/db')

from . import views
from .model import adminUser
from app.manager_app.model import Manager
from app.worker_app.model import Worker
from app.data_app.model import Store, KPI_TOTAL, KPI_PER_DAY, COST_TOTAL, COST_PER_DAY
