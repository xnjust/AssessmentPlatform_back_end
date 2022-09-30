from email import message
from operator import and_
from turtle import st
from flask import jsonify, request, session
from sqlalchemy import desc, extract, and_, func
from app.data_app.model import KPI_PER_DAY, KPI_TOTAL, Store

from app.db_app import db
from app.manager_app.model import Manager
from app.manager_app import bp
from app.worker_app.model import Worker

from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from calendar import monthrange

import requests
import json
from copy import deepcopy


@bp.route('/login', endpoint='login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        print(data)
        account = data['account']
        password = data['password']

        manager = Manager.query.filter(Manager.account == account).first()
        # print(manager.password)
        # print(password)
        # print(check_password_hash(manager.password, password))
        if manager and check_password_hash(manager.password, password):
            session['role'] = 'Manager'
            session['account'] = account
            session['uuid'] = manager.uuid
            return jsonify(status=0, account=account, role='Manager',uuid=manager.uuid, username=manager.username)
        else:
            session.clear()
            return jsonify(status=-1, account='', role='',uuid=-1, msg='account or password error')
    except:
        return jsonify(status=-1,account='',role='',uuid=-1,msg='data format error')

@bp.route('/get_worker', endpoint='get_worker', methods=['POST'])
def get_worker():
    try:
        data = request.get_json()
        username = data['username']
        uuid = data['uuid']
        role = data['role']
        if role != 'manager':
            return jsonify(status=-1,worker='',msg='role error')
        else:
            workers = Worker.query.order_by(Worker.uuid).all()
            workers_list = [{'uuid':worker.uuid, 'worker_name':worker.username} for worker in workers]
            return jsonify(status=0,worker=workers_list,msg='get worker success')
    except Exception as e:
        print(e)
        return jsonify(status=-1,worker=[],msg='get worker error')

@bp.route('/get_worker_by_page', endpoint='get_worker_by_page', methods=['POST'])
def get_worker_by_page():
    try:
        data = request.get_json()
        username = data['username']
        uuid = data['uuid']
        role = data['role']
        size = int(data['size'])
        page = int(data['page'])
        if role != 'manager':
            return jsonify(status=-1,worker='',msg='role error')
        else:
            workers = Worker.query.order_by(Worker.id).all()
            all_len = len(workers)
            print(all_len, page, size, (page-1)*size)
            if len(workers) > (page-1)*size:
                workers = workers[(page-1)*size:]
                if len(workers) > size:
                    workers = workers[:size]
                workers_list = [{'uuid':worker.uuid, 'worker_name':worker.username, 'worker_account': worker.account, 'progress': worker.progress} for worker in workers]
                data = {
                    "total": all_len,
                    "page": page,
                    "pageSize": size,
                    "rows": workers_list,
                    'summary': {}
                }
                return jsonify(code=200, data=data,message='get worker success')
            raise Exception('len error')
    except Exception as e:
        print(e)
        data = {
            "total": 0,
            "page": 0,
            "pageSize": size,
            "rows": [],
            'summary': {}
        }
        return jsonify(code=200, data=data,message='get worker failure')

@bp.route('/add_worker', endpoint='add_worker', methods=['POST'])
def add_worker():
    try:
        data = request.get_json()
        worker_name = data['worker_name']
        worker_account = data['worker_account']
        worker_password = data['worker_password']
        worker = Worker(username=worker_name, pwd=worker_password, account=worker_account)
        db.session.add(worker)
        db.session.commit()
        return jsonify(status=0,msg='add worker success')
    except:
        return jsonify(status=-1,msg='add worker failure')

@bp.route('/edit_worker', endpoint='edit_worker', methods=['POST'])
def edit_worker():
    try:
        data = request.get_json()
        worker_name = data['worker_name']
        worker_uuid = data['worker_uuid']
        worker_password = data['worker_password']
        print("******************************************")
        
        print("\033[1;30m {} \033[0m".format(worker_password))
        worker = Worker.query.filter(Worker.uuid == worker_uuid).first()
        worker.username = worker_name
        worker.password = generate_password_hash(worker_password)
        db.session.commit()
        return jsonify(status=0,msg='edit worker success')
    except:
        return jsonify(status=-1,msg='edit worker failure')

@bp.route('/delete_worker', endpoint='delete_worker', methods=['POST'])
def delete_worker():
    try:
        data = request.get_json()
        worker_uuid = data['worker_uuid']
        worker = Worker.query.filter(Worker.uuid == worker_uuid).first()

        kpi_totals = worker.Stores.order_by(Store.uuid).all()
        for kpi_total in kpi_totals:
            kpi_total.belong = ''
            db.session.commit()

        db.session.delete(worker)
        db.session.commit()
        return jsonify(status=0,msg='delet worker success')
    except Exception as e:
        print(e)
        return jsonify(status=-1,msg='delet worker failure')


@bp.route('/get_store', endpoint='get_store', methods=['POST'])
def get_store():
    try:
        data = request.get_json()
        role = data['role']
        if role != 'manager':
            return jsonify(status=-1,store='',msg='role error')
        else:
            source = data['source']
            if source == 'all':
                stores = Store.query.order_by(Store.uuid).all()
                stores_list = [{'uuid':store.uuid, 'store_name':store.name} for store in stores]
                return jsonify(status=0,store=stores_list,msg='get store success')
            elif source == 'page':
                size = int(data['size'])
                page = int(data['page'])
                stores = Store.query.order_by(Store.id).all()
                all_len = len(stores)
                if len(stores) > (page-1)*size:
                    stores = stores[(page-1)*size:]
                if len(stores) > size:
                    stores = stores[:size]
                stores_list = [{'uuid':store.uuid, 'store_name':store.name, 'store_remarks': store.remarks, 'store_belong': store.belong, 'store_grade_yestoday': store.grade_before ,'store_grade_today': store.grade_now, "store_class": store.store_class} for store in stores]
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

            elif source == 'worker':
                worker_uuid = data['worker_uuid']
                worker = Worker.query.filter(Worker.uuid == worker_uuid).first()
                stores = worker.Stores.order_by(Store.uuid).all()
                stores_list = [{'uuid':store.uuid, 'store_name':store.name} for store in stores]
                return jsonify(status=0,store=stores_list,msg='get store success')
            else:
                return jsonify(status=-1,code=404,store=[],msg='get store error')
    except Exception as e:
        print(e)
        return jsonify(status=-1,store=[],msg='get store error')

@bp.route('/add_store', endpoint='add_store', methods=['POST'])
def add_store():
    def add_meituan_store(cookies_str):
        cookies_dict = {}
        cookies_str = cookies_str.replace(" ", "")
        cookies_str_list = cookies_str.split(";")
        for item in cookies_str_list:
            split_str = item.split("=")
            cookies_dict[split_str[0]] = split_str[1]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            "Host": "e.waimai.meituan.com",
            "Referer": "https://e.waimai.meituan.com/v2/index?ignoreSetRouterProxy=true"
        }

        data_str = "optimus_uuid=f4597f79-0705-4263-b485-a5f1fcaf7f98&optimus_risk_level=71&optimus_code=10&optimus_partner=19"

        data_dict = {}

        for item in data_str.split("&"):
            split_list = item.split("=")
            data_dict[split_list[0]] = split_list[1]

        url = "https://e.waimai.meituan.com/api/poi/poiList?ignoreSetRouterProxy=true"
        res = requests.post(url, cookies=cookies_dict, headers=headers, data=data_dict)

        try:
            json_data = json.loads(res.text)
        except:
            return jsonify(status=-1,msg='add store failure')

        stores_info = json_data["data"]
        for store_info in stores_info:
            try:
                if store_info["id"] == -1 or store_info["id"] == "-1":
                    continue
                print("add store: {}".format(store_info["poiName"]))
                store_name = store_info["poiName"]
                store_remark = "无"
                cookies_cache = deepcopy(cookies_dict)
                cookies_cache["wmPoiId"] = store_info["id"]

                store = Store.query.filter(Store.name == store_name).first()
                if store:
                    print("store {} exits".format(store_info["poiName"]))
                    continue
                store = Store(store_name, store_remark)
                store.cookies = str(cookies_cache)
                store.store_class = "美团"
                db.session.add(store)
                db.session.commit()
                print("add store: {} sccuess".format(store_info["poiName"]))
            except Exception as e:
                print(e)
                print("add store: {} failure".format(store_info["poiName"]))
    try:
        data = request.get_json()
        store_class = data["store_class"]
        get_store_cookies = data["get_store_cookies"]

        if store_class == "meituan":
            add_meituan_store(get_store_cookies)
        return jsonify(status=0,msg='add store success')
    except Exception as e:
        print("\033[31;42m{}\033[0m".format(e))
        return jsonify(status=-1,msg='add store failure')

@bp.route('/edit_store', endpoint='edit_store', methods=['POST'])
def edit_store():
    try:
        data = request.get_json()
        source = data['source']
        if source == 'info':
            store_name = data['store_name']
            store_remarks = data['store_remarks']
            store_uuid = data['store_uuid']
            store = Store.query.filter(Store.uuid == store_uuid).first()
            store.name = store_name
            store.remarks = store_remarks
            db.session.commit()
        elif source == 'belong':
            store_belong = data['worker_uuid']
            store_uuid = data['store_uuid']
            store = Store.query.filter(Store.uuid == store_uuid).first()
            store.belong = store_belong
            db.session.commit()
        elif source == 'grade':
            store_grade_now = data['grade_now']
            store_uuid = data['store_uuid']
            store = Store.query.filter(Store.uuid == store_uuid).first()
            store.grade_before = store.grade_now
            store.grade_now = store_grade_now
            db.session.commit()
        else:
            return jsonify(status=0,msg='edit store failure')


        return jsonify(status=0,msg='edit store success')
    except:
        return jsonify(status=-1,msg='edit store failure')

@bp.route('/delete_store', endpoint='delete_store', methods=['POST'])
def delete_store():
    try:
        data = request.get_json()
        store_uuid = data['store_uuid']
        store = Store.query.filter(Store.uuid == store_uuid).first()

        db.session.delete(store)
        db.session.commit()
        return jsonify(status=0,msg='delet store success')
    except Exception as e:
        print(e)
        return jsonify(status=-1,msg='delet store failure')


#turnover_target, turnover, income_target, income, order_num_target, order_num, store_uuid, time_belong
@bp.route('/get_kpi_total', endpoint='get_kpi_total', methods=['POST'])
def get_kpi_total():
    try:
        data = request.get_json()
        role = data['role']
        if role != 'manager':
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


@bp.route('/add_kpi_total', endpoint='add_kpi_total', methods=['POST'])
def add_kpi_total():
    try:
        data = request.get_json()

        turnover_target = int(data['turnover_target'])
        turnover = int(data['turnover'])
        income_target = int(data['income_target'])
        income = int(data['income'])
        order_num_target = int(data['order_num_target'])
        order_num = int(data['order_num'])
        store_uuid = data['store_uuid']
        time_belong = datetime.now().date()

        store = Store.query.filter(Store.uuid == store_uuid).first()
        kpi_total_database = store.kpi_totals.order_by(desc(KPI_TOTAL.time_belong)).first()

        if kpi_total_database and kpi_total_database.time_belong.year == time_belong.year and kpi_total_database.time_belong.month == time_belong.month:
            return jsonify(status=-1,msg='add kpi_total failure, this month had kpi_total')

        kpi_total = KPI_TOTAL(turnover_target, turnover, income_target, income, order_num_target, order_num, store_uuid, time_belong)
        db.session.add(kpi_total)
        db.session.commit()

        days = monthrange(time_belong.year, time_belong.month)[1]

        turnover_target_perday = turnover_target / days
        turnover_perday = turnover / days
        income_target_perday = income_target / days
        income_perday = income / days
        order_num_target_perday = order_num_target / days
        order_num_perday = order_num / days
        for i in range(1, days+1):
            try:
                time_belong = datetime(time_belong.year, time_belong.month, i)
                kpi_perday = KPI_PER_DAY(turnover_target_perday, turnover_perday, income_target_perday, income_perday, order_num_target_perday, order_num_perday, kpi_total.uuid, time_belong)
                db.session.add(kpi_perday)
                db.session.commit()
            except Exception as e:
                print(e)
        
        return jsonify(status=0,msg='add kpi_total success')
    except Exception as e:
        print(e)
        return jsonify(status=-1,msg='add kpi_total failure')

@bp.route('/edit_kpi_total', endpoint='edit_kpi_total', methods=['POST'])
def edit_kpi_total():
    try:
        data = request.get_json()

        turnover_target = float(data['turnover_target'])
        # turnover = data['turnover']
        income_target = float(data['income_target'])
        # income = data['income']
        order_num_target = float(data['order_num_target'])
        # order_num = data['order_num']
        kpi_total_uuid = data['kpi_total_uuid']

        kpi_total = KPI_TOTAL.query.filter(KPI_TOTAL.uuid == kpi_total_uuid).first()

        kpi_total.turnover_target = turnover_target
        # kpi_total.turnover = turnover

        kpi_total.income_target = income_target
        # kpi_total.income = income

        kpi_total.order_num_target = order_num_target
        # kpi_total.order_num = order_num

        db.session.commit()

        days = monthrange(kpi_total.time_belong.year, kpi_total.time_belong.month)[1]

        turnover_target_perday = turnover_target / days
        income_target_perday = income_target / days
        order_num_target_perday = order_num_target / days
        for i in range(1, days+1):
            try:
                kpi_perday = KPI_PER_DAY.query.filter(KPI_PER_DAY.kpi_total_uuid == kpi_total_uuid, extract('year', KPI_PER_DAY.time_belong) == kpi_total.time_belong.year, extract('month', KPI_PER_DAY.time_belong) == kpi_total.time_belong.month, extract('day', KPI_PER_DAY.time_belong) == i).first()
                kpi_perday.turnover_target = turnover_target_perday
                kpi_perday.income_target = income_target_perday
                kpi_perday.order_num_target = order_num_target_perday
                # db.session.add(kpi_perday)
                db.session.commit()
            except Exception as e:
                print("*********************************")
                print(e)
        
        turnover = db.session.query(func.sum(KPI_PER_DAY.turnover)).filter(KPI_PER_DAY.kpi_total_uuid == kpi_total.uuid).scalar()
        order_num = db.session.query(func.sum(KPI_PER_DAY.order_num)).filter(KPI_PER_DAY.kpi_total_uuid == kpi_total.uuid).scalar()

        kpi_total.turnover = turnover
        kpi_total.turnover_rate = turnover / kpi_total.turnover_target
        kpi_total.order_num = order_num
        kpi_total.order_num_rate = order_num / kpi_total.order_num_target
        db.session.commit()

        return jsonify(status=0,msg='edit kpi_total success')
    except Exception as e:
        print("*********************************")
        print(e)
        return jsonify(status=-1,msg='edit kpi_total failure')

@bp.route('/delete_kpi_total', endpoint='delete_kpi_total', methods=['POST'])
def delete_kpi_total():
    try:
        data = request.get_json()
        kpi_total_uuid = data['kpi_total_uuid']
        kpi_total = KPI_TOTAL.query.filter(KPI_TOTAL.uuid == kpi_total_uuid).first()

        db.session.delete(kpi_total)
        db.session.commit()
        return jsonify(status=0,msg='delet kpi_total success')
    except Exception as e:
        print(e)
        return jsonify(status=-1,msg='delet kpi_total failure')

