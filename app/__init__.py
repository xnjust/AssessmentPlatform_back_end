from flask import Flask
from app.db_app import db
from app.db_app import bp as db_bp

from app.manager_app import bp as man_bp
from app.worker_app import bp as wo_bp
from app.data_app import bp as data_bp

from flask_migrate import Migrate
from flask import redirect, url_for, request, render_template

from flask_admin import Admin, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_cors import CORS

from app.views import bp as all_bp

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.manager_app.model import Manager
from app.worker_app.model import Worker
from app.data_app.model import Store, KPI_TOTAL, KPI_PER_DAY, COST_TOTAL, COST_PER_DAY
from app.db_app.model import adminUser

import flask_admin as admin
import flask_login as login
from flask_admin.contrib import sqla
from flask_admin import helpers, expose

from app.data_app.timer_task import Config, scheduler

__version__ = '0.0.1'

app = Flask(__name__)
app.debug = True
app.secret_key = 'some_secret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data_base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SCHEDULER_API_ENABLED'] = True

# app.config.from_object(Config())

CORS(app, supports_credentials=True)

db.init_app(app=app)

Migrate(app, db)

scheduler.init_app(app)
scheduler.start()

# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(id):
        return adminUser.query.filter(adminUser.id == id).first()

init_login()

class MyModelView(sqla.ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated


# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        print(login.current_user)
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return self.render('admin-login.html', logout=True)
        # self._template = 'admin-login.html'
        # return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        if request.method == 'GET':
            print('*********get***********')
            return self.render('admin-login.html', logout=False)
        else:
            username = request.form['username']
            password = request.form['password']
            if username == 'root' and password == 'xroot':
                user = adminUser.query.filter(adminUser.username == username).first()
                if user:
                    pass
                else:
                    user = adminUser(username, password)
                    db.session.add(user)
                    db.session.commit()
                    user = adminUser.query.filter(adminUser.username == username).first()
                login.login_user(user)

            if login.current_user.is_authenticated:
                return redirect(url_for('admin.index'))
            return self.render('admin-login.html', msg='需要超级管理员权限，请联系开发者VX:repoxjust', logout=False)

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('admin.index'))

admin = Admin(app,name=u'后台管理系统',index_view=MyAdminIndexView())

# from app.tea_app.model import Teacher

app.register_blueprint(all_bp)
app.register_blueprint(db_bp)
app.register_blueprint(man_bp)
app.register_blueprint(wo_bp)
app.register_blueprint(data_bp)

admin.add_view(MyModelView(Manager, db.session,endpoint='ManagerClass'))
admin.add_view(MyModelView(Worker, db.session,endpoint='WorkerClass'))
admin.add_view(MyModelView(Store, db.session,endpoint='StoreClass'))
admin.add_view(MyModelView(KPI_TOTAL, db.session,endpoint='KPI_TOTALClass'))
admin.add_view(MyModelView(KPI_PER_DAY, db.session,endpoint='KPI_PER_DAYClass'))
admin.add_view(MyModelView(COST_TOTAL, db.session,endpoint='COST_TOTALClass'))
admin.add_view(MyModelView(COST_PER_DAY, db.session,endpoint='COST_PER_DAYClass'))

@app.route('/')
def index_route():
    return redirect(url_for('all.index'))