from flask import Blueprint, render_template, request, abort
from .models import ZipcodeDistance
from math import cos, radians, acos, sin, atan

zipcode_distance = Blueprint("zipcode_distance", __name__, template_folder="templates", static_folder="static",
                             url_prefix="/zipcodes")


@zipcode_distance.route("/", methods=("GET", "POST"))
def zip_codes():
return render_template('brainwallet.html')
