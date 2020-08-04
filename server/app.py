import requests
from flask import Flask, redirect, request, jsonify,render_template ,url_for
from flask_cors import CORS
import time
import random
from math import sin,cos,radians,pi
import re
import json
import os
import sqlite3
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient

# Load env variables
from dotenv import load_dotenv
load_dotenv()


# Internal imports
import utils
import routing
from db import init_db_command
from user import User


# Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)



app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
app.config["DEBUG"] = True
CORS(app)


# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)


# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")
# @app.route("/")
# def index():
#     if current_user.is_authenticated:
#         return (
#             "<p>Hello, {}! You're logged in! Email: {}</p>"
#             "<div><p>Google Profile Picture:</p>"
#             '<img src="{}" alt="Google profile pic"></img></div>'
#             '<a class="button" href="/logout">Logout</a>'.format(
#                 current_user.name, current_user.email, current_user.profile_pic
#             )
#         )
#     else:
#         return '<a class="button" href="/login">Google Login</a>'

@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google
    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route('/api/1.0/itinerary', methods=['GET'])
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
@app.route('/api/1.0/route', methods=['GET'])
def api_route():
    query_parameters = request.args
    startCoord = query_parameters.get('start')
    distance = query_parameters.get('distance')

    # regular expression to extract the coords
    result = re.findall("(.+?),(.+?)$",startCoord)
    # The result come like this : [('48.9589708', '7.3350752', '49.0508729', '7.4254577')] and we need to create two dictionnary
    start = {"lat":result[0][0],"lon":result[0][1]}

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



def geocode(location):
    # This function use nominatim to get the GPS point of an address
    endpoint = "https://nominatim.openstreetmap.org/search/"
    query = endpoint+location+"?format=json&limit=1"
    response = requests.get(query).json()[0]
    return {"lat": response["lat"], "lon": response["lon"]}

def extractGPS(gpsPoint):
    # Extract latitude and longitude from the request and return in the good format
    position = gpsPoint.split(",")
    return {"lat": position[0], "lon": position[1]}


def generateCircle(start,distance,points):
    # Generate a circle for the route
    angleBetween = 360/points
    radius = float(distance)/(2*pi)
    waypointList = []
    isDirectionOk = False
    nbRetry = 20   #Only allow 20 retry

    while (isDirectionOk==False and nbRetry>0):
        nbRetry-=1
        print("Try n",nbRetry)
        waypointList = []   #clear the list
        isDirectionOk = True  #reset for another  test

        maxValue = 360;
        direction = int(random.random()*maxValue)
        print("direction : ", direction)

        startAngle = direction-180;
        #set startAngle (180 - angle of direction)
        #un depart vers l'est, implique un point de depart a gauche du cercle
        #on commence donc par ce point

        centerPoint = addKmWithAngle(radius,direction,start)

        for i in range(points):
            print("Angle :",startAngle+angleBetween*i)
            coord = addKmWithAngle(radius,startAngle+angleBetween*i,centerPoint)
            result = creator.getClosestNode(coord["lat"],coord["lon"])

            if result[1]>3 :
                isDirectionOk=False
            else :
                coords = {}
                coords["lat"] = result[0].latitude
                coords["lon"] = result[0].longitude

                waypointList.append(coords)


    coord = addKmWithAngle(radius,startAngle,centerPoint)
    waypointList.append(coord)            #adding startNode to close the route

    return waypointList



def addKmWithAngle(radius, direction, startPos):
    #calculate the km to add to latitude and longitude based on the angle
    addLat = sin(radians(direction))*radius
    addLon = cos(radians(direction))*radius

    returnValues = {}
    returnValues["lat"] = utils.addKmToLatitude(float(startPos["lat"]),addLat)
    returnValues["lon"] = utils.addKmToLongitude(float(startPos["lat"]),float(startPos["lon"]),addLon)

    return returnValues


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5000,ssl_context="adhoc")
