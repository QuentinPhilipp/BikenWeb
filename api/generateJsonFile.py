import json
import sys
from string import ascii_uppercase
from math import pi,cos


data = {}
data['point'] = []



def addKmToLatitude(originalLat,kmToAdd):
    return originalLat + kmToAdd/111.1  #almost 111km everywhere on the planet

def addKmToLongitude(originalLat,originalLon,kmToAdd):
    r_earth = 6378
    return originalLon + (kmToAdd / r_earth) * (180 / pi) / cos(originalLat *pi/180) #longitude to km depend on the latitude. 111km at equador but 0 in the pole

def addSquare(lat,lon,indexX,indexY):
    stringId = ""+ascii_uppercase[indexY]+str(indexX)
    values = {
    'id':stringId,
    'lat':lat,
    'lon':lon,
    'download':0
    }
    data['point'].append(values)

startLat = 50.8
startLon = 7.81
maxLat = 42
maxLon = -5
indexX=0
indexY=0

currentLat = startLat
currentLon = startLon
while (currentLat>maxLat):
    currentLon=startLon
    indexX=0
    while (currentLon>maxLon):
        addSquare(currentLat,currentLon,indexX,indexY)
        currentLon = addKmToLongitude(currentLat,currentLon,-65)
        indexX+=1
    currentLat = addKmToLatitude(currentLat,-65)
    indexY+=1

with open('../data/departement2.json', 'w') as outfile:
    json.dump(data, outfile)
