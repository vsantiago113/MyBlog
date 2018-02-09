from flask import Blueprint, render_template, redirect, url_for, request
from .models import AffiliateProduct
from flask_login import login_required
from .forms import ProductForm
from app import db
from app import admin_required
import os
import uuid

affiliate_store = Blueprint("affiliate_store", __name__, template_folder="templates", static_folder="static", url_prefix="/affiliate_store")


@affiliate_store.route("/", methods=("GET", "POST"))
def view_store():
    page = 1
    per_page = 10
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        q = request.args.get('q', None)
        if q:
            results = AffiliateProduct.query.search(q, sort=True).paginate(page, per_page, error_out=False)
            return render_template("view_store.html", products=results, s3_url=app.config.get('S3_URL'), q=q)
        else:
            products = AffiliateProduct.query.order_by(AffiliateProduct.id.desc()).paginate(page, per_page, error_out=False)
            return render_template("view_store.html", products=products, s3_url=app.config.get('S3_URL'), q=None)
    else:
        products = AffiliateProduct.query.order_by(AffiliateProduct.id.desc()).paginate(page, per_page, error_out=False)
        return render_template("view_store.html", products=products, s3_url=app.config.get('S3_URL'), q=None)


@affiliate_store.route("/add_product", methods=("GET", "POST"))
@login_required
@admin_required
def add_product():
    return False
    # form = ProductForm()
    # if form.validate_on_submit():
    #     file_name, file_ext = os.path.splitext(form.image_name.data.filename)
    #     unique_filename = str(uuid.uuid4()) + file_ext
    #     file_name = images.save(form.image_name.data, name=unique_filename)
    #     product = AffiliateProduct(form.title.data, form.description.data, form.discount_price.data, form.regular_price.data, form.product_url.data, file_name)
    #     db.session.add(product)
    #     db.session.commit()
    #     return redirect(url_for("affiliate_store.view_store"))
    # else:
    #     return render_template("add_product.html", form=form)
