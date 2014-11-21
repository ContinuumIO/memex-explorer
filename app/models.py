from . import db

plots = db.Table('plots',
    db.Column('plot_id', db.Integer, db.ForeignKey('plot.id')),
    db.Column('monitor_data_id', db.Integer, db.ForeignKey('monitor_data.id')),
    db.Column('dashboard_id', db.Integer, db.ForeignKey('dashboard.id')),
    db.Column('crawl_id', db.Integer, db.ForeignKey('crawl.id'))
)


dashboards = db.Table('dashboards',
    db.Column('dashboard_id', db.Integer, db.ForeignKey('dashboard.id')),
    db.Column('plot_id', db.Integer, db.ForeignKey('plot.id')),
)


class Crawl(db.Model):
    __tablename__ = "crawl"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    endpoint = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.Text)
    monitor_data = db.relationship('MonitorData', backref='crawl', lazy='dynamic')
    plots = db.relationship('Plot', secondary=plots, \
        backref=db.backref('crawl', lazy='dynamic'))

    def __repr__(self):
        return '<Crawl %r>' % (self.name)


class MonitorData(db.Model):
    __tablename__ = "monitor_data"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    endpoint = db.Column(db.String(64), index=True, unique=True)
    data_uri = db.Column(db.String(120), index=True, unique=True)
    description = db.Column(db.Text)
    crawl_id = db.Column(db.Integer, db.ForeignKey('crawl.id'))
    plots = db.relationship('Plot', secondary=plots, \
        backref=db.backref('data', lazy='dynamic'))

    def __repr__(self):
        return '<MonitorData %r>' % (self.name)


class Plot(db.Model):
    __tablename__ = "plot"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.Text)
    endpoint = db.Column(db.String(64), index=True, unique=True)
    plot = db.Column(db.String(64), index=True)
    dashboards = db.relationship('Dashboard', secondary=dashboards, \
        backref=db.backref('plot', lazy='dynamic'))


class Dashboard(db.Model):
    __tablename__ = "dashboard"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    endpoint = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.Text)
    plots = db.relationship('Plot', secondary=plots, \
        backref=db.backref('dashboard', lazy='dynamic'))

