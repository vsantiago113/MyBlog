from app import db
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr
from flask_sqlalchemy import BaseQuery
from sqlalchemy_searchable import make_searchable, SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType

make_searchable()


# Require for Full Text Search using Flask_SQLAlchemy
class ArticleQuery(BaseQuery, SearchQueryMixin):
    pass


class BlogUser(db.Model):
    __abstract__ = True

    @declared_attr
    def posts(cls):
        return db.relationship('Post', backref='author', lazy='dynamic')


class Post(db.Model):
    query_class = ArticleQuery
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(256), nullable=False)
    body = db.Column(db.UnicodeText, default='')
    excerpt = db.Column(db.Text, default='')
    pub_date = db.Column(db.DateTime)
    image_name = db.Column(db.String(128), default="")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    search_vector = db.Column(TSVectorType('title', 'body'))

    def __init__(self, title, body, excerpt, pub_date, image_name, author):
        self.title = title
        self.body = body
        self.excerpt = ' '.join(excerpt.split()[:50]) + '[...]'
        if isinstance(pub_date, str):
            pub_date = datetime.strptime(pub_date, "%Y/%m/%d")
        self.pub_date = pub_date
        self.image_name = image_name
        self.author = author

    def __repr__(self):
        return '<Post %r>' % self.title


# very important! This part is for the full text search to work.
db.configure_mappers()
