import flask
import requests
from flask import request, jsonify
from flask_cors import CORS
import sqlite3
import databaseManager

app = flask.Flask(__name__)
app.config["DEBUG"] = True
CORS(app)

@app.route('/api/docs', methods=['GET'])
def home():
    return '''<h1>Biken Web API</h1>
<p>Follow the project on <a href="https://github.com/QuentinPhilipp/BikenAPI">Github</a></p>
<hr>
<h3>If start and finish is an address</h3>
<p>Endpoint : http://127.0.0.1:5000/api/1.0/itinerary?start={startPoint}&finish={finishPoint} WIP
<p>Endpoint : http://127.0.0.1:5000/api/1.0/route?start={startPoint}&distance={km} WIP
<hr>
<h3>If start and finish are latitude and longitude</h3>
<p>Endpoint : http://127.0.0.1:5000/api/1.0/itinerary?startPos=48.577043,7.759002&finishPos={finishPoint} WIP
<p>Endpoint : http://127.0.0.1:5000/api/1.0/route?startPos=48.577043,7.759002&distance={km} WIP

'''

@app.route('/api/1.0/itinerary', methods=['GET'])
def api_itinerary():
    query_parameters = request.args
    start = query_parameters.get('start')
    finish = query_parameters.get('finish')
    startPos = query_parameters.get('startPos')
    finishPos = query_parameters.get('finishPos')

    # If the start/end is an adress
    if start and finish:
        print("Itinerary with address")
        startPosition = geocode(start)
        finishPosition = geocode(finish)
        val = {"type" : "itinerary", "gps" : "false", "data" : {"startName": start, "startPos": startPosition, "finishName": finish, "finishPos": finishPosition, "waypoint":[]}}
        return jsonify(val)

    # if the start/end is an GPS point
    elif startPos and finishPos:
        print("Itinerary with GPS points")
        startPosition = extractGPS(startPos)
        finishPosition = extractGPS(finishPos)
        val = {"type" : "itinerary", "gps" : "true", "data" : {"startName": start, "startPos": startPosition, "finishName": finish, "finishPos": finishPosition, "waypoint":[]}}
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
    startPos = query_parameters.get('startPos')
    distance = query_parameters.get('distance')

    # If the start is an adress
    if start and distance:
        print("Route with address")
        startPosition = geocode(start)
        val = {"type" : "route", "gps" : "false", "data" : {"startName": start, "startPos": startPosition, "distance": distance, "waypoint":[]}}
        return jsonify(val)

    # If the start is a GPS point
    elif startPos and distance:
        print("Route with GPS points")
        startPosition = extractGPS(startPos)
        val = {"type" : "route", "gps" : "true", "data" : {"startName": start, "startPos": startPosition, "distance": distance, "waypoint":[]}}
        return jsonify(val)
    else :
        print("Bad request")
        val = {"error_code": "01", "error_desc": "Endpoint not defined"}
        return jsonify(val)


@app.route('/api/1.0/debugDownload', methods=['GET'])
def sendDownloadSquares():
    dbManager = databaseManager.DatabaseManager()
    values = dbManager.getDownloadPoints()
    val = {"status_code": "200", "data": values}
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

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

app.run()
