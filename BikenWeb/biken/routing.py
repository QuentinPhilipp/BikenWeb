import requests
import json
import time
from math import pi,cos,sin,radians
import random
import biken.utils as utils


def itinerary(startCoord,endCoord,mode) :
    startLon = startCoord['lon']
    startLat = startCoord['lat']
    endLon = endCoord['lon']
    endLat = endCoord['lat']

    startTime = time.time()

    url = f"https://routing.openstreetmap.de/routed-{mode}/route/v1/cycling/{startLon},{startLat};{endLon},{endLat}?overview=false&alternatives=false&steps=true&geometries=geojson"
    print("Url:",url)

    r = requests.get(url)
    data = r.json()
    startWaypoint = data['waypoints'][0]
    endWaypoint = data['waypoints'][1]


    print(f"\nDistance :{data['routes'][0]['distance']} meters")
    print(f"\nDuration :{data['routes'][0]['duration']//60} minutes")



    path = []
    for step in data['routes'][0]["legs"][0]["steps"]:
        path += step["geometry"]["coordinates"]

    print("\nNumber of point in the path :",len(path))


    # Switch from lon,lat to lat,lon for leaflet
    returnedPath = [(coord[1], coord[0]) for coord in path]
    endTime = time.time()
    print(f"~~~~~~~~~~~~\nTime for the request : {endTime-startTime} seconds")

    returnObject = {"waypoints":returnedPath,"distance":data["routes"][0]['distance'],"calculationTime":endTime-startTime,"estimatedTime":0}

    return returnObject


def route(startPoint,distance) :
    numberOfPoints = 5
    waypointList = generateCircle(startPoint,distance,numberOfPoints)

    baseUrl = 'http://router.project-osrm.org/trip/v1/cycling/'
    for waypoint in waypointList:
        baseUrl += str(waypoint["lon"]) + "," + str(waypoint["lat"]) + ";"

    #remove last ";"
    url = baseUrl[:-1] + "?steps=true&geometries=geojson"

    startTime = time.time()
    # url = 'http://router.project-osrm.org/trip/v1/driving/7.38005110142422,48.997893;7.391206631583589,48.91401095997912;7.515921473100911,48.8950695287716;7.581843953900803,48.96724512051065?steps=true&geometries=geojson'
    print(url)
    r = requests.get(url)
    data = r.json()
    path = []
    for leg in data['trips'][0]["legs"]:
        for step in leg["steps"]:
            path += step["geometry"]["coordinates"]
    #       print(path)
    # Switch from lon,lat to lat,lon for leaflet
    returnedPath = [(coord[1], coord[0]) for coord in path]
    endTime = time.time()
    returnObject = {"waypoints":returnedPath,"distance":data["trips"][0]['distance'],"calculationTime":endTime-startTime}
    return returnObject

def generateCircle(start,distance,points):
    # Generate a circle for the route
    angleBetween = 360/points
    radius = float(distance)/(2*pi)
    waypointList = []
    isDirectionOk = False
    nbRetry = 10   #Only allow 20 retry

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


            waypointList.append(coord)


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

if __name__ == '__main__':

    start = {}
    end = {}
    start["lat"] = 48.997893
    start["lon"] = 7.379982
    end["lat"] =48.962728
    end["lon"] = 7.369994

    # itinerary(start,end,"bike")

    route(start,50)
