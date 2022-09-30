from flask import Blueprint

bp = Blueprint('manager', __name__, url_prefix='/manager')

from app.manager_app import views