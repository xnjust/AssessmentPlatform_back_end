from flask import Blueprint

bp = Blueprint('worker', __name__, url_prefix='/worker')

from app.worker_app import views