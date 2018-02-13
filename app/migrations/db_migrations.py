from flask import Flask
from sqlalchemy.ext.declarative import declared_attr
from flask_login import UserMixin
from datetime import datetime
from flask_bcrypt import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import BaseQuery
from sqlalchemy_searchable import make_searchable, SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import os

app = Flask(__name__)

# Environment Variables Setup
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = bool(os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS'))

db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


make_searchable()


# Require for Full Text Search using Flask_SQLAlchemy
class ArticleQuery(BaseQuery, SearchQueryMixin):
    pass


class BlogUser(db.Model):
    __abstract__ = True

    @declared_attr
    def posts(cls):
        return db.relationship('Post', backref='author', lazy='dynamic')


class CommentUser(db.Model):
    __abstract__ = True

    @declared_attr
    def comments(cls):
        return db.relationship('Comment', backref='author', lazy='dynamic')


followers = db.Table("followers",
                     db.Column("following_id", db.Integer, db.ForeignKey("user.id")),
                     db.Column("followed_id", db.Integer, db.ForeignKey("user.id"))
                     )


class User(UserMixin, BlogUser, CommentUser, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.Binary(128), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime, default=datetime.now)
    first_name = db.Column(db.String(50), nullable=False, default="")
    last_name = db.Column(db.String(50), nullable=False, default="")
    user_title = db.Column(db.String(50), nullable=False, default="")
    image_name = db.Column(db.String(128), default="")
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    joined_on = db.Column(db.DateTime, default=datetime.now)
    followed = db.relationship("User",
                               secondary=followers,
                               primaryjoin=(followers.c.following_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref("follow", lazy="dynamic"),
                               lazy="dynamic")

    def __init__(self, username, email, password, is_admin=False):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.is_admin = is_admin

    def __repr__(self):
        return '<User %r>' % self.username

    def is_following(self, user):
        return self.follow.filter(followers.c.following_id == user.id).count() > 0


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

    comments = db.relationship('Comment', backref='post', cascade='all, delete-orphan', lazy='dynamic')

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


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    comment_datetime = db.Column(db.DateTime, default=datetime.now)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __init__(self, author, content, post):
        self.author = author
        self.content = content
        self.post = post

    def __repr__(self):
        return '<Comment ID %r>' % self.id


class AffiliateProduct(db.Model):
    query_class = ArticleQuery
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(256), nullable=False)
    description = db.Column(db.Text, default='')
    discount_price = db.Column(db.Unicode(16), nullable=False)
    regular_price = db.Column(db.Unicode(16), default='')
    product_url = db.Column(db.String(256), nullable=False)
    image_name = db.Column(db.String(128), default='')
    search_vector = db.Column(TSVectorType('title', 'description'))

    def __init__(self, title, description, discount_price, regular_price, product_url, image_name):
        self.title = title
        self.description = ' '.join(description.split()[:50])
        self.discount_price = discount_price
        self.regular_price = regular_price
        self.product_url = product_url
        self.image_name = image_name

    def __repr__(self):
        return '<Product %r>' % self.title


# very important! This part is for the full text search to work.
db.configure_mappers()

if __name__ == '__main__':
    manager.run()
