from flask import Flask, g, redirect, url_for
from functools import wraps
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_recaptcha import ReCaptcha
import os

app = Flask(__name__)

# Environment Variables Setup
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['HOST'] = os.environ.get('HOST')
app.config['PORT'] = int(os.environ.get('PORT'))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = bool(os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS'))
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH'))
app.config['BUCKET_IMAGES'] = os.environ.get('BUCKET_IMAGES')
app.config['BUCKET_PHOTOS'] = os.environ.get('BUCKET_PHOTOS')
app.config['BUCKET_FILES'] = os.environ.get('BUCKET_FILES')
app.config['AWS_ACCESS_KEY_ID'] = os.environ.get('AWS_ACCESS_KEY_ID')
app.config['AWS_SECRET_ACCESS_KEY'] = os.environ.get('AWS_SECRET_ACCESS_KEY')
app.config['S3_BUCKET'] = os.environ.get('S3_BUCKET')
app.config['S3_URL'] = os.environ.get('S3_URL')
app.config['BUCKET_URL'] = os.environ.get('BUCKET_URL')
app.config['DEFAULT_PHOTO'] = os.environ.get('DEFAULT_PHOTO')
app.config['RECAPTCHA_ENABLED'] = bool(os.environ.get('RECAPTCHA_ENABLED'))
app.config['RECAPTCHA_SITE_KEY'] = os.environ.get('RECAPTCHA_SITE_KEY')
app.config['RECAPTCHA_SECRET_KEY'] = os.environ.get('RECAPTCHA_SECRET_KEY')
app.config['RECAPTCHA_THEME'] = os.environ.get('RECAPTCHA_THEME')

csrf = CSRFProtect(app)
csrf.init_app(app)
recaptcha = ReCaptcha(app=app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

db = SQLAlchemy(app)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user.is_admin:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def before_request():
    g.user = current_user

from app import views
