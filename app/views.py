from flask import Blueprint, request, session, jsonify

from app.db_app import db
from app.manager_app.model import Manager
from app.worker_app.model import Worker

bp = Blueprint('all', __name__, url_prefix="/r")

@bp.route('/register', endpoint='register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        role = data['role']
        username = data['username']
        account = data['account']
        password = data['password']
        if role == 'manager':
            manager = Manager.query.filter(Manager.account == account).first()
            if manager:
                return jsonify(status=-1,msg='account has been used')
            manager = Manager(username=username, pwd=password, account=account)
            db.session.add(manager)
            db.session.commit()
            return jsonify(status=0,msg='register success', uuid=manager.uuid)
            
        else:
            worker = Worker.query.filter(Worker.account == account).first()
            if worker:
                return jsonify(status=-1,msg='account has been used')
            worker = Worker(username=username, pwd=password, account=account)
            db.session.add(worker)
            db.session.commit()
            return jsonify(status=0,msg='register success', uuid=worker.uuid)
    except Exception as e:
        print('error ', e)
        return jsonify(status=-1,msg='register failure')

@bp.route('/logout', endpoint='logout', methods=['POST'])
def logout():
    data = request.get_json()
    uuid = data['uuid']
    if session.get('uuid') == uuid or not session.get('uuid'):
        session.clear()
        return jsonify(status=0,msg='logout success')
    return jsonify(status=-1,msg='logout failure')