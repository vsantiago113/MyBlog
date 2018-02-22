from app import db
from flask_sqlalchemy import BaseQuery
from sqlalchemy_searchable import make_searchable, SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType

make_searchable()


# Require for Full Text Search using Flask_SQLAlchemy
class ProductQuery(BaseQuery, SearchQueryMixin):
    pass


class AffiliateProduct(db.Model):
    query_class = ProductQuery
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
