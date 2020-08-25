import requests
import json
import time
from math import pi,cos,sin,radians
import random
import biken.utils as utils
import os
from dotenv import load_dotenv


load_dotenv()
ELEVATION_API_KEY = os.environ.get("ELEVATION_API_KEY", None)

COEFF_DURATION = 2
OFFSET_DISTANCE_ROUTE = 10

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


    print(f"\nDistance :{data['routes'][0]['distance']/1000} kms")
    print(f"\nDuration :{data['routes'][0]['duration']//60} minutes")



    path = []
    for step in data['routes'][0]["legs"][0]["steps"]:
        path += step["geometry"]["coordinates"]

    print("\nNumber of point in the path :",len(path))



    # Switch from lon,lat to lat,lon for leaflet
    returnedPath = [(coord[1], coord[0]) for coord in path]
    endTime = time.time()
    print(f"~~~~~~~~~~~~\nTime for the request : {endTime-startTime} seconds")

    returnObject = {"waypoints":returnedPath,"duration":(data['routes'][0]['duration']//60)/COEFF_DURATION,"distance":round(data["routes"][0]['distance']/1000,2),"calculationTime":endTime-startTime,"estimatedTime":0}

    return returnObject


def route(startPoint,distance,mode) :
    numberOfPoints = 5
    waypointList = generateCircle(startPoint,distance,numberOfPoints)

    baseUrl = f'https://routing.openstreetmap.de/routed-{mode}/trip/v1/cycling/'
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

    waypointsIndex = []

    for leg in data['trips'][0]["legs"]:
        indexStart=0
        for step in leg["steps"]:
            path += step["geometry"]["coordinates"]
            indexStart += len(step["geometry"]["coordinates"])
        waypointsIndex.append(indexStart)
    #       print(path)
    # Switch from lon,lat to lat,lon for leaflet
    returnedPath = [(coord[1], coord[0]) for coord in path]


    # Check U-turn on the roads
    returnedPath = removeUturn(returnedPath);


    endTime = time.time()
    returnObject = {"waypoints":returnedPath,"duration":(data['trips'][0]['duration']//60)/COEFF_DURATION,"distance": round(data["trips"][0]['distance']/1000,2),"calculationTime":endTime-startTime}
    return returnObject





def removeUturn(coordsList):
    # Need to check if two adjacents points are the same;

    verified = False
    bufferSize=10;


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




def getElevation(path):
    print(path)
    print("Len of path :",len(path))

    # Scale down the resolution of the path for the Elevation API

    # Max 30 points
    divider = len(path)//30 + 1
    print("Divider :",divider)

    newPath = path[::divider]
    print("Len of new path :",len(newPath))

    # Convert list of tuple to a long string for the query

    query = "points="
    for point in newPath:
        query+=str(point[0])+','+str(point[1])+','

    # Remove last comma
    query = query[:-1]
    baseUrl = f'https://api.airmap.com/elevation/v1/ele/path?{query}'
    headers = {'X-API-Key': ELEVATION_API_KEY}
    print(baseUrl)
    r = requests.get(baseUrl, headers=headers)
    data = r.json()
    print(data)



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

    # route(start,50)

    # coordsList = ["G","E","D","C","B","A","B","C","D","F","H"]
    # coordsList = ["G","E","D","C","B","A","A","B","C","D","F","H"]
    # coordsList = ["X","W","V","U","T","S","R","Q","P","O","N","M","L","K","I","G","F","E","C","B","A","D","E","F","H","J"]
    # removeUturn(coordsList)
    # print(coordsList)
