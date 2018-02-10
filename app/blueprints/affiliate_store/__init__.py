from flask import Blueprint, render_template, redirect, url_for, abort, request
from .models import AffiliateProduct
from flask_login import login_required
from .forms import AddProductForm, EditProductForm
from app import app
from app import db
from app import admin_required
import os
import uuid
import boto3

affiliate_store = Blueprint("affiliate_store", __name__, template_folder="templates", static_folder="static",
                            url_prefix="/affiliate_store")


@affiliate_store.route("/", methods=("GET", "POST"))
def view_store():
    page = 1
    per_page = 10
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        q = request.args.get('q', None)
        if q:
            results = AffiliateProduct.query.search(q, sort=True).paginate(page, per_page, error_out=False)
            return render_template("view_store.html", products=results, bucket_url=app.config.get('BUCKET_URL'), q=q)
        else:
            products = AffiliateProduct.query.order_by(AffiliateProduct.id.desc()).paginate(page, per_page, error_out=False)
            return render_template("view_store.html", products=products, bucket_url=app.config.get('BUCKET_URL'), q=None)
    else:
        products = AffiliateProduct.query.order_by(AffiliateProduct.id.desc()).paginate(page, per_page, error_out=False)
        return render_template("view_store.html", products=products, bucket_url=app.config.get('BUCKET_URL'), q=None)


@affiliate_store.route("/add_product", methods=("GET", "POST"))
@login_required
@admin_required
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        s3 = boto3.resource('s3',
                            aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY')
                            )

        file_name, file_ext = os.path.splitext(form.image_name.data.filename)
        unique_filename = app.config.get('BUCKET_FILES') + str(uuid.uuid4()) + file_ext

        s3.Bucket(app.config.get('S3_BUCKET')).put_object(Key=unique_filename,
                                                          Body=form.image_name.data,
                                                          ACL='public-read')

        product = AffiliateProduct(form.title.data, form.description.data, form.discount_price.data,
                                   form.regular_price.data, form.product_url.data, unique_filename)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for("affiliate_store.view_store"))
    else:
        return render_template("add_product.html", form=form)


@affiliate_store.route("/edit_product/<path:product_id>", methods=("GET", "POST"))
@login_required
@admin_required
def edit_product(product_id):
    form = EditProductForm()
    product = AffiliateProduct.query.get(product_id)
    if product:
        if form.validate_on_submit():
            s3 = boto3.resource('s3',
                                aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
                                aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY')
                                )

            product.title = form.title.data
            product.description = form.description.data
            product.discount_price = form.discount_price.data
            product.regular_price = form.regular_price.data
            product.product_url = form.product_url.data

            if form.image_name.data:
                s3.Bucket(app.config.get('S3_BUCKET')).delete_objects(
                    Delete={
                        'Objects': [
                            {'Key': product.image_name},
                        ],
                        'Quiet': True
                    }
                )

                file_name, file_ext = os.path.splitext(form.image_name.data.filename)
                unique_filename = app.config.get('BUCKET_IMAGES') + str(uuid.uuid4()) + file_ext
                s3.Bucket(app.config.get('S3_BUCKET')).put_object(Key=unique_filename,
                                                                  Body=form.image_name.data,
                                                                  ACL='public-read')
                product.image_name = unique_filename
            else:
                pass
            db.session.commit()
            return redirect(url_for("affiliate_store.view_store"))
        else:
            return render_template("edit_product.html", form=form, product=product,
                                   bucket_url=app.config.get('BUCKET_URL'))
    else:
        abort(404)
