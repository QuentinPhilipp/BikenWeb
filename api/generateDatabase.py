# coding: utf-8

import sqlite3
import requests
import time
import json
import sys
from math import pi,cos
import utils

beforeData = 0
afterData = 0

conn = sqlite3.connect("../data/Database.db")

requestTime = 0
stockageTime = 0
fetchingTime = 0

class Way(object):
    """docstring for Way."""
    def __init__(self, id,nodesIdVector,centerNode,oneway,roundabout,maxspeed,type):
        self.nodes = nodesIdVector
        self.id = id
        self.centerNode = centerNode
        self.oneway = oneway
        self.roundabout = roundabout
        self.maxspeed = maxspeed
        self.type = type

    def getNodes(self):
        return self.nodes

    def getId(self):
        return self.id

    def getCenterNode(self):
        return self.centerNode

    def getOneway(self):
        return self.oneway

    def getRoundabout(self):
        return self.roundabout

    def getMaxspeed(self):
        return self.maxspeed

    def getType(self):
        return self.type

class Node(object):
    """docstring for Node."""

    def __init__(self, id,lat,lon):
        self.id = id
        self.lat = lat
        self.lon = lon

    def getId(self):
        return self.id
    def getLat(self):
        return self.lat
    def getLon(self):
        return self.lon

def createTable():
    c = conn.cursor() # The database will be saved in the location where your 'py' file is saved
    try :
        # Create table - CLIENTS
        c.execute('''CREATE TABLE roads (id_way BIGINT, centerLat DOUBLE, centerLon DOUBLE, id_node BIGINT,oneway BOOL,roundabout BOOL, maxspeed INT, type TEXT,latitude DOUBLE, longitude DOUBLE)''')
        conn.commit()
        c.execute('''CREATE TABLE downloadPoints (id TEXT, latitude DOUBLE,longitude DOUBLE)''')
        conn.commit()
        print("Table created")
    except :
        print("Table already created")
        pass

def resetDatabase():
    c = conn.cursor() # The database will be saved in the location where your 'py' file is saved
    try :
        # Create table - CLIENTS
        c.execute('''DROP TABLE roads''')
        conn.commit()
        c.execute('''DROP TABLE downloadPoints''')
        conn.commit()
        print("Table clear")
    except :
        print("Table already destroy")
        pass

def callApi(north,west,south,east):
    resolved=False
    overpass_url = "http://overpass-api.de/api/interpreter"
    # overpass_query = f"[out:json];\n(\nnode[highway=tertiary]({south},{west},{north},{east});\nway[highway=tertiary]({south},{west},{north},{east});\nnode[highway=secondary]({south},{west},{north},{east});\nway[highway=secondary]({south},{west},{north},{east});\nnode[highway=primary]({south},{west},{north},{east});\nway[highway=primary]({south},{west},{north},{east});\nway[highway=cycleway]({south},{west},{north},{east});\n);\nout body;\n>;\nout skel qt;\n"

    overpass_query = f"""
[out:json];
// gather results
(
  node["highway"="tertiary"]({north},{west},{south},{east});
  node["highway"="secondary"]({north},{west},{south},{east});
  node["highway"="primary"]({north},{west},{south},{east});

  way["highway"="tertiary"]({north},{west},{south},{east});
  way["highway"="secondary"]({north},{west},{south},{east});
  way["highway"="primary"]({north},{west},{south},{east});

  // way[highway=cycleway]({north},{west},{south},{east});
);
// print results
(._;>;);
out body;
out skel asc;
"""
    while resolved==False:
        print("\nRequesting...")
        response = requests.get(overpass_url,
                        params={'data': overpass_query})
        # print("API response :",response)

        if (response.status_code==429):
            print("Try again later. Limit reached")

            # "Hack to get the waiting time"
            timeBlocked = requests.get("http://overpass-api.de/api/status")
            # return a text explaining how many time you need to wait
            index = timeBlocked.text.rfind("seconds")
            # cut the string at the last "seconds" in the text
            newString = timeBlocked[:index]
            # get all the digits in the text.
            intList = [int(s) for s in newString.split() if s.isdigit()]

            # We need the last one because we cut the string just before "seconds"
            timeToWait=intList[-1]
            print("waiting for ",timeToWait)
            time.sleep(timeToWait)
        elif (response.status_code==200):
            print("Status 200 : OK")
            data = response.json()
            resolved=True
            return data
        else :
            resolved=True
            print("Response from API :",response)

def getData(tile):
    global requestTime,stockageTime,fetchingTime
    squareSize = 70

    north = utils.addKmToLatitude(tile["lat"],-squareSize/2)
    west = utils.addKmToLongitude(tile["lat"],tile["lon"],-squareSize/2)
    south = utils.addKmToLatitude(tile["lat"],squareSize/2)
    east = utils.addKmToLongitude(tile["lat"],tile["lon"],squareSize/2)


    data = callApi(north,west,south,east)

    #parse elements
    elems = data["elements"]

    startFetchingTime = time.time()         #timer
    nodesVector = []
    wayVector = []
    for elem in elems:
        if elem["type"] == "node":
            id = elem["id"]
            lat = elem["lat"]
            lon = elem["lon"]
            n = Node(id,lat,lon)
            nodesVector.append(n)


        elif elem["type"] == "way":
            # print("way :",elem)
            nodeIdVector = []
            idWay = elem["id"]
            try :
                if elem["tags"]["junction"] == "roundabout":
                    roundabout = True
            except :
                roundabout = False

            try:
                if elem["tags"]["oneway"] == "yes":
                    oneway = True
                else :
                    oneway = False
            except Exception as e:
                print(e)
                oneway = False

            try:
                highway = elem["tags"]["highway"]
            except Exception as e:
                print(e)
                highway = "None"

            try:
                maxspeed = elem["tags"]["maxspeed"]

                #Must detect if the speed is in mph              (In France : 'maxspeed = 80 '    |  In England : 'maxspeed = 40mph')
                if maxspeed[len(maxspeed)-3:len(maxspeed)] == "mph":      #detect if the end of the string is "mph"
                    #convert the speed without mph (maxspeed[0:len(maxspeed)-4]) in kmh
                    maxspeed = int(int(maxspeed[0:len(maxspeed)-4]) * 1.609) #coeff multiplicateur

            except Exception as e:
                maxspeed = 80


            i=0
            for nodeId in elem["nodes"]:
                # print("add node id :",nodeId)
                nodeIdVector.append(nodeId)

                if(i==int(len(elem["nodes"])/2-1)):        #on est au milieu
                    centerNode = utils.findNodeInNodeVector(nodeId,nodesVector)
                    # print("centerNode : ",centerNode)
                i+=1

            w = Way(idWay,nodeIdVector,centerNode,oneway,roundabout,maxspeed,highway)
            # print(w)
            wayVector.append(w)

    endFetchingTime = time.time()
    fetchingTime+=endFetchingTime-startFetchingTime

    print("Node vector size : ",len(nodesVector))
    print("Way vector size : ",len(wayVector))

    data_tuple = (tile["id"],tile["lat"],tile["lon"]) #store the positions of the requests. Use to debug
    cur = conn.cursor()
    cur.execute("INSERT INTO downloadPoints(id,latitude,longitude) VALUES (?,?,?)",data_tuple)
    print("Inserting downloadPoints : ",data_tuple)
    conn.commit()

    startStockageTime = time.time()

    ways = []
    for way in wayVector:
        #centerNodeData = getNodeFromId(way.getCenterNodeId())
        for nodeId in way.getNodes():
            nodeLat = utils.findNodeInNodeVector(nodeId,nodesVector).getLat()
            nodeLon = utils.findNodeInNodeVector(nodeId,nodesVector).getLon()
            ways.append((way.getId(),way.getCenterNode().getLat(),way.getCenterNode().getLon(),nodeId,way.getOneway(),way.getRoundabout(),way.getMaxspeed(),way.getType(),nodeLat,nodeLon))

    sqlInsertQuery = """INSERT INTO roads (id_way,centerLat,centerLon,id_node,oneway,roundabout,maxspeed,type,latitude,longitude) VALUES (?,?,?,?,?,?,?,?,?,?)"""

    cur.executemany(sqlInsertQuery, ways)
    conn.commit()
    print("Added to db")

    endStockageTime = time.time()
    stockageTime+=endStockageTime-startStockageTime



def checkDataIn():
    #return the list of departement to add to avoid double values in the database
    cur = conn.cursor()
    tilesIn = []

    #check which tiles we have
    cur.execute("SELECT * FROM downloadPoints")
    rows = cur.fetchall()

    for row in rows:
        tilesIn.append(row[0])

    print("Tiles already in the database : ")
    for tile in tilesIn:
        print(tile)

    if len(tilesIn)==0:
        print("0")
    return tilesIn

def addRequestedTiles():
    tilesIn = checkDataIn()
    tilesToAdd = []
    with open('../data/tiles.json') as json_file:
        data = json.load(json_file)
        for tile in data["points"]:
            # If we need to download and not already in
            if tile['download']==1 and tile["id"] not in tilesIn:
                tilesToAdd.append(tile)

    print("Tiles to add : ",tilesToAdd)

    errorList=[]

    for tile in tilesToAdd:
        print('Adding tile :',tile["id"])
        try:
            getData(tile)
            print("1 point added")
        except Exception as e:
            errorList.append(tile)
            print(e)


    while (len(errorList)!=0):
        print('Still ',len(errorList),' errors')
        try:
            getData(errorList[len(errorList)-1])
            errorList.pop()
        except Exception as e:
            print("Exception : ",e)
            pass



if len(sys.argv)>1:
    if sys.argv[1]=="clear":
        print("Clearing database")
        resetDatabase()
else :
    createTable()
    addRequestedTiles()
