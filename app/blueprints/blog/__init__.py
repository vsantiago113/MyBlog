from flask import Blueprint, render_template, redirect, url_for, request, jsonify, g, abort
from .models import Post, Comment, Reply
from flask_login import login_required
from .forms import CreatePostForm, EditPostForm, CommentForm, ReplyForm
from app import app
from app import db
from app import admin_required
import os
import uuid
import boto3
from datetime import datetime

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
            return render_template("view_posts.html", posts=results, bucket_url=app.config.get('BUCKET_URL'), q=q)
        else:
            posts = Post.query.order_by(Post.pub_date.desc()).paginate(page, per_page, error_out=False)
            return render_template("view_posts.html", posts=posts, bucket_url=app.config.get('BUCKET_URL'), q=None)
    else:
        posts = Post.query.order_by(Post.pub_date.desc()).paginate(page, per_page, error_out=False)
        return render_template("view_posts.html", posts=posts, bucket_url=app.config.get('BUCKET_URL'), q=None)


@blog.route("/post/<path:post_id>")
def view_post(post_id):
    post = Post.query.get(post_id)
    comment_form = CommentForm()
    reply_form = ReplyForm()
    if post:
        return render_template("view_post.html", post=post, bucket_url=app.config.get('BUCKET_URL'),
                               comment_form=comment_form, reply_form=reply_form, todays_date=datetime.now())
    else:
        abort(404)


@blog.route("/create_post", methods=("GET", "POST"))
@login_required
@admin_required
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        s3 = boto3.resource('s3',
                            aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY')
                            )

        file_name, file_ext = os.path.splitext(form.image_name.data.filename)
        unique_filename = app.config.get('BUCKET_IMAGES') + str(uuid.uuid4()) + file_ext
        s3.Bucket(app.config.get('S3_BUCKET')).put_object(Key=unique_filename,
                                                          Body=form.image_name.data,
                                                          ACL='public-read')

        post = Post(form.title.data, form.body.data, form.excerpt.data, form.pub_date.data, unique_filename, g.user)
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
            if post.author == g.user:
                s3 = boto3.resource('s3',
                                    aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
                                    aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY')
                                    )

                post.title = form.title.data
                post.body = form.body.data
                post.excerpt = form.excerpt.data
                if form.image_name.data:
                    s3.Bucket(app.config.get('S3_BUCKET')).delete_objects(
                        Delete={
                            'Objects': [
                                {'Key': post.image_name},
                            ],
                            'Quiet': True
                        }
                    )

                    file_name, file_ext = os.path.splitext(form.image_name.data.filename)
                    unique_filename = app.config.get('BUCKET_IMAGES') + str(uuid.uuid4()) + file_ext
                    s3.Bucket(app.config.get('S3_BUCKET')).put_object(Key=unique_filename,
                                                                      Body=form.image_name.data,
                                                                      ACL='public-read')
                    post.image_name = unique_filename
                else:
                    pass
                db.session.commit()
                return redirect(url_for("blog.view_post", post_id=post.id))
            else:
                return redirect(url_for("blog.view_posts"))
        else:
            editor1 = post.body
            return render_template("edit_post.html", form=form, post=post, editor1=editor1,
                                   bucket_url=app.config.get('BUCKET_URL'))
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
            s3 = boto3.resource('s3',
                                aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
                                aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY')
                                )
            s3.Bucket(app.config.get('S3_BUCKET')).delete_objects(
                Delete={
                    'Objects': [
                        {'Key': post.first().image_name},
                    ],
                    'Quiet': True
                }
            )
            post.delete()
            db.session.commit()
            return jsonify(result="success")
        else:
            return jsonify(result="false")
    else:
        return jsonify(result="false")


@blog.route('/leave_comment/<path:post_id>', methods=('GET', 'POST'))
@login_required
def leave_comment(post_id):
    post = Post.query.get(post_id)
    if post:
        form = CommentForm()
        if form.validate_on_submit():
            if form.comment.data:
                comment = Comment(g.user, form.comment.data, post)
                db.session.add(comment)
                db.session.commit()
            else:
                pass
            return redirect(url_for("blog.view_post", post_id=post.id))
        else:
            return redirect(url_for("blog.view_post", post_id=post.id))
    else:
        abort(404)


@blog.route('/leave_reply/<path:post_id>', methods=('POST',))
@login_required
def leave_reply(post_id):
    form = ReplyForm()
    if form.validate_on_submit():
        comment = Comment.query.get(int(form.comment_id.data))
        if comment:
            reply = Reply(g.user, form.reply.data, comment)
            db.session.add(reply)
            db.session.commit()
            return redirect(url_for("blog.view_post", post_id=post_id))
        else:
            abort(404)
    else:
        return redirect(url_for("blog.view_post", post_id=post_id))


@blog.route('/likes', methods=('POST',))
@login_required
def likes():
    data = request.get_json()
    post_id = data.get('post_id', None)
    comment_id = data.get('comment_id', None)
    reply_id = data.get('reply_id', None)
    if not comment_id and not reply_id:
        abort(404)
    else:
        pass
    if comment_id:
        comment = Comment.query.get(int(comment_id))
    else:
        comment = None
    if reply_id:
        reply = Reply.query.get(int(reply_id))
    else:
        reply = None

    if post_id:
        if comment:
            _comment = CommentLike(g.user, comment)
            db.session.add(_comment)
            #db.session.commit()
            return redirect(url_for("blog.view_post", post_id=post_id))
        elif reply:
            _reply = ReplyLike(g.user, reply)
            db.session.add(_reply)
            #db.session.commit()
            return redirect(url_for("blog.view_post", post_id=post_id))
        else:
            abort(404)
    else:
        abort(404)
