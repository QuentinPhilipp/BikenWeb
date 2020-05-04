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


app = flask.Flask(__name__)
app.config["DEBUG"] = False
CORS(app)

creator = itinaryCreator.itineraryCreator(48.467466, -4.649883)
# creator2 = itinaryCreator.itineraryCreator(48.467466, -4.649883)
# creator3 = itinaryCreator.itineraryCreator(48.467466, -4.649883)
#
#
creatorList = [creator]

print("itinaryCreator ready")


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")



@app.route('/api/docs', methods=['GET'])
def docs():
    return '''<h1>Biken Web API</h1>
<p>Follow the project on <a href="https://github.com/QuentinPhilipp/BikenAPI">Github</a></p>
<hr>
<h3>If start and finish are latitude and longitude</h3>
<p>Endpoint : http://127.0.0.1:5000/api/1.0/itinerary?start=48.577043,7.759002&finish=48.577043,7.759002 DONE
<p>Endpoint : http://127.0.0.1:5000/api/1.0/route?start=48.577043,7.759002&distance={km} WIP

'''

class Compute(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print("Start Reset")
        for c in creatorList :
            c.resetAllNodes()
        print("End reset")


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

        itinerary = creator.getItinerary(startPosition,finishPosition)
        itinerary['geolocalisationTime']=geolocalisationTime;

        print("Time : ",itinerary['calculationTime'])
        # startPosition={"lat": waypointList[0][0], "lon": waypointList[0][1]}
        # finishPosition={"lat": waypointList[-1][0], "lon": waypointList[-1][1]}

        val = {"type" : "itinerary","distance":itinerary['distance'],"geolocalisationTime":itinerary['geolocalisationTime'],"calculationTime":itinerary['calculationTime'], "gps" : "false", "data" : {"startName": start, "startPos": startPosition , "finishName": finish, "finishPos": finishPosition, "waypoints":itinerary["waypoints"]}}
        print("Returned")

        # reset all the nodes in another thread to return the data instantly
        thread_a = Compute()
        thread_a.start()

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

        # geolocalisationTime = time.time()-startGeolocalisationTime;
        #
        #
        # list_threads = []
        # my_queue = queue.Queue()
        #
        # startComputationTime = time.time();
        # print("Starting threads")
        #
        # thread1 = Thread(target=testFunction, args=(0, my_queue,finishPosition,startPosition))
        # list_threads.append(thread1)
        # thread2 = Thread(target=testFunction, args=(1, my_queue,thirdPosition,finishPosition))
        # list_threads.append(thread2)
        # thread3 = Thread(target=testFunction, args=(2, my_queue,startPosition,thirdPosition))
        # list_threads.append(thread3)
        #
        # print("\nStart Threads\n\n")
        #
        #
        # # Start computing
        # for thread in list_threads:
        #     thread.start()
        #
        # print("\nWait Threads\n\n")
        #
        # # Wait the result from all thread
        # for thread in list_threads:
        #     thread.join() # Wait until thread terminates its task
        #
        # print("\n\nAll thread complete\n\n")
        #
        #
        # itinerary = {}
        # itinerary['distance']=0
        # itinerary["waypoints"]=[]
        #
        # # Check thread's return value
        # while not my_queue.empty():
        #     result = my_queue.get()
        #     itinerary["distance"] +=result['distance']
        #     itinerary["waypoints"] += result["waypoints"]
        #
        # computationTime = time.time()-startComputationTime;
        #
        # # reset all the nodes in another thread to return the data instantly
        # thread_a = Compute()
        # thread_a.start()
        #
        # itinerary['geolocalisationTime']=geolocalisationTime;
        # itinerary['calculationTime']=computationTime;
        #
        #
        # val = {"type" : "itinerary","distance":itinerary['distance'],"geolocalisationTime":itinerary['geolocalisationTime'],"calculationTime":itinerary['calculationTime'], "gps" : "false", "data" : {"startName": start, "startPos": startPosition , "finishName": finish, "finishPos": finishPosition, "waypoints":itinerary["waypoints"]}}
        #
        # return jsonify(val)


    else :
        print("Bad request")
        val = {"error_code": "01", "error_desc": "Endpoint not defined"}
        return jsonify(val)



@app.route('/api/1.0/debugDownload', methods=['GET'])
def sendDownloadSquares():

    dbManager = databaseManager.DatabaseManager()

    valuesRaw = dbManager.getDownloadPoints()
    values = []
    for point in valuesRaw :
        value = {
        "id":point[0],
        "lat":point[1],
        "lon":point[2]
        }
        values.append(value)

    val = {"status_code": "200", "data": values}
    return jsonify(val)

@app.route('/api/1.0/testThread', methods=['GET'])
def testThread():
    startGeolocalisationTime = time.time();
    start = "Brest"
    finish = "Rennes"
    startPosition = geocode(start)

    rep = generateCircle(startPosition,50,3)
    print(rep)

    # finishPosition = geocode(finish)
    # thirdPosition = geocode("Lannion")
    #
    #
    # geolocalisationTime = time.time()-startGeolocalisationTime;
    #
    #
    # list_threads = []
    # my_queue = queue.Queue()
    #
    # startComputationTime = time.time();
    # print("Starting threads")
    #
    # thread1 = Thread(target=testFunction, args=(0, my_queue,finishPosition,startPosition))
    # list_threads.append(thread1)
    # thread2 = Thread(target=testFunction, args=(1, my_queue,thirdPosition,finishPosition))
    # list_threads.append(thread2)
    # thread3 = Thread(target=testFunction, args=(2, my_queue,startPosition,thirdPosition))
    # list_threads.append(thread3)
    #
    # # thread = Thread(target=testFunction, args=(1,my_queue,startPosition,thirdPosition))
    # # list_threads.append(thread)
    #
    # print("\nStart Threads\n\n")
    #
    #
    # # Start computing
    # for thread in list_threads:
    #     thread.start()
    #
    # print("\nWait Threads\n\n")
    #
    # # Wait the result from all thread
    # for thread in list_threads:
    #     thread.join() # Wait until thread terminates its task
    #
    # print("\n\nAll thread complete\n\n")
    #
    #
    # itinerary = {}
    # itinerary['distance']=0
    # itinerary["waypoints"]=[]
    #
    # # Check thread's return value
    # while not my_queue.empty():
    #     result = my_queue.get()
    #     itinerary["distance"] +=result['distance']
    #     itinerary["waypoints"] += result["waypoints"]
    #
    #
    # # Without threads
    # # itinerary = creator.getItinerary(finishPosition,startPosition)
    # # creator.resetAllNodes()
    # #
    # # itinerary2 = creator.getItinerary(finishPosition,thirdPosition)
    # # creator.resetAllNodes()
    # #
    # # itinerary3 = creator.getItinerary(startPosition,thirdPosition)
    # # creator.resetAllNodes()
    #
    # # itinerary["waypoints"] += itinerary2["waypoints"]
    # # itinerary["waypoints"] += itinerary3["waypoints"]
    #
    #
    #
    # computationTime = time.time()-startComputationTime;
    #
    # # reset all the nodes in another thread to return the data instantly
    # thread_a = Compute()
    # thread_a.start()
    #
    # itinerary['geolocalisationTime']=geolocalisationTime;
    # itinerary['calculationTime']=computationTime;
    #
    #
    # val = {"type" : "itinerary","distance":itinerary['distance'],"geolocalisationTime":itinerary['geolocalisationTime'],"calculationTime":itinerary['calculationTime'], "gps" : "false", "data" : {"startName": start, "startPos": startPosition , "finishName": finish, "finishPos": finishPosition, "waypoints":itinerary["waypoints"]}}
    #
    # return jsonify(val)


    waypointList=[]

    for waypoint in rep:
        waypointList.append([waypoint["lat"],waypoint["lon"]])


    val = {"type" : "route","distance":0,"geolocalisationTime":0,"calculationTime":0, "gps" : "false", "data" : {"startName": "test", "startPos": startPosition , "finishName": "test", "finishPos": startPosition, "waypoints":waypointList}}

    return jsonify(val)

def testFunction(ts,queue,start,finish):

    print("Starting function for thread",ts)
    itinerary = creatorList[ts].getItinerary(start,finish)
    print("Ending function for thread",ts)
    queue.put(itinerary)


class RouteThread(Thread):
    def __init__(self,start,finish,id,queue):
        Thread.__init__(self)
        print("Starting initialisation thread",id)
        self.id = id
        self.startPoint = start
        self.finishPoint=finish
        print("Finish initialisation thread",id)


    def run(self):
        print("Start Computation")
        itineray = creatorList[self.id].getItinerary(self.startPoint,self.finishPoint)
        print("End Computation")
        queue.put(itinerary)



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
        print("Try n°",nbRetry)
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

app.run(host='0.0.0.0',port=6060)
