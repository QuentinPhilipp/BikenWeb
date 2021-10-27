import requests
import json
import time
from math import pi,cos,sin,radians
import random
import biken.utils as utils
import biken.data as dataManager
import os
from dotenv import load_dotenv
import polyline


load_dotenv()
ELEVATION_API_KEY = os.environ.get("ELEVATION_API_KEY", None)
MAPBOX_API_KEY = os.environ.get("MAPBOX_DIRECTION_API_TOKEN", None)

COEFF_DURATION = 2
OFFSET_DISTANCE_ROUTE = 10

def itinerary(startCoord,endCoord) :
    startLon = startCoord['lon']
    startLat = startCoord['lat']
    endLon = endCoord['lon']
    endLat = endCoord['lat']

    startTime = time.time()

    # Add the waypoints in the request
    url = f"https://api.mapbox.com/directions/v5/mapbox/cycling/{startLon},{startLat};{endLon},{endLat}?alternatives=false&overview=full&geometries=polyline&steps=false&access_token={MAPBOX_API_KEY}"

    # Request data and sort the results
    try:
        print("Request itinerary: ",url)
        r = requests.get(url)
        data = r.json()
        polyline = data["routes"][0]["geometry"]
        distance = int(data["routes"][0]["distance"])
        duration = int(data["routes"][0]["duration"]/60)

        # Create waypoints
        startWaypoint = {"name":data["waypoints"][0]["name"],"lon": data["waypoints"][0]["location"][0],"lat": data["waypoints"][0]["location"][1]}
        endWaypoint = {"name":data["waypoints"][1]["name"],"lon": data["waypoints"][1]["location"][0],"lat": data["waypoints"][1]["location"][1]}

        endTime = time.time()

        # Return the route
        returnObject = {"type":"oneway","polyline":polyline,"duration":duration/COEFF_DURATION,"distance":distance,"calculationTime":endTime-startTime,"start":startWaypoint,"end":endWaypoint}
        return returnObject
    except Exception as e:
        return {"type":"error","polyline":[],"duration":0,"distance":0,"calculationTime":0,"start":0,"end":0}


def route(startPoint,distance, waypointList=[]) :
    numberOfPoints = 5
    if waypointList == []:
        waypointList = generateCircle(startPoint,distance,numberOfPoints)

    # Add the waypoints in the request
    url = f"https://api.mapbox.com/directions/v5/mapbox/cycling/{waypointList[0]['lon']},{waypointList[0]['lat']};{waypointList[1]['lon']},{waypointList[1]['lat']};{waypointList[2]['lon']},{waypointList[2]['lat']};{waypointList[3]['lon']},{waypointList[3]['lat']};{waypointList[4]['lon']},{waypointList[4]['lat']};{waypointList[0]['lon']},{waypointList[0]['lat']}?alternatives=false&overview=full&geometries=polyline&steps=false&access_token={MAPBOX_API_KEY}"

    startTime = time.time()
    print("Request itinerary: ",url)

    # Request data and sort the results
    r = requests.get(url)
    data = r.json()
    polyline = data["routes"][0]["geometry"]
    distance = int(data["routes"][0]["distance"])
    duration = int(data["routes"][0]["duration"]/60)

    # Create waypoints
    startWaypoint = {"name":data["waypoints"][0]["name"],"lon": data["waypoints"][0]["location"][0],"lat": data["waypoints"][0]["location"][1]}
    endWaypoint = startWaypoint

    endTime = time.time()

    # Return the route
    returnObject = {"type":"round","polyline":polyline,"duration":duration,"distance":distance,"calculationTime":endTime-startTime,"start":startWaypoint,"end":endWaypoint, "waypoints":waypointList}
    return returnObject


def removeUturn(coordsList):
    # Need to check if two adjacents points are the same;

    verified = False
    bufferSize=10


    # while not verified:
    #     for i,point in enumerate(coordsList[:-2]):
    #         # print("point:",coordsList[i],"point+1:",coordsList[i+1],"point+2:",coordsList[i+2])
    #
    #
    #         minIndex = i-bufferSize
    #         if minIndex<0:
    #             minIndex = 0
    #
    #         # Update buffer with last 20 points
    #         bufferPoint = coordsList[minIndex:i+2]
    #
    #         if coordsList[i+2] in bufferPoint:
    #             ind = bufferPoint.index(coordsList[i+2])
    #             removeLow = i-(bufferSize-ind)
    #             removeHigh = i+2
    #             removedList = coordsList[removeLow:removeHigh]
    #             del coordsList[removeLow:removeHigh]
    #             break
    #
    #         if coordsList[i]==coordsList[i+2] :
    #             # config XYX
    #             # remove the point Y to have two identical point next to each other
    #             coordsList.remove(coordsList[i+1])
    #             break
    #
    #         elif coordsList[i]==coordsList[i+1] :
    #             # config XYYX
    #             # Remove the two Y only if the next one are different
    #             if (coordsList[i-1]!=coordsList[i+2]):
    #                  # XYYZ -> XYZ
    #                 coordsList.remove(coordsList[i])
    #             else:
    #                 # XYYX -> XX
    #                 coordsList.remove(coordsList[i+1])
    #                 coordsList.remove(coordsList[i])
    #             break
    #     else:
    #         verified=True

    return coordsList




def generateCircle(start,distance,points):
    # Generate a circle for the route

    distance = distance - OFFSET_DISTANCE_ROUTE

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

        maxValue = 360
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
    # waypointList.append(coord)            #adding startNode to close the route

    return waypointList

def getGPSLocation(place):
    endpoint = "https://nominatim.openstreetmap.org/search/"
    endpoint = endpoint+place+"?format=json&limit=1"
    r = requests.get(endpoint)
    response = r.json()
    return {"lat":response[0]["lat"],"lon":response[0]["lon"]}


def getElevation(itineraryId):
    # Get the polyline associated with the itinerary ID
    polylineData = dataManager.getPolylineFromId(itineraryId)

    if polyline != -1 :

        # Convert the polyline into gps points
        path = polyline.decode(polylineData, 5,geojson=True)

        # Scale down the resolution of the path for the Elevation API
        # Max 30 points
        divider = len(path)//30 + 1
        newPath = path[::divider]

        # Convert list of tuple to a long string for the query
        query = "points="
        for point in newPath:
            query+=str(point[0])+','+str(point[1])+','

        # Remove last comma
        query = query[:-1]
        baseUrl = f'https://api.airmap.com/elevation/v1/ele/path?{query}'
        headers = {'X-API-Key': ELEVATION_API_KEY}
        r = requests.get(baseUrl, headers=headers)
        response = r.json()
        profile = []
        data = response["data"]
        if response["status"]=="success":
            for step in data:
                profile.extend(step["profile"])

        # # Calculate total elevation
        # elevation = 0
        # try:
        #     for i in range(len(profile)-2):
        #         if profile[i]>profile[i+1]:
        #             elevation += (profile[i]-profile[i+1])
        # except IndexError as e:
        #     print("Error")
        #
        # print("Total elevation :",elevation)

        # Max N points in the profile
        divider = len(profile)//150 + 1
        profile = profile[::divider]

        return {"profile":profile,"elevation":0}
    else :
        return {"error":"Itinerary not found when requesting elevation"}


def addKmWithAngle(radius, direction, startPos):
    #calculate the km to add to latitude and longitude based on the angle
    addLat = sin(radians(direction))*radius
    addLon = cos(radians(direction))*radius

    returnValues = {}
    returnValues["lat"] = utils.addKmToLatitude(float(startPos["lat"]),addLat)
    returnValues["lon"] = utils.addKmToLongitude(float(startPos["lat"]),float(startPos["lon"]),addLon)

    return returnValues

def convertStravaItinerary(polylineData,distance,duration):
    startTime = time.time()

    # Convert the polyline into gps points
    path = polyline.decode(polylineData, 5,geojson=True)

    # Create waypoints
    startWaypoint = {"name":"Start","lon": path[0][0],"lat": path[0][1]}
    endWaypoint = {"name":"Destination","lon": path[len(path)-1][0],"lat": path[len(path)-1][1]}

    # Detecting route or itinerary
    # TO FIX ( Allow a variation due to GPS imprecision)

    # if startPoint and endPoint are located at 1km from each other, we consider that it's a round trip
    if utils.distanceBetweenPoints(startWaypoint,endWaypoint)<=1000:
        itineraryType = "round"
    else :
        itineraryType = "oneway"


    endTime = time.time()

    # Create the itinerary object
    itineraryObject = {"type":itineraryType,"polyline":polylineData,"duration":duration,"distance":distance,"calculationTime":endTime-startTime,"start":startWaypoint,"end":endWaypoint}

    print("\n\n\n",itineraryObject,"\n\n\n")

    # Store itinerary in DB
    itineraryId = dataManager.storeItinerary(itineraryObject)
    uniqueId = itineraryId

    return uniqueId



if __name__ == '__main__':

    start = {}
    end = {}
    start["lat"] = 48.997893
    start["lon"] = 7.379982
    end["lat"] =48.962728
    end["lon"] = 7.369994


    getGPSLocation("Strasbourg")

    # itinerary(start,end,"bike")

    # route(start,50)

    # coordsList = ["G","E","D","C","B","A","B","C","D","F","H"]
    # coordsList = ["G","E","D","C","B","A","A","B","C","D","F","H"]
    # coordsList = ["X","W","V","U","T","S","R","Q","P","O","N","M","L","K","I","G","F","E","C","B","A","D","E","F","H","J"]
    # removeUturn(coordsList)
    # print(coordsList)
