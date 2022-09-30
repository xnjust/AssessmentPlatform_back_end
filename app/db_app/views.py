from flask import render_template, abort
from . import bp

@bp.route('/')
def show():
    try:
        return 'db_hello'
    except:
        abort(404)