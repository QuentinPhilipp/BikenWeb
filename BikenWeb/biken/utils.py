from math import cos,sin,atan2,pi, sqrt
import re
def addKmToLatitude(originalLat,kmToAdd):
    # print(type(originalLat))
    # print(type(kmToAdd))
    # +km go north, -km go south
    return originalLat + kmToAdd/111.1  #almost 111km everywhere on the planet

def addKmToLongitude(originalLat,originalLon,kmToAdd):
    # print(type(originalLat))
    # print(type(originalLon))
    # print(type(kmToAdd))
    # +km go east  -km go west
    r_earth = 6378
    return originalLon + (kmToAdd / r_earth) * (180 / pi) / cos(originalLat *pi/180) #longitude to km depend on the latitude. 111km at equador but 0 in the pole


def strToWaypoints(itineraryString):
    # transform a string of coords to a list of waypoints
    result = re.findall("((.+?),(.+?);)",itineraryString)

    waypoints = []
    for wp in result:
        waypoint = [float(wp[1]),float(wp[2])]
        waypoints.append(waypoint)


    return waypoints



def distanceBetweenPoints(pointA,pointB):
    R = 6371000 #metres
    φ1 = pointA["lat"] * pi/180 # φ, λ in radians
    φ2 = pointB["lat"] * pi/180
    Δφ = (pointB["lat"]-pointA["lat"]) * pi/180
    Δλ = (pointB["lon"]-pointA["lon"]) * pi/180

    a = sin(Δφ/2) * sin(Δφ/2) + cos(φ1) * cos(φ2) * sin(Δλ/2) * sin(Δλ/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = R * c

    return d  # in meters

if __name__ == '__main__':

    pointA = {"lat":46.056755,"lon":14.505581}
    pointB = {"lat":46.053155,"lon":14.503893 }
    d = distanceBetweenPoints(pointA,pointB)
    print("Distance :",d)