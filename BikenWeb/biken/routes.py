import requests
import biken.routing as routing
import biken.strava as strava
import biken.utils as utils
import biken.gpxEncoder as gpxEncoder
import biken.data as dataManager
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

import os
from dotenv import load_dotenv
load_dotenv()
STRAVA_REDIRECT_LINK = os.environ.get("STRAVA_REDIRECT_LINK", None)

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
            itinerary["polyline"] = itineraryObject.polyline
            itinerary["distance"] = itineraryObject.distance
            itinerary["duration"] = itineraryObject.duration
            itinerary["uniqueId"] = itineraryObject.itineraryIdentifier


            startWaypoint = {"lat":itineraryObject.startCoordLat,"lon":itineraryObject.startCoordLon}
            endWaypoint = {"lat":itineraryObject.endCoordLat,"lon":itineraryObject.endCoordLon}

            if utils.distanceBetweenPoints(startWaypoint,endWaypoint)<=1000:
                itinerary["type"] = "round"
            else :
                itinerary["type"] = "oneway"

            return render_template(
                'index.html',
                title='Biken Home page',
                current_user=current_user,
                itinerary=itinerary
            )
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





# Plan an itinerary
@main_bp.route('/plan/itinerary', methods=['GET'])
def planItinerary():
    query_parameters = request.args
    startPlace = query_parameters.get('start')
    destinationPlace = query_parameters.get('destination')
    distance = query_parameters.get('distance')
    routeType = query_parameters.get('type')
    render = query_parameters.get('render')

    if routeType=="oneway":
        gpsStart=routing.getGPSLocation(startPlace)
        gpsDestination=routing.getGPSLocation(destinationPlace)
        if gpsStart and gpsDestination:
            itinerary = routing.itinerary(gpsStart,gpsDestination)

            # Store itinerary in DB
            itineraryId = dataManager.storeItinerary(itinerary)
            itinerary["uniqueId"]=itineraryId
 
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
            val = {"error": "Bad request", "error_desc": "Start and/or destination not found"}
            return jsonify(val)


    elif routeType=="round":
        # Remove 10% of distance
        distance = float(distance) - float(distance)*0.1

        gpsStart=routing.getGPSLocation(startPlace)
        # If the start is an adress
        if gpsStart and distance:
            route = routing.route(gpsStart,distance)
            
            # Store itinerary in DB
            itineraryId = dataManager.storeItinerary(route)
            route["uniqueId"]=itineraryId
 
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
            val = {"error": "Bad request", "error_desc": "Start and/or distance not found"}
            return jsonify(val)

    else :
        val = {"error": "Bad request", "error_desc": "RouteType doesn't correspond to any of the valid entry (oneway or roundtrip)"}
        return jsonify(val)





@main_bp.route("/save",methods=["POST"])
def save():
    if current_user.is_authenticated:
        req = request.get_json()
        itineraryId = req['itineraryID']

        dataManager.bindUserToItinerary(itineraryId,current_user.userId)

        returnValue = {"success":True}
        return jsonify(returnValue)
    else :
        returnValue = {"error":"notLoggedIn"}
        flash('You must be logged in to save an itinerary.')
        return jsonify(returnValue) 


@main_bp.route("/plan/elevation",methods=['GET'])
def api_elevation():
    query_parameters = request.args
    itineraryId = query_parameters.get('id')
    profile = routing.getElevation(itineraryId)

    returnValue = {"profile":profile["profile"],"elevation":profile["elevation"]}

    return jsonify(returnValue)



@main_bp.route("/convertToItinerary",methods=["POST"])
def convertToItinerary():
    req = request.get_json()
    polyline = req['polyline']
    distance = req['distance']
    time = req['time']
    gpx = req["gpx"]
    itineraryName = req["name"]

    if gpx:
        # Convert the itinerary
        itineraryID = routing.convertStravaItinerary(polyline,distance,time)

        itinerary = Itinerary.query.filter_by(itineraryIdentifier=itineraryID).first();
        if itinerary:
            filename = gpxEncoder.createGPXfile(itinerary,itineraryName)
            if filename != "Error":
                val = {"filename": filename, "success": True}
                return jsonify(val)
    else :
        # Return only the itinerary Id to render in the route editor
        itineraryID = routing.convertStravaItinerary(polyline,distance,time)

        returnValue = {"itineraryID":itineraryID}
        return jsonify(returnValue)



@main_bp.route("/getGPX",methods=["GET"])
def getGpx():
    query_parameters = request.args
    itineraryID = query_parameters.get('itinerary')
    itineraryName = query_parameters.get('name')

    itinerary = Itinerary.query.filter_by(itineraryIdentifier=itineraryID).first();

    if itinerary:
        filename = gpxEncoder.createGPXfile(itinerary,itineraryName)
      
        if filename != "Error":
            val = {"filename": filename, "success": True}
            return jsonify(val)
    else:
        val = {"success": False}
        return jsonify(val)

    val = {"success": False}
    return jsonify(val)


@main_bp.route("/logout")
@login_required
def logout():
    """User log-out logic."""
    # log out user from Google or simple login system
    logout_user()

    # Log out user from Strava
    # Force expiration of token
    current_user.stravaTokenExpiration=str(time.time()-1)
    db.session.commit()  # Store data

    return redirect(url_for('main_bp.home'))


@main_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """Logged-in User."""

    itineraries = dataManager.getAllItineraryFromUser(current_user.userId)

    return render_template(
        'profile.html',
        title='Biken - Your profile',
        current_user=current_user,
        itineraries=itineraries
    )

@main_bp.route('/features', methods=['GET'])
def features():
    """Logged-in User."""


    return render_template(
        'features.html',
        title='Biken - Features'
    )





@main_bp.route('/activities', methods=['GET'])
@login_required
def activities():
    """Logged-in User."""


    print("Expiration :",current_user.stravaTokenExpiration)
    print("Current Time :",time.time())
    activities = []

    if current_user.stravaTokenExpiration != None and current_user.stravaTokenExpiration != "":
        if int(current_user.stravaTokenExpiration) > time.time():
            print("Token not expired")

            rawActivities = strava.getActivity(current_user.stravaToken,5)
            for activity in rawActivities:
                if activity["type"]=="Ride":
                    activitySummary = {}
                    activitySummary["distance"] = round(activity["distance"]/1000, 2)
                    # transform "/" into "//"
                    polyline = re.escape(activity["map"]["summary_polyline"])

                    activitySummary["polyline"] = polyline
                    activitySummary["elevation"] = activity["total_elevation_gain"]

                    # moving_time in seconds, transform in minutes
                    activitySummary["time"] = activity["moving_time"]//60
                    activitySummary["id"] = activity["id"]
                    activitySummary["name"] = activity["name"]

                    # try:
                    #     # Request detail for the itinerary
                    #     detailedActivity = strava.getDetailedActivity(current_user.stravaToken,activity["id"])
                    #     activitySummary["polyline"] = detailedActivity["map"]["summary_polyline"]
                    #
                    # except Exception as e:
                    #     print("Error fetching details")

                    activities.append(activitySummary)


        else :
            print("Token expired")

    return render_template(
        'activities.html',
        title='Biken - Your activities',
        current_user=current_user,
        activities=activities,
        redirect_link=STRAVA_REDIRECT_LINK
    )





@main_bp.route("/itineraries",methods=["POST"])
@login_required
def editName():
    query_parameters = request.args
    itineraryID = query_parameters.get('itinerary')
    name = request.form['name']


    result = dataManager.renameItinerary(itineraryID,current_user.userId,name)
    if result :
        return redirect(url_for('main_bp.profile'))
    else : return "Fail"



@main_bp.route("/itineraries",methods=["DELETE"])
@login_required
def deleteItinerary():

    query_parameters = request.args
    itineraryID = query_parameters.get('itinerary')

    result = dataManager.removeLinkUserItinerary(itineraryID,current_user.userId)
    if result :
        return "OK"
    else : 
        return "Fail"