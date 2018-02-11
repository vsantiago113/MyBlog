from flask import redirect, url_for, render_template, flash, g, session, request, jsonify
from flask_login import login_required, login_user, logout_user
from functools import wraps
from flask_bcrypt import generate_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
from app import app
from app import login_manager
from app import db
from app.forms import LoginForm, RegistrationForm, ChangeProfileImageForm, ChangePasswordForm, EditProfileForm
from app.models import User, followers
from app.blueprints.blog import blog
from app.blueprints.blog.models import Post
from app.blueprints.affiliate_store import affiliate_store
from app.blueprints.affiliate_store.models import AffiliateProduct
from app import csrf
from app import admin_required, ssl_required
from app import recaptcha
import boto3

app.register_blueprint(blog)
app.register_blueprint(affiliate_store)


# @app.before_first_request
# def before_first_request(f):
#     db.create_all()
#     if User.query.get(1):
#         pass
#     else:
#         admin = User("admin", "admin@example.com", "password", True)
#         db.session.add(admin)
#         db.session.commit()


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
    products = AffiliateProduct.query.order_by(AffiliateProduct.id.desc()).limit(4)
    return render_template('index.html', posts=posts, products=products, user=user,
                           bucket_url=app.config.get('BUCKET_URL'),
                           default_photo=app.config.get('DEFAULT_PHOTO'))


@app.route("/login", methods=("GET", "POST"))
@ssl_required
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
@ssl_required
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        if recaptcha.verify():
            user = User(form.username.data, form.email.data, form.password.data, False)
            db.session.add(user)
            db.session.commit()
            flash("your account has been created successfully you can now log in.", "success")
        else:
            flash('The Captcha is invalid, please try again!', 'warning')
            return render_template("registration.html", form=form)
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
    return render_template("profile_templates/user_profile.html", user=user, bucket_url=app.config.get('BUCKET_URL'),
                           default_photo=app.config.get('DEFAULT_PHOTO'))


@app.route("/update_image", methods=["GET", "POST"])
@login_required
def change_profile_image():
    form = ChangeProfileImageForm()
    if form.validate_on_submit():

        s3 = boto3.resource('s3',
                            aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY')
                            )

        if g.user.image_name:
            s3.Bucket(app.config.get('S3_BUCKET')).delete_objects(
                Delete={
                    'Objects': [
                        {'Key': g.user.image_name},
                    ],
                    'Quiet': True
                }
            )
        else:
            pass

        file_name, file_ext = os.path.splitext(form.image_name.data.filename)
        unique_filename = app.config.get('BUCKET_PHOTOS') + str(uuid.uuid4()) + file_ext

        s3.Bucket(app.config.get('S3_BUCKET')).put_object(Key=unique_filename,
                                                          Body=form.image_name.data,
                                                          ACL='public-read')

        g.user.image_name = unique_filename
        db.session.commit()

        return redirect(url_for("user_profile", user_id=g.user.id))
    return render_template("profile_templates/change_profile_image.html", form=form,
                           bucket_url=app.config.get('BUCKET_URL'),
                           default_photo=app.config.get('DEFAULT_PHOTO'))


@app.route("/delete_profile_image")
@login_required
def delete_profile_image():
    if g.user.image_name:
        s3 = boto3.resource('s3',
                            aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY')
                            )
        s3.Bucket(app.config.get('S3_BUCKET')).delete_objects(
            Delete={
                'Objects': [
                    {'Key': g.user.image_name},
                ],
                'Quiet': True
            }
        )
        g.user.image_name = ''
        db.session.commit()
    else:
        pass
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
    s3 = boto3.resource('s3',
                        aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
                        aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY')
                        )
    bucket = s3.Bucket(app.config.get('S3_BUCKET'))
    file_list = []
    for key in bucket.objects.all():
        if key.key.endswith('/'):
            pass
        else:
            file_list.append(key.key)
    return render_template('file_browser.html', bucket_url=app.config.get('BUCKET_URL'), bucket_keys=file_list)


@app.route("/file_upload", methods=["GET", "POST"])
@login_required
@admin_required
@csrf.exempt
def file_upload():
    if request.method == 'POST' and 'upload' in request.files:
        s3 = boto3.resource('s3',
                            aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY')
                            )

        file = request.files['upload']
        file_name, file_ext = os.path.splitext(file.filename)
        unique_filename = app.config.get('BUCKET_FILES') + str(uuid.uuid4()) + file_ext
        file_url = app.config.get('BUCKET_URL') + unique_filename

        s3.Bucket(app.config.get('S3_BUCKET')).put_object(Key=unique_filename,
                                                          Body=file,
                                                          ACL='public-read')

        return jsonify({"uploaded": 1, "fileName": unique_filename, "url": file_url})
    else:
        return jsonify({"uploaded": 0, "error": {"message": "Error uploading Image."}})

#initialize()
