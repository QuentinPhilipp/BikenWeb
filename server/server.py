import flask
import requests
from flask import request, jsonify,render_template
from flask_cors import CORS
import time
import random
from math import sin,cos,radians,pi
import utils
import routing
import re


app = flask.Flask(__name__)
app.config["DEBUG"] = True
CORS(app)


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")


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
        print("Route :",route)

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

app.run(host='127.0.0.1',port=6001)
