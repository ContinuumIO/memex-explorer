from . import db

# Table Relations

# A plot can be sourced from multiple data sources,
#   each data source can drive multiple plots.
data_plot = db.Table('data_plot',
    db.Column('data_source_id', db.Integer, db.ForeignKey('data_source.id')),
    db.Column('plot_id', db.Integer, db.ForeignKey('plot.id'))
)


class Project(db.Model):
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    slug = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(64))
    crawls = db.relationship('Crawl', backref='project', lazy='dynamic')
    image_spaces = db.relationship('ImageSpace', backref='project', lazy='dynamic')
    crawl_models = db.relationship('CrawlModel', backref='project', lazy='dynamic')

    def __repr__(self):
        return '<Project %r>' % (self.name)


class Crawl(db.Model):
    __tablename__ = "crawl"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    slug = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text)
    crawler = db.Column(db.String(64))
    status = db.Column(db.String(64))
    config = db.Column(db.String(64))
    seeds_list = db.Column(db.String(64))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    crawl_model_id = db.Column(db.Integer, db.ForeignKey('crawl_model.id'))
    image_space = db.relationship('ImageSpace', backref='crawl', uselist=False)
    data_sources = db.relationship('DataSource', backref='crawl', lazy='dynamic')
    pages_crawled = db.Column(db.BigInteger)
    harvest_rate = db.Column(db.Float)

    def __repr__(self):
        return '<Crawl %r>' % (self.name)


class CrawlModel(db.Model):
    __tablename__ = "crawl_model"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    def __repr__(self):
        return '<CrawlModel %r>' % (self.name)


class DataSource(db.Model):
    __tablename__ = "data_source"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    data_uri = db.Column(db.String(120))
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    crawl_id = db.Column(db.Integer, db.ForeignKey('crawl.id'))
    plots = db.relationship('Plot', secondary=data_plot, \
        backref=db.backref('data', lazy='dynamic'))

    def __repr__(self):
        return '<DataSource %r>' % (self.name)

        
class ImageSpace(db.Model):
    __tablename__ = "image_space"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    slug = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    crawl_id = db.Column(db.Integer, db.ForeignKey('crawl.id'))
    images = db.relationship('Image', backref='image_space', lazy='dynamic')

    def __repr__(self):
        return '<ImageSpace %r>' % (self.id)


class Image(db.Model):
    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(140))
    EXIF_LensSerialNumber = db.Column(db.String(140))
    MakerNote_SerialNumberFormat = db.Column(db.String(140))
    EXIF_BodySerialNumber = db.Column(db.String(140))
    MakerNote_InternalSerialNumber = db.Column(db.String(140))
    MakerNote_SerialNumber = db.Column(db.String(140))
    Image_BodySerialNumber = db.Column(db.String(140))
    uploaded = db.Column(db.Integer)
    image_space_id = db.Column(db.Integer, db.ForeignKey('image_space.id'))

    def __unicode__(self):
        return '<Image %s>' % self.filename


class Plot(db.Model):
    __tablename__ = "plot"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    endpoint = db.Column(db.String(64), index=True, unique=True)
    plot = db.Column(db.String(64), index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    crawl_id = db.Column(db.Integer, db.ForeignKey('crawl.id'))
    source_id = db.Column(db.String(64))
    autoload_tag = db.Column(db.Text)

    def __unicode__(self):
        return '<Plot %s>' % self.name

