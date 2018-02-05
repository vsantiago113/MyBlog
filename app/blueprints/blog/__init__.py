from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, g, abort
from .models import Post
from flask_login import login_required
from .forms import CreatePostForm, EditPostForm
from app import db
from app import images
from app import admin_required
import os
import uuid
from math import ceil

blog = Blueprint("blog", __name__, template_folder="templates", static_folder="static", url_prefix="/blog")


@blog.route("/", methods=("GET", "POST"))
def view_posts():
    page = 1
    per_page = 10
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        q = request.args.get('q', None)
        if q:
            results = Post.query.search(q, sort=True).paginate(page, per_page, error_out=False)
            return render_template("view_posts.html", posts=results, post_image=images, q=q)
        else:
            posts = Post.query.order_by(Post.pub_date.desc()).paginate(page, per_page, error_out=False)
            return render_template("view_posts.html", posts=posts, post_image=images, q=None)
    else:
        posts = Post.query.order_by(Post.pub_date.desc()).paginate(page, per_page, error_out=False)
        return render_template("view_posts.html", posts=posts, post_image=images, q=None)


@blog.route("/post/<path:post_id>")
def view_post(post_id):
    post = Post.query.get(post_id)
    if post:
        return render_template("view_post.html", post=post)
    else:
        abort(404)


@blog.route("/create_post", methods=("GET", "POST"))
@login_required
@admin_required
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        file_name, file_ext = os.path.splitext(form.image_name.data.filename)
        unique_filename = str(uuid.uuid4()) + file_ext
        file_name = images.save(form.image_name.data, name=unique_filename)
        post = Post(form.title.data, form.body.data, form.excerpt.data, form.pub_date.data, file_name, g.user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("blog.view_posts"))
    else:
        return render_template("create_post.html", form=form)


@blog.route("/edit_post/<path:post_id>", methods=("GET", "POST"))
@login_required
@admin_required
def edit_post(post_id):
    form = EditPostForm()
    post = Post.query.get(post_id)
    if post:
        if form.validate_on_submit():
            post = Post.query.get(post_id)
            if post.author == g.user:
                post.title = form.title.data
                post.body = form.body.data
                post.excerpt = form.excerpt.data
                if form.image_name.data:
                    if bool(post.image_name) is False:
                        pass
                    else:
                        try:
                            os.remove(images.path(post.image_name))
                        except OSError:
                            pass
                    file_name, file_ext = os.path.splitext(form.image_name.data.filename)
                    unique_filename = str(uuid.uuid4()) + file_ext
                    file_name = images.save(form.image_name.data, name=unique_filename)
                    post.image_name = file_name
                else:
                    pass
                db.session.commit()
                flash("Updated successfully!", "success")
                return redirect(url_for("blog.view_post", post_id=post.id))
            else:
                return redirect(url_for("blog.view_posts"))
        else:
            editor1 = post.body
            return render_template("edit_post.html", form=form, post=post, editor1=editor1, post_image=images)
    else:
        return redirect(url_for("blog.view_posts"))


@blog.route("/delete_post", methods=("DELETE",))
@login_required
@admin_required
def delete_post():
    if request.method == "DELETE":
        data = request.get_json()
        post_id = data['post_id']
        post = Post.query.filter_by(id=post_id)
        if post.first().author == g.user:
            if bool(post.first().image_name) is False:
                pass
            else:
                try:
                    os.remove(images.path(post.first().image_name))
                except OSError:
                    pass
            post.delete()
            db.session.commit()
            return jsonify(result="success")
        else:
            return jsonify(result="false")
    else:
        return jsonify(result="false")
