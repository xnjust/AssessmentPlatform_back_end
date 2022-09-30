from flask import jsonify, request, session

from app.worker_app.model import Worker
from app.data_app import bp
from app.data_app.model import KPI_PER_DAY, Store, KPI_TOTAL
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from sqlalchemy import extract, func
from app.db_app import db

@bp.route('/get_achievements_data', endpoint='get_achievements_data', methods=['POST'])
def get_achievements_data():
    try:
        workers = Worker.query.filter(Worker.Stores != None).all()
        workers_name = [worker.username for worker in workers]
        date_now = datetime.now().date()
        workers_info = []
        for i in range(len(workers_name)):
            turnover = 0
            income = 0
            order_num = 0
            stores = Store.query.filter(Store.belong == workers[i].uuid).all()
            stores_uuid = [store.uuid for store in stores]
            # print("****************", stores_uuid)
            if stores_uuid:
                kpis = KPI_TOTAL.query.filter(KPI_TOTAL.store_uuid.in_(stores_uuid), extract('year', KPI_TOTAL.time_belong) == date_now.year, extract('month', KPI_TOTAL.time_belong) == date_now.month).all()
                kpis_uuid = [kpi.uuid for kpi in kpis]
                # print("****************", kpis_uuid)
                if kpis_uuid:
                    turnover = db.session.query(func.sum(KPI_PER_DAY.turnover)).filter(KPI_PER_DAY.kpi_total_uuid.in_(kpis_uuid)).scalar()
                    income = db.session.query(func.sum(KPI_PER_DAY.income)).filter(KPI_PER_DAY.kpi_total_uuid.in_(kpis_uuid)).scalar()
                    order_num = db.session.query(func.sum(KPI_PER_DAY.order_num)).filter(KPI_PER_DAY.kpi_total_uuid.in_(kpis_uuid)).scalar()
            # print("**{}**{}**".format(workers_name[i], turnover))
                    workers_info.append({"worker_name":workers_name[i], "turnover": turnover, "income":income, "order_num":order_num})
        return jsonify(status=0, workers_info=workers_info, msg="get achievements data success")
    except Exception as e:
        print(e)
        return jsonify(status=-1, workers_info=workers_info, msg="get achievements data failure")

@bp.route('/get_store', endpoint='get_store', methods=['POST'])
def get_store():
    try:

        date_now = datetime.now().date()
        stores = Store.query.filter(Store.belong != None, Store.kpi_totals != None).all()
        print(stores)
        stores_list = []
        for store in stores:
            kpi = store.kpi_totals.filter(extract('year', KPI_TOTAL.time_belong) == date_now.year, extract('month', KPI_TOTAL.time_belong) == date_now.month).all()
            if kpi:
                kpi_today = kpi[0].kpi_per_days.filter(extract('day', KPI_PER_DAY.time_belong) == date_now.day).first()
                stores_list.append({"store_name": store.name+"/"+str(store.grade_now - store.grade_before), "turnover":kpi_today.turnover, "income":kpi_today.income, "order_num": kpi_today.order_num, "grade": store.grade_now})
        
        # print(stores_list)

        return jsonify(status=0, message='get store success', stores_list=stores_list)

    except Exception as e:
        print(e)
        return jsonify(status=-1,stores_list=[],msg='get store error')

@bp.route('/get_progress', endpoint='get_progress', methods=['POST'])
def get_progress():
    try:
        workers = Worker.query.order_by(Worker.progress.desc()).all()
        worker_list = [{"index": index, "username": worker.username, "progress": worker.progress} for index, worker in enumerate(workers)]
        return jsonify(status=0,worker_list=worker_list,msg='get progress success')
    except Exception as e:
        print(e)
        return jsonify(status=-1,worker_list=[],msg='get progress error')