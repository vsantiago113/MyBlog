from flask import Blueprint, render_template, request, abort
from .models import ZipcodeDistance
from math import cos, radians, acos, sin, atan

zipcode_distance = Blueprint("zipcode_distance", __name__, template_folder="templates", static_folder="static",
                             url_prefix="/zipcodes")


@zipcode_distance.route("/", methods=("GET", "POST"))
def zip_codes():
        dist = None
        if request.method == 'GET':
            _zipcode1 = request.args.get('zipcode1', None)
            _zipcode2 = request.args.get('zipcode2', None)
            if _zipcode1 and _zipcode2:
                try:
                    _zipcode1 = int(_zipcode1)
                    _zipcode2 = int(_zipcode2)
                except ValueError:
                    abort(404)
                else:
                    zipcode1 = ZipcodeDistance.query.filter_by(zipcode=_zipcode1).first()
                    zipcode2 = ZipcodeDistance.query.filter_by(zipcode=_zipcode2).first()
                    lat1 = radians(float(zipcode1.lat))
                    long1 = radians(float(zipcode1.long))

                    lat2 = radians(float(zipcode2.lat))
                    long2 = radians(float(zipcode2.long))

                    dististance = 6367 * acos(sin(lat1) * sin(lat2) +
                                          cos(lat1) * cos(lat2) *
                                          cos(long1 - long2)
                                          )
                    dist_km = round(dististance, 2)
                    dist_miles = round(dististance * 0.62137119, 2)
                    return render_template('zipcodes.html', zipcode1=zipcode1, zipcode2=zipcode2, distance=dist_miles)
            else:
                return render_template('zipcodes.html', zipcode1=None, zipcode2=None, distance=None)
        else:
            abort(404)
