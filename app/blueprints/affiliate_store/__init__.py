from flask import Blueprint, render_template, redirect, url_for
from .models import AffiliateProduct
from flask_login import login_required
from .forms import ProductForm
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
    return 'Needs to be completed, Come back later!'
    # page = 1
    # per_page = 10
    # if request.method == 'GET':
    #     page = request.args.get('page', 1, type=int)
    #     q = request.args.get('q', None)
    #     if q:
    #         results = AffiliateProduct.query.search(q, sort=True).paginate(page, per_page, error_out=False)
    #         return render_template("view_store.html", products=results, s3_url=app.config.get('S3_URL'), q=q)
    #     else:
    #         products = AffiliateProduct.query.order_by(AffiliateProduct.id.desc()).paginate(page, per_page, error_out=False)
    #         return render_template("view_store.html", products=products, s3_url=app.config.get('S3_URL'), q=None)
    # else:
    #     products = AffiliateProduct.query.order_by(AffiliateProduct.id.desc()).paginate(page, per_page, error_out=False)
    #     return render_template("view_store.html", products=products, s3_url=app.config.get('S3_URL'), q=None)


@affiliate_store.route("/add_product", methods=("GET", "POST"))
@login_required
@admin_required
def add_product():
    form = ProductForm()
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
