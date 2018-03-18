from app import db


class ZipcodeDistance(db.Model):
    zipcode = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(32))
    state = db.Column(db.String(3))
    lat = db.Column(db.String(8))
    long = db.Column(db.String(8))
