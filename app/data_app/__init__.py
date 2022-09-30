from flask import Blueprint

bp = Blueprint('data', __name__, url_prefix='/data')

from app.data_app import views