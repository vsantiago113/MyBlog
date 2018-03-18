from flask import Blueprint, render_template, request, abort
from .models import ZipcodeDistance
from math import cos, radians, acos, sin, atan
import requests

zipcode_distance = Blueprint("zipcode_distance", __name__, template_folder="templates", static_folder="static",
                             url_prefix="/zipcodes")


@zipcode_distance.route("/", methods=("GET", "POST"))
def zip_codes():
        error = None
        if request.method == 'GET':
            _zipcode1 = request.args.get('zipcode1', None)
            _zipcode2 = request.args.get('zipcode2', None)
            if _zipcode1 and _zipcode2:
                try:
                    int(_zipcode1)
                    int(_zipcode2)
                    _zipcode1 = _zipcode1
                    _zipcode2 = _zipcode2
                except ValueError:
                    abort(404)
                else:
                    # Zip Code 1 Data
                    url = 'http://maps.googleapis.com/maps/api/geocode/json'
                    parameters = dict(address=_zipcode1)
                    response = requests.get(url=url, params=parameters)
                    data = response.json()
                    zipcode1_status = data.get('status', 'None').upper()
                    if data.get('status', 'None').upper() == 'OK':
                        if len(data.get('results')[0].get('address_components')) == 5:
                            zipcode1 = dict(status=data.get('status'),
                                            zipcode=data.get('results')[0].get('address_components')[0].get('long_name'),
                                            city=data.get('results')[0].get('address_components')[1].get('long_name'),
                                            county=data.get('results')[0].get('address_components')[2].get('long_name'),
                                            state=data.get('results')[0].get('address_components')[3].get('short_name'),
                                            country=data.get('results')[0].get('address_components')[4].get('long_name'),
                                            lat=data.get('results')[0].get('geometry').get('location').get('lat'),
                                            lng=data.get('results')[0].get('geometry').get('location').get('lng'),
                                            localities=data.get('results')[0].get('postcode_localities'),
                                            address=data.get('results')[0].get('formatted_address')
                                            )
                        elif len(data.get('results')[0].get('address_components')) == 4:
                            zipcode1 = dict(status=data.get('status'),
                                            zipcode=data.get('results')[0].get('address_components')[0].get('long_name'),
                                            city=data.get('results')[0].get('address_components')[1].get('long_name'),
                                            state=data.get('results')[0].get('address_components')[2].get('short_name'),
                                            country=data.get('results')[0].get('address_components')[3].get('long_name'),
                                            lat=data.get('results')[0].get('geometry').get('location').get('lat'),
                                            lng=data.get('results')[0].get('geometry').get('location').get('lng'),
                                            localities=data.get('results')[0].get('postcode_localities'),
                                            address=data.get('results')[0].get('formatted_address')
                                            )
                        else:
                            error = 'Error getting Geolocation data.'
                            zipcode1 = None
                    else:
                        error = 'Error getting Geolocation data.'
                        zipcode1 = None

                    # Zip Code 2 Data
                    url = 'http://maps.googleapis.com/maps/api/geocode/json'
                    parameters = dict(address=_zipcode2)
                    response = None
                    data = None
                    del response
                    del data
                    response = requests.get(url=url, params=parameters)
                    data = response.json()
                    zipcode2_status = data.get('status', 'None').upper()
                    if data.get('status', 'None').upper() == 'OK':
                        if len(data.get('results')[0].get('address_components')) == 5:
                            zipcode2 = dict(status=data.get('status'),
                                            zipcode=data.get('results')[0].get('address_components')[0].get('long_name'),
                                            city=data.get('results')[0].get('address_components')[1].get('long_name'),
                                            county=data.get('results')[0].get('address_components')[2].get('long_name'),
                                            state=data.get('results')[0].get('address_components')[3].get('short_name'),
                                            country=data.get('results')[0].get('address_components')[4].get('long_name'),
                                            lat=data.get('results')[0].get('geometry').get('location').get('lat'),
                                            lng=data.get('results')[0].get('geometry').get('location').get('lng'),
                                            localities=data.get('results')[0].get('postcode_localities'),
                                            address=data.get('results')[0].get('formatted_address')
                                            )
                        elif len(data.get('results')[0].get('address_components')) == 4:
                            zipcode2 = dict(status=data.get('status'),
                                            zipcode=data.get('results')[0].get('address_components')[0].get('long_name'),
                                            city=data.get('results')[0].get('address_components')[1].get('long_name'),
                                            state=data.get('results')[0].get('address_components')[2].get('short_name'),
                                            country=data.get('results')[0].get('address_components')[3].get('long_name'),
                                            lat=data.get('results')[0].get('geometry').get('location').get('lat'),
                                            lng=data.get('results')[0].get('geometry').get('location').get('lng'),
                                            localities=data.get('results')[0].get('postcode_localities'),
                                            address=data.get('results')[0].get('formatted_address')
                                            )
                        else:
                            error = 'Error getting Geolocation data.'
                            zipcode2 = None
                    else:
                        error = 'Error getting Geolocation data.'
                        zipcode2 = None

                    if zipcode1 and zipcode2:
                        lat1 = radians(float(zipcode1['lat']))
                        long1 = radians(float(zipcode1['lng']))

                        lat2 = radians(float(zipcode2['lat']))
                        long2 = radians(float(zipcode2['lng']))

                        dististance = 6367 * acos(sin(lat1) * sin(lat2) +
                                              cos(lat1) * cos(lat2) *
                                              cos(long1 - long2)
                                              )
                        dist_km = round(dististance, 2)
                        dist_miles = round(dististance * 0.62137119, 2)
                        return render_template('zipcodes.html', zipcode1=zipcode1, zipcode2=zipcode2, distance=dist_miles, error=error)
                    else:
                        if zipcode1_status == 'OK':
                            pass
                        else:
                            error = zipcode1_status
                        if zipcode2_status == 'OK':
                            pass
                        else:
                            error = zipcode2_status
                        return render_template('zipcodes.html', zipcode1=None, zipcode2=None,
                                               distance=None, error=error)
            else:
                return render_template('zipcodes.html', zipcode1=None, zipcode2=None, distance=None, error=error)
        else:
            abort(404)
