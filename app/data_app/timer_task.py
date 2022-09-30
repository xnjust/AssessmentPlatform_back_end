from glob import escape
from http import cookies
from flask_apscheduler import APScheduler
from datetime import datetime
import requests
import json
from sqlalchemy import extract, func

from app.data_app.model import KPI_TOTAL, Store, KPI_PER_DAY
from app.db_app import db
import threading
import app
from app.worker_app.model import Worker


class Config(object):
    SCHEDULER_API_ENABLED = True


scheduler = APScheduler()



# wmPoiId="8519956"

def get_store_info_from_meituan(cookies_str):
    url = "https://e.waimai.meituan.com/v2/index/r/businessOverview?ignoreSetRouterProxy=true&optimus_uuid=f4597f79-0705-4263-b485-a5f1fcaf7f98&optimus_risk_level=71&optimus_code=10&optimus_partner=19"
    cookies = eval(cookies_str)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        "Host": "e.waimai.meituan.com",
        "Referer": "https://e.waimai.meituan.com/v2/index?ignoreSetRouterProxy=true"
    }

    try:
        print(url, headers)
        res = requests.get(url, cookies=cookies, headers=headers)
        print(res.text)
    except Exception as e:
        print(e)
        print("get store info from meituan error")
        return None, None

    # res = requests.get(url, cookies=cookies, headers=headers)

    json_data = json.loads(res.text)

    return json_data["data"]["totalTurnover"], json_data["data"]["validOrderCount"]

def get_store_info_thread():
    with app.app.app_context():
        print("update store info thread start")
        date_now = datetime.now().date()
        try:
            stores = Store.query.filter(Store.kpi_totals != None)
        except Exception as e:
            stores = []
            print(e)
        if stores:
            for store in stores:
                try:
                    print("try to update store: {}".format(store.name))
                    kpi = store.kpi_totals.filter(extract("year", KPI_TOTAL.time_belong) == date_now.year, extract("month", KPI_TOTAL.time_belong) == date_now.month).first()
                    if kpi:
                        print("store has kpi for month")
                        kpi_perday = kpi.kpi_per_days.filter(extract("year", KPI_PER_DAY.time_belong) == date_now.year, extract("month", KPI_PER_DAY.time_belong) == date_now.month, extract("day", KPI_PER_DAY.time_belong) == date_now.day).first()
                        
                        
                        turnover, order_num = get_store_info_from_meituan(store.cookies)

                        if turnover and order_num:
                            print("get info success, update data for kpi_perday")
                            kpi_perday.turnover = turnover
                            kpi_perday.turnover_rate = turnover / kpi_perday.turnover_target
                            kpi_perday.order_num = order_num
                            kpi_perday.order_num_rate = order_num / kpi_perday.order_num_target
                            db.session.commit()

                            turnover = db.session.query(func.sum(KPI_PER_DAY.turnover)).filter(KPI_PER_DAY.kpi_total_uuid == kpi.uuid).scalar()
                            order_num = db.session.query(func.sum(KPI_PER_DAY.order_num)).filter(KPI_PER_DAY.kpi_total_uuid == kpi.uuid).scalar()

                            kpi.turnover = turnover
                            kpi.turnover_rate = turnover / kpi.turnover_target
                            kpi.order_num = order_num
                            kpi.order_num_rate = order_num / kpi.order_num_target
                            db.session.commit()
                    else:
                        print("store has no kpi for month")
                except Exception as e:
                    print("update error",e)
        else:
            print("have no store who has kpi")

        print("update worker progress")
        try:
            workers = Worker.query.filter(Worker.Stores != None).all()
            if workers:
                for worker in workers:
                    turnovers = []
                    turnover_targets = []
                    order_nums = []
                    order_num_targets = []
                    stores = worker.Stores.filter(Store.kpi_totals != None).all()
                    for store in stores:
                        kpi = store.kpi_totals.filter(extract("year", KPI_TOTAL.time_belong) == date_now.year, extract("month", KPI_TOTAL.time_belong) == date_now.month).first()
                        
                        if kpi:
                            turnovers.append(kpi.turnover)
                            turnover_targets.append(kpi.turnover_target)
                            order_nums.append(kpi.order_num)
                            order_num_targets.append(kpi.order_num_target)
                    
                    turnover_sum = sum(turnovers)
                    turnover_target_sum = sum(turnover_targets)
                    order_num_sum = sum(order_nums)
                    order_num_target_sum = sum(order_num_targets)
                    worker.progress = ((turnover_sum / turnover_target_sum)+(order_num_sum / order_num_target_sum))/2
                    db.session.commit()

                
        except Exception as e:
            print(e)
        print("update worker progress end")

        print("update store info thread end")



# cron examples
# @scheduler.task('cron', id='get_store_info', minute='*')
# def get_store_info():
#     try:
#         t = threading.Thread(target=get_store_info_thread)
#         t.start()
#         print("start update store info thread scuess")
#     except Exception as e:
#         print(e)
#         print("start update store info thread failure")

# # interval examples
# @scheduler.task('interval', id='do_job_1', seconds=30, misfire_grace_time=900)
# def job1():
#     print(str(datetime.datetime.now()) + ' Job 1 executed')


# # cron examples
# @scheduler.task('cron', id='do_job_2', minute='*')
# def job2():
#     print(str(datetime.datetime.now()) + ' Job 2 executed')


# @scheduler.task('cron', id='do_job_3', week='*', day_of_week='sun')
# def job3():
#     print(str(datetime.datetime.now()) + ' Job 3 executed')


# @scheduler.task('cron', id='do_job_3', day='*', hour='13', minute='26', second='05')
# def job4():
#     print(str(datetime.datetime.now()) + ' Job 4 executed')


# if __name__ == '__main__':
#     app = Flask(__name__)
#     app.config.from_object(Config())

#     # it is also possible to enable the API directly
#     # scheduler.api_enabled = True
#     scheduler.init_app(app)
#     scheduler.start()

#     app.run(port=8000)