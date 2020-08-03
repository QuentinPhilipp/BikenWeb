import flask
import requests
from flask import request, jsonify,render_template
from flask_cors import CORS
import sqlite3
import databaseManager
import itinaryCreator
from threading import Thread
import time
import copy
import queue
import random
from math import sin,cos,radians,pi
import utils
import routing

app = flask.Flask(__name__)
app.config["DEBUG"] = False
CORS(app)


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")


@app.route('/api/1.0/itinerary', methods=['GET'])
def api_itinerary():
    query_parameters = request.args
    start = query_parameters.get('start')
    finish = query_parameters.get('finish')

    print(start)
    print(finish)

    # If the start/end is an adress
    if start and finish:
        print("Itinerary with address")

        startGeolocalisationTime = time.time();
        startPosition = geocode(start)
        finishPosition = geocode(finish)
        geolocalisationTime = time.time()-startGeolocalisationTime;

        # itinerary = creator.getItinerary(startPosition,finishPosition)
        itinerary = routing.route(startPosition,finishPosition,"bike")


        itinerary['geolocalisationTime']=geolocalisationTime;

        print("Time : ",itinerary['calculationTime'])
        # startPosition={"lat": waypointList[0][0], "lon": waypointList[0][1]}
        # finishPosition={"lat": waypointList[-1][0], "lon": waypointList[-1][1]}

        val = {"type" : "itinerary","distance":itinerary['distance'],"geolocalisationTime":itinerary['geolocalisationTime'],"calculationTime":itinerary['calculationTime'], "gps" : "false", "data" : {"startName": start, "startPos": startPosition , "finishName": finish, "finishPos": finishPosition, "waypoints":itinerary["waypoints"]}}
        print("Returned")

        # reset all the nodes in another thread to return the data instantly
        # thread_a = Compute()
        # thread_a.start()

        return jsonify(val)

    else :
        print("Bad request")
        val = {"error_code": "01", "error_desc": "Endpoint not defined"}
        return jsonify(val)


# Route
@app.route('/api/1.0/route', methods=['GET'])
def api_route():
    query_parameters = request.args
    start = query_parameters.get('start')
    distance = query_parameters.get('distance')

    # If the start is an adress
    if start and distance:
        print("Route with distance")
        startGeolocalisationTime = time.time();

        startPosition = geocode(start)


        points=3
        pointList=generateCircle(startPosition,distance,points)

        waypointList=[]

        for waypoint in pointList:
            waypointList.append([waypoint["lat"],waypoint["lon"]])


        val = {"type" : "route","distance":0,"geolocalisationTime":0,"calculationTime":0, "gps" : "false", "data" : {"startName": "test", "startPos": startPosition , "finishName": "test", "finishPos": startPosition, "waypoints":waypointList}}

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
