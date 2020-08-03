from math import cos,pi

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
