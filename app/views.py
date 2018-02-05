from flask import redirect, url_for, render_template, flash, g, session, request, jsonify
from flask_login import login_required, login_user, logout_user
from functools import wraps
from flask_bcrypt import generate_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO
import os
import uuid
from app import app
from app import login_manager
from app import db
from app import photos
from app import images
from app.forms import LoginForm, RegistrationForm, ChangeProfileImageForm, ChangePasswordForm, EditProfileForm
from app.models import User, followers, initialize
from app.blueprints.blog import blog
from app.blueprints.blog.models import Post
from app.blueprints.affiliate_store import affiliate_store
from app.blueprints.affiliate_store.models import AffiliateProduct
from app import csrf
from app import admin_required

app.register_blueprint(blog)
app.register_blueprint(affiliate_store)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@login_manager.user_loader
def load_user(user_id):
    return User.query.get_or_404(int(user_id))


@app.route("/")
def home():
    user = User.query.get(1)
    posts = Post.query.order_by(Post.pub_date.desc()).limit(3)
    products = AffiliateProduct.query.order_by(AffiliateProduct.id.desc()).limit(3)
    return render_template('index.html', posts=posts, products=products, user=user, images=images, photos=photos)


@app.route("/login", methods=("GET", "POST"))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first_or_404()
        if form.remember_me.data:
            login_user(user, remember=True)
        else:
            login_user(user)
        return redirect(url_for("home"))
    else:
        return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been successfully logged out!", "info")
    return redirect(url_for("login"))


@app.route('/terms_of_service')
def terms_of_service():
    return render_template('terms_of_service.html')


@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')


@app.route("/registration", methods=("GET", "POST"))
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(form.username.data, form.email.data, form.password.data, False)
        db.session.add(user)
        db.session.commit()
        flash("your account has been created successfully you can now log in.", "success")
        return redirect(url_for("login"))
    else:
        return render_template("registration.html", form=form)


@app.route("/myprofile")
@login_required
def my_profile():
    return redirect(url_for("user_profile", user_id=g.user.id))


@app.route("/user_profile/<path:user_id>")
def user_profile(user_id):
    user = User.query.get(user_id)
    return render_template("profile_templates/user_profile.html", user=user, profile_image=photos)


@app.route("/update_image", methods=["GET", "POST"])
@login_required
def change_profile_image():
    form = ChangeProfileImageForm()
    if form.validate_on_submit():
        if bool(g.user.image_name) is False:
            pass
        else:
            try:
                os.remove(photos.path(g.user.image_name))
            except OSError:
                pass
        maxsize = (350, 235)
        old_filename = secure_filename(form.image_name.data.filename)
        file_name, file_ext = os.path.splitext(old_filename)
        img = Image.open(BytesIO(form.image_name.data.read()))
        unique_filename = str(uuid.uuid4()) + file_ext
        # img = img.resize(maxsize, Image.ANTIALIAS)
        img.save(os.path.join('_uploads/photos', unique_filename), quality=95)
        img.close()
        g.user.image_name = unique_filename
        db.session.commit()
        return redirect(url_for("user_profile", user_id=g.user.id))
    return render_template("profile_templates/change_profile_image.html", form=form)


@app.route("/delete_profile_image")
@login_required
def delete_profile_image():
    if bool(g.user.image_name) is False:
        pass
    else:
        try:
            os.remove(photos.path(g.user.image_name))
        except OSError:
            pass
        g.user.image_name = ""
        db.session.commit()
    return redirect(url_for("user_profile", user_id=g.user.id))


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        g.user.first_name = form.first_name.data
        g.user.last_name = form.last_name.data
        g.user.user_title = form.user_title.data
        db.session.commit()
        flash("Your profile has been updated.", "info")
        return redirect(url_for("user_profile", user_id=g.user.id))
    else:
        return render_template("profile_templates/edit_profile.html", form=form)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        g.user.password = generate_password_hash(form.password.data)
        db.session.commit()
        logout_user()
        flash("Your password has been successfully updated. Please login with your new password.", "info")
        return redirect(url_for("login"))
    else:
        return render_template("profile_templates/change_password.html", form=form)


@app.route("/follow_user/<path:user_id>")
@login_required
def follow_user(user_id):
    user = User.query.get(user_id)
    if g.user.follow.filter(followers.c.following_id == user.id).count():
        g.user.follow.remove(user)
    else:
        g.user.follow.append(user)
    db.session.commit()
    return redirect(url_for("user_profile", user_id=user_id))


@app.route('/file_browser')
@login_required
@admin_required
def file_browser():
    image_list = []
    for i in os.listdir('_uploads/images'):
        image_list.append('/_uploads/images/' + i)
    return render_template('file_browser.html', image_list=image_list)


@app.route("/file_upload", methods=["GET", "POST"])
@login_required
@admin_required
@csrf.exempt
def file_upload():
    if request.method == 'POST' and 'upload' in request.files:
        file = request.files['upload']
        file_name, file_ext = os.path.splitext(file.filename)
        unique_filename = str(uuid.uuid4()) + file_ext
        filename = images.save(file, name=unique_filename)
        file_url = '/_uploads/images/{}'.format(filename)
        return jsonify({"uploaded": 1, "fileName": filename, "url": file_url})
    else:
        return jsonify({"uploaded": 0, "error": {"message": "Error uploading Image."}})

initialize()
