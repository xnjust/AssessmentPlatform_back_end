from flask import jsonify, request, session

from app.worker_app.model import Worker
from app.worker_app import bp
from app.data_app.model import Store, KPI_TOTAL
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from sqlalchemy import extract

@bp.route('/login', endpoint='login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        account = data['account']
        password = data['password']
    
        worker = Worker.query.filter(Worker.account == account).first()
        print(account, password, generate_password_hash(password), worker.password)
        if worker and check_password_hash(worker.password, password):
            session['role'] = 'Worker'
            session['username'] = worker.username
            session['uuid'] = worker.uuid
            return jsonify(status=0,username=worker.username,role='Worker',uuid=worker.uuid)
        else:
            session.clear()
            return jsonify(status=-1, username='', role='',uuid=-1, msg='account or password error')
    except Exception as e:
        print(e)
        return jsonify(status=-1,username='',role='',uuid=-1,msg='data format error')

@bp.route('/get_store', endpoint='get_store', methods=['POST'])
def get_store():
    try:
        data = request.get_json()
        role = data['role']
        size = int(data['size'])
        page = int(data['page'])
        if role != 'worker':
            return jsonify(status=-1,store='',msg='role error')
        worker_uuid = data['worker_uuid']
        worker = Worker.query.filter(Worker.uuid == worker_uuid).first()

        if not worker:
            raise Exception('worker not found')
        stores = worker.Stores.order_by(Store.uuid).all()
        all_len = len(stores)
        if len(stores) > (page-1)*size:
            stores = stores[(page-1)*size:]
        if len(stores) > size:
            workers = workers[:size]
        stores_list = [{'uuid':store.uuid, 'store_name':store.name, 'store_remarks': store.remarks, 'store_belong': store.belong, 'store_grade_yestoday': store.grade_before ,'store_grade_today': store.grade_now} for store in stores]
        for i in range(len(stores_list)):
            belong = stores_list[i]['store_belong']
            if belong:
                worker = Worker.query.filter(Worker.uuid == belong).first()
                if worker:
                    stores_list[i]['store_belong'] = worker.username
                else:
                    stores_list[i]['store_belong'] = "暂无负责人"
            else:
                stores_list[i]['store_belong'] = "暂无负责人"
        data = {
            "total": all_len,
            "rows": stores_list,
        }
        return jsonify(code=200, data=data,message='get worker success')
    except Exception as e:
        data = {
            "total": 0,
            "rows": [],
        }
        return jsonify(code=404, data=data,message='get worker success')

@bp.route('/get_kpi_total', endpoint='get_kpi_total', methods=['POST'])
def get_kpi_total():
    try:
        data = request.get_json()
        role = data['role']
        if role != 'worker':
            return jsonify(status=-1,kpi_total='',msg='role error')
        else:
            all_len = 0
            source = data['source']
            if source == 'all':
                size = int(data['size'])
                page = int(data['page'])

                store_uuid = data['store_uuid']
                store = Store.query.filter(Store.uuid == store_uuid).first()
                kpi_totals = store.kpi_totals.order_by(KPI_TOTAL.uuid).all()
                all_len = len(kpi_totals)
                if len(kpi_totals) > (page-1)*size:
                    kpi_totals = kpi_totals[(page-1)*size:]
                if len(kpi_totals) > size:
                    kpi_totals = kpi_totals[:size]
                kpi_totals_list = [{'uuid':kpi_total.uuid, 'turnover':kpi_total.turnover, 'turnover_target':kpi_total.turnover_target,'turnover_rate': kpi_total.turnover_rate,'income':kpi_total.income, 'income_target':kpi_total.income_target,'income_rate': kpi_total.income_rate,'order_num':kpi_total.order_num, 'order_num_target':kpi_total.order_num_target,'order_num_rate': kpi_total.order_num_rate,
                'time_belong':kpi_total.time_belong.strftime('%Y-%m')} for kpi_total in kpi_totals]
            else:
                all_len = 1
                store_uuid = data['store_uuid']
                store = Store.query.filter(Store.uuid == store_uuid).first()

                date_now = datetime.now().date()
                print(date_now)
                # extract('month', KPI_TOTAL.time_belong)
                # kpi_totals = store.kpi_totals.filter(and_(extract('year', KPI_TOTAL.time_belong) == date_now.year, extract('month', KPI_TOTAL.time_belong) == date_now.month)).first()
                kpi_total = KPI_TOTAL.query.filter(KPI_TOTAL.store_uuid == store_uuid, extract('year', KPI_TOTAL.time_belong) == date_now.year, extract('month', KPI_TOTAL.time_belong) == date_now.month).first()
                # print(kpi_total.time_belong.strftime('%Y-%m'), type(kpi_total.time_belong))
                # kpi_totals = store.kpi_totals.order_by(KPI_TOTAL.time_belong).all()

                kpi_totals_list = [{'uuid':kpi_total.uuid, 'turnover':kpi_total.turnover, 'turnover_target':kpi_total.turnover_target,'turnover_rate': kpi_total.turnover_rate,'income':kpi_total.income, 'income_target':kpi_total.income_target,'income_rate': kpi_total.income_rate,'order_num':kpi_total.order_num, 'order_num_target':kpi_total.order_num_target,'order_num_rate': kpi_total.order_num_rate,
                'time_belong':kpi_total.time_belong.strftime('%Y-%m')}]
            data = {
                "total": all_len,
                "page": page,
                "pageSize": size,
                "rows": kpi_totals_list,
                'summary': {}
            }
            return jsonify(code=200, data=data,message='get kpi_total success')
    except Exception as e:
        print(e)
        return jsonify(status=-1,kpi_total=[],msg='get kpi_total error')
