import requests
import biken.routing as routing
import biken.strava as strava
import biken.utils as utils
import re
import json
from .models import db, User, Itinerary
import hashlib
import random
import time
import string

"""Logged-in page routes."""
from flask import Blueprint,flash,render_template, redirect, url_for,request,jsonify
from flask_login import current_user, login_required, logout_user


# Blueprint Configuration
main_bp = Blueprint(
    'main_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@main_bp.route('/home', methods=['GET'])
@main_bp.route('/', methods=['GET'])
def home():
    query_parameters = request.args
    itineraryID = query_parameters.get('itinerary')

    if itineraryID==None :
        return render_template(
            'index.html',
            title='Biken Home page',
            current_user=current_user,
            itinerary=None
        )
    else:
        itinerary = {}
        # Load itinerary from db
        print("Look for Id:",itineraryID)
        itineraryObject = Itinerary.query.filter_by(itineraryIdentifier=itineraryID).first()

        if itineraryObject:
            itinerary["waypoints"]=utils.strToWaypoints(itineraryObject.waypoints)
            itinerary["distance"] = itineraryObject.distance
            itinerary["duration"] = itineraryObject.duration
            # itinerary=itineraryObject.waypoints

        else:
            return render_template(
                'index.html',
                title='Biken Home page',
                current_user=current_user,
                itinerary=None
            )

    # itinerary="Test"
    return render_template(
        'index.html',
        title='Biken Home page',
        current_user=current_user,
        itinerary=itinerary
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

    itineraries = Itinerary.query.filter_by(user_id=current_user.id).all()

    return render_template(
        'profile.html',
        title='Biken - Your profile',
        current_user=current_user,
        itineraries=itineraries
    )


@main_bp.route('/activities', methods=['GET'])
@login_required
def activities():
    """Logged-in User."""


    print("Expiration :",current_user.stravaTokenExpiration)
    print("Current Time :",time.time())
    activity="None"

    if current_user.stravaTokenExpiration != None:
        print(current_user.stravaTokenExpiration > time.time())
        if int(current_user.stravaTokenExpiration) > time.time():
            activity = strava.getActivity(current_user.stravaToken)


    return render_template(
        'activities.html',
        title='Biken - Your activities',
        current_user=current_user,
        activity=activity
    )





@main_bp.route("/itineraries",methods=["POST"])
@login_required
def editName():
    query_parameters = request.args
    itineraryID = query_parameters.get('itinerary')

    itinerary = Itinerary.query.filter_by(itineraryIdentifier=itineraryID).first();
    name = request.form['name']

    if itinerary.user_id==current_user.id:
        # Edit the itinerary
        if name!="" :
            if len(name)<=100:
                print("New name :",name)
                itinerary.name = name
                db.session.commit()
                return redirect(url_for("main_bp.profile"))
            else:
                flash("The name of the itinerary can't exceed 100 characters")
        else:
            flash("You can't set an empty name")
    else :
        flash("You can't edit the itinerary of another person")
    return redirect(url_for("main_bp.profile"))

@main_bp.route("/itineraries",methods=["DELETE"])
@login_required
def deleteItinerary():

    query_parameters = request.args
    itineraryID = query_parameters.get('itinerary')
    itinerary = Itinerary.query.filter_by(itineraryIdentifier=itineraryID).first();

    if itinerary.user_id==current_user.id:
        Itinerary.query.filter_by(itineraryIdentifier=itineraryID).delete()
        db.session.commit()
        print("Route deleted")
        return "Success"

        # return redirect(url_for("main_bp.profile"))

    else :
        flash("You can't delete the itinerary of another person")

    return "Success"



@main_bp.route("/save",methods=["POST"])
@login_required
def save():

    dataWaypoints = request.form['waypoints']
    distance = float(request.form['distance'])
    duration = float(request.form['duration'])

    print("Duration:",duration)
    print("Distance:",distance)

    if not dataWaypoints:
        flash('You need to create an itinerary before saving')
        return render_template(
            'index.html',
            title='Biken Home page',
            current_user=current_user,
        )

    print("Load waypoinst")
    waypoints = json.loads(dataWaypoints)
    print("Done waypoinst")

    stringCoord = ""
    for waypoint in waypoints:
        stringCoord+=str(waypoint["lat"])+","+str(waypoint["lng"])+";"

    itineraryRenderMap = utils.strToWaypoints(stringCoord)

    hash_object = hashlib.md5(stringCoord.encode())

    hashValue = hash_object.hexdigest()

    existingItinerary = Itinerary.query.filter_by(hash=hashValue,user_id=current_user.id).first()

    if not existingItinerary:
        randomString = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

        itinerary = Itinerary(
            itineraryIdentifier=randomString,
            user_id=current_user.id,
            waypoints=stringCoord,
            hash=hashValue,
            distance=distance,
            name= "Itinerary "+ randomString,
            duration=int(duration)
        )
        db.session.add(itinerary)
        db.session.commit()  #


        print("Itinerary stored")
        return "OK"
    else:
        print("Itinerary already stored")
        return "Already Stored"



@main_bp.route('/itinerary', methods=['GET'])
def api_itinerary():
    query_parameters = request.args
    coords = query_parameters.get('coords')
    render = query_parameters.get('render')

    # regular expression to extract the coords
    result = re.findall("(.+?),(.+?);(.+?),(.+?)$",coords)
    # The result come like this : [('48.9589708', '7.3350752', '49.0508729', '7.4254577')] and we need to create two dictionnary
    start = {"lat":result[0][0],"lon":result[0][1]}
    finish = {"lat":result[0][2],"lon":result[0][3]}

    # If the start/end are defined
    if start and finish:
        itinerary = routing.itinerary(start,finish,"bike")

        if render=='false':
            # return only the data
            return jsonify(itinerary)
        else :
            # Return the template
            return render_template(
                'index.html',
                title='Biken Home page',
                current_user=current_user,
                itinerary=itinerary
            )

    else :
        print("Bad request")
        val = {"error_code": "01", "error_desc": "Endpoint not defined"}
        return jsonify(val)


@main_bp.route("/elevation",methods=['POST'])
def api_elevation():
    # print('\n\n\n\n\n'+request.json+'\n\n\n\n\n')

    dataWaypoints = json.loads(request.form['waypoints'])
    profile = routing.getElevation(dataWaypoints)


    returnValue = {"profile":profile["profile"],"elevation":profile["elevation"]}

    return jsonify(returnValue)


# Route
@main_bp.route('/route', methods=['GET'])
def api_route():
    query_parameters = request.args
    startCoord = query_parameters.get('start')
    distance = query_parameters.get('distance')
    render = query_parameters.get('render')


    # regular expression to extract the coords
    result = re.findall("(.+?),(.+?)$",startCoord)
    # The result come like this : [('48.9589708', '7.3350752', '49.0508729', '7.4254577')] and we need to create two dictionnary
    start = {"lat":result[0][0],"lon":result[0][1]}


    distance = float(distance) - float(distance)*0.1
    # If the start is an adress
    if start and distance:
        route = routing.route(start,distance,"bike")

        if render=='false':
            # return only the data
            return jsonify(route)
        else :
            # Return the template
            return render_template(
                'index.html',
                title='Biken Home page',
                current_user=current_user,
                itinerary=route
            )

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
