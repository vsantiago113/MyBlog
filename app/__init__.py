from flask import Flask, g, redirect, url_for
from functools import wraps
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
from werkzeug.wsgi import SharedDataMiddleware

app = Flask(__name__)
app.config.from_json("config.json")
csrf = CSRFProtect(app)
csrf.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

db = SQLAlchemy(app)

app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/_uploads':  '_uploads'
})

images = UploadSet("images", IMAGES)
photos = UploadSet("photos", IMAGES)
configure_uploads(app, (images, photos))

patch_request_class(app)


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
