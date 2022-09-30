from app.db_app import db
import uuid

class Store(db.Model):
    __tablename__ = 'store'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    uuid = db.Column(db.String(40), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    belong = db.Column(db.String(40), db.ForeignKey('worker.uuid', ondelete='CASCADE'), nullable=True)
    remarks = db.Column(db.String(200), nullable=True)
    store_class =  db.Column(db.String(200), nullable=False)
    cookies = db.Column(db.String(2000), unique=True, nullable=False)
    grade_before = db.Column(db.Float, nullable=True)
    grade_now = db.Column(db.Float, nullable=True)

    kpi_totals = db.relationship('KPI_TOTAL', backref='store', lazy='dynamic',cascade='all, delete-orphan')
    cost_totals = db.relationship('COST_TOTAL', backref='store', lazy='dynamic',cascade='all, delete-orphan')

    def __init__(self, name, remarks, belong='', grade_before=0, grade_now=0):
        self.name = name
        if belong:
            self.belong = belong
        self.remarks = remarks
        self.grade_before = grade_before
        self.grade_now = grade_now
        self.uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, name))
 
    def __repr__(self):
        return '<Store %r>' % self.name

class KPI_TOTAL(db.Model):
    __tablename__ = 'kpi_total'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    turnover_target = db.Column(db.Float, nullable=False)
    turnover = db.Column(db.Float, nullable=False)
    turnover_rate = db.Column(db.Float, nullable=False)

    income_target = db.Column(db.Float, nullable=False)
    income = db.Column(db.Float, nullable=False)
    income_rate = db.Column(db.Float, nullable=False)

    order_num_target = db.Column(db.Float, nullable=False)
    order_num = db.Column(db.Float, nullable=False)
    order_num_rate = db.Column(db.Float, nullable=False)

    uuid = db.Column(db.String(40), unique=False, nullable=False)
    store_uuid = db.Column(db.String(40), db.ForeignKey('store.uuid', ondelete='CASCADE'), nullable=False)
    time_belong = db.Column(db.Date, nullable=False)

    kpi_per_days = db.relationship('KPI_PER_DAY', backref='kpi_total', lazy='dynamic',cascade='all, delete-orphan')

    def __init__(self, turnover_target, turnover, income_target, income, order_num_target, order_num, store_uuid, time_belong):
        self.turnover_target = turnover_target
        self.turnover = turnover
        if turnover_target != 0:
            self.turnover_rate = (turnover / turnover_target) * 100
        else:
            self.turnover_rate = 0

        self.income_target = income_target
        self.income = income
        if income_target != 0:
            self.income_rate = (income / income_target) * 100
        else:
            self.income_rate = 0

        self.order_num_target = order_num_target
        self.order_num = order_num
        if order_num_target != 0:
            self.order_num_rate = (order_num / order_num_target) * 100
        else:
            self.order_num_rate = 0

        self.uuid = str(uuid.uuid1())

        self.store_uuid = store_uuid
        self.time_belong = time_belong
 
    def __repr__(self):
        return '<KPI %r>' % self.uuid

class KPI_PER_DAY(db.Model):
    __tablename__ = 'kpi_per_day'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    turnover_target = db.Column(db.Float, nullable=False)
    turnover = db.Column(db.Float, nullable=False)
    turnover_rate = db.Column(db.Float, nullable=False)

    income_target = db.Column(db.Float, nullable=False)
    income = db.Column(db.Float, nullable=False)
    income_rate = db.Column(db.Float, nullable=False)

    order_num_target = db.Column(db.Float, nullable=False)
    order_num = db.Column(db.Float, nullable=False)
    order_num_rate = db.Column(db.Float, nullable=False)

    uuid = db.Column(db.String(40), unique=False, nullable=False)
    kpi_total_uuid = db.Column(db.String(40), db.ForeignKey('kpi_total.uuid', ondelete='CASCADE'), nullable=False)
    time_belong = db.Column(db.Date, nullable=False)

    def __init__(self, turnover_target, turnover, income_target, income, order_num_target, order_num, kpi_total_uuid, time_belong):
        self.turnover_target = turnover_target
        self.turnover = turnover
        if turnover_target != 0:
            self.turnover_rate = (turnover / turnover_target) * 100
        else:
            self.turnover_rate = 0

        self.income_target = income_target
        self.income = income
        if income_target != 0:
            self.income_rate = (income / income_target) * 100
        else:
            self.income_rate = 0

        self.order_num_target = order_num_target
        self.order_num = order_num
        if order_num_target != 0:
            self.order_num_rate = (order_num / order_num_target) * 100
        else:
            self.order_num_rate = 0

        self.uuid = str(uuid.uuid1())

        self.kpi_total_uuid = kpi_total_uuid
        self.time_belong = time_belong
 
    def __repr__(self):
        return '<KPI_Perday %r>' % self.uuid

class COST_TOTAL(db.Model):
    __tablename__ = 'cost_total'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    store_uuid = db.Column(db.String(40), db.ForeignKey('store.uuid', ondelete='CASCADE'), nullable=False)
    time_belong = db.Column(db.Date, nullable=False)
    uuid = db.Column(db.String(40), unique=False, nullable=False)
    cost = db.Column(db.Float, nullable=False)

    cost_per_days = db.relationship('COST_PER_DAY', backref='cost_total', lazy='dynamic',cascade='all, delete-orphan')

    def __init__(self, time_belong, cost, store_uuid):
        self.uuid = uuid.uuid1()

        self.time_belong = time_belong

        self.cost = cost

        self.store_uuid = store_uuid

 
    def __repr__(self):
        return '<COST %r>' % self.uuid


class COST_PER_DAY(db.Model):
    __tablename__ = 'cost_per_day'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    cost_total_uuid = db.Column(db.String(40), db.ForeignKey('cost_total.uuid', ondelete='CASCADE'), nullable=False)
    time_belong = db.Column(db.Date, nullable=False)
    uuid = db.Column(db.String(40), unique=False, nullable=False)
    cost = db.Column(db.Float, nullable=False)

    def __init__(self, time_belong, cost, store_uuid):
        self.uuid = uuid.uuid1()

        self.time_belong = time_belong

        self.cost = cost

        self.store_uuid = store_uuid

 
    def __repr__(self):
        return '<COST %r>' % self.uuid

    
