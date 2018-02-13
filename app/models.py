from flask_login import UserMixin
from flask_bcrypt import generate_password_hash
from datetime import datetime
from app import db
from app.blueprints.blog.models import BlogUser, CommentUser
from sqlalchemy_searchable import make_searchable, SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType

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
