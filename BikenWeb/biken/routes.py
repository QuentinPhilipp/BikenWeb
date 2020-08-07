import requests
import biken.routing as routing
import re
import json



"""Logged-in page routes."""
from flask import Blueprint, render_template, redirect, url_for,request,jsonify
from flask_login import current_user, login_required, logout_user


# Blueprint Configuration
main_bp = Blueprint(
    'main_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@main_bp.route('/', methods=['GET'])
def home():
    return render_template(
        'index.html',
        title='Biken Home page.',
        current_user=current_user
    )


@main_bp.route("/logout")
@login_required
def logout():
    """User log-out logic."""
    logout_user()
    return redirect(url_for('auth_bp.login'))


@main_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """Logged-in User."""
    return render_template(
        'profile.html',
        title='Biken - Your profile.',
        current_user=current_user
    )




@main_bp.route("/api/1.0/save",methods=["POST"])
def save():
    print(request.form)
    return '''OK'''


@main_bp.route('/api/1.0/itinerary', methods=['GET'])
def api_itinerary():
    query_parameters = request.args
    coords = query_parameters.get('coords')
    # regular expression to extract the coords
    result = re.findall("(.+?),(.+?);(.+?),(.+?)$",coords)
    # The result come like this : [('48.9589708', '7.3350752', '49.0508729', '7.4254577')] and we need to create two dictionnary
    start = {"lat":result[0][0],"lon":result[0][1]}
    finish = {"lat":result[0][2],"lon":result[0][3]}

    # If the start/end are defined
    if start and finish:
        itinerary = routing.itinerary(start,finish,"bike")

        val = {"type" : "itinerary","distance":itinerary['distance'],"calculationTime":itinerary['calculationTime'], "gps" : "false", "data" : {"startPos": start , "finishPos": finish, "waypoints":itinerary["waypoints"]}}

        return jsonify(val)

    else :
        print("Bad request")
        val = {"error_code": "01", "error_desc": "Endpoint not defined"}
        return jsonify(val)

# Route
@main_bp.route('/api/1.0/route', methods=['GET'])
def api_route():
    query_parameters = request.args
    startCoord = query_parameters.get('start')
    distance = query_parameters.get('distance')

    # regular expression to extract the coords
    result = re.findall("(.+?),(.+?)$",startCoord)
    # The result come like this : [('48.9589708', '7.3350752', '49.0508729', '7.4254577')] and we need to create two dictionnary
    start = {"lat":result[0][0],"lon":result[0][1]}


    distance = float(distance) - float(distance)*0.1
    # If the start is an adress
    if start and distance:
        print("Route with distance")
        route = routing.route(start,distance)
        # print("Route :",route)

        startPosition= route["waypoints"][0]
        val = {"type" : "route","distance":route["distance"],"calculationTime":route['calculationTime'], "gps" : "false", "data" : {"startName": "test", "startPos": startPosition, "waypoints":route["waypoints"]}}

        return jsonify(val)

    else :
        print("Bad request")
        val = {"error_code": "01", "error_desc": "Endpoint not defined"}
        return jsonify(val)

#
# @app.route('/profile', methods=['GET'])
# @login_required
# def profile():
#     return render_template("profile.html")
#
# @app.route('/activities', methods=['GET'])
# @login_required
# def activities():
#     return render_template("activities.html")
#
# @app.route('/settings', methods=['GET'])
# @login_required
# def preferences():
#     return render_template("preferences.html")
#
#
# @login_manager.unauthorized_handler
# def unauthorized_callback():
#     return redirect('/login?next=' + request.path)
#
