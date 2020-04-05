# coding: utf-8

import sqlite3
import requests
import time
import json
import sys
from math import *

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
        self.centerNode = centerNode;
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
        c.execute('''CREATE TABLE departement (id TEXT,name TEXT)''')
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
        c.execute('''DROP TABLE departement''')
        conn.commit()
        print("Table clear")
    except :
        print("Table already destroy")
        pass

def callApi(north,west,south,east):
    resolved=0;
    while resolved==0:
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
        print(overpass_query)

        response = requests.get(overpass_url,
                        params={'data': overpass_query})
        print("API response :",response)

        if (response.status_code==409):
            print("Try again later. Limit reached");
            timeBlocked = requests.get("http://overpass-api.de/api/status")
            print(timeBlocked)
            exit()
        elif (response.status_code==200):
            print("Response OK")
            data = response.json()
            resolved=1
            return data
        else :
            print("Response from API :",response)

def getData(north,west,south,east):
    global requestTime,stockageTime,fetchingTime

    startRequestTime = time.time()

    data = callApi(north,west,south,east);

    endRequestTime = time.time()

    #parse elements
    elems = data["elements"]
    print("Elements :",len(elems))


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
                oneway = False

            try:
                highway = elem["tags"]["highway"]
            except Exception as e:
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
                    centerNode = findNodeInNodeVector(nodeId,nodesVector)
                    # print("centerNode : ",centerNode)
                i+=1

            w = Way(idWay,nodeIdVector,centerNode,oneway,roundabout,maxspeed,highway)
            # print(w)
            wayVector.append(w)

    endFetchingTime = time.time()
    fetchingTime+=endFetchingTime-startFetchingTime

    print("\nNode vector size : ",len(nodesVector))
    print("Way vector size : ",len(wayVector),"\n")

    startStockageTime = time.time()
    addValues(nodesVector,wayVector)

    endStockageTime = time.time()
    stockageTime+=endStockageTime-startStockageTime

def findNodeInNodeVector(idNode,nodeVector):
    # print("Find node ", idNode, "in nodeVector")
    i = len(nodeVector)-1
    prev_i=0
    temporaryValue=0
    valueToSubstract=0
    while(True):
        # print("Search for nodeID",temporaryValue," ",valueToSubstract," ",i," ",prev_i)
        node = nodeVector[i]
        id =node.getId()
        if(id==idNode):
            return node
        else :
            temporaryValue=i
            if(i>prev_i):
                valueToSubstract=int((i-prev_i)/2)
            else :
                valueToSubstract=int((prev_i-i)/2)

            if(valueToSubstract==0): #I had to add this because in the last operation we can have: (prev_i-i=1), so valueToSubstract would be 1/2=0
                valueToSubstract=1

            if(id>idNode):
                i-=valueToSubstract

            else :
                i+=valueToSubstract

            prev_i=temporaryValue

def addValues(nodesVector,wayVector):
    c = conn.cursor()
    ways = []
    i =0
    for way in wayVector:
        i+=1
        #centerNodeData = getNodeFromId(way.getCenterNodeId())
        for nodeId in way.getNodes():
            nodeLat = findNodeInNodeVector(nodeId,nodesVector).getLat()
            nodeLon = findNodeInNodeVector(nodeId,nodesVector).getLon()
            ways.append((way.getId(),way.getCenterNode().getLat(),way.getCenterNode().getLon(),nodeId,way.getOneway(),way.getRoundabout(),way.getMaxspeed(),way.getType(),nodeLat,nodeLon))

    # print "Creating Database Ways: ",time.time()
    # for node in nodesVector:
    sqlInsertQuery = """INSERT INTO roads (id_way,centerLat,centerLon,id_node,oneway,roundabout,maxspeed,type,latitude,longitude) VALUES (?,?,?,?,?,?,?,?,?,?)"""

    #print ways
    c.executemany(sqlInsertQuery, ways)
    conn.commit()
    print("Added to db")


def addRegion(region):
    distance = 25           #distance*2 = distance between two requestPoint
    errorList=[]


    north = "49.018312"
    west = "7.3889923"
    south = "49.083115"
    east = "7.4961090"

    try:
        getData(north,west,south,east)                #71km fais un cercle qui englobe tout le carre
        print("one tile added")
    except Exception as e:
        errorList.append((north,west,south,east))
        print(e)

    while (len(errorList)!=0):
        print('Still ',len(errorList),' errors')
        try:
            getData(errorList[len(errorList)-1][0],errorList[len(errorList)-1][1],errorList[len(errorList)-1][2],errorList[len(errorList)-1][3])
            errorList.pop()
        except Exception as e:
            pass

def checkDataIn():
    #return the list of departement to add to avoid double values in the database
    cur = conn.cursor()
    regionIn = []

    #check which region we have
    cur.execute("SELECT * FROM departement")
    rows = cur.fetchall()

    for row in rows:
        regionIn.append(row[0])

    print("Region already in the database : ")
    for region in regionIn:
        print(region)

    if len(regionIn)==0:
        print("0")
    return regionIn

def addRequestedRegions():
    regionIn = checkDataIn()
    regionToAdd = []
    with open('../data/departements.json') as json_file:
        data = json.load(json_file)
        for region in data:
            # If we need to download and not already in
            if region['download']==1 and region["id"] not in regionIn:
                regionToAdd.append(region)

    print("Region to add : ",regionToAdd)

    for region in regionToAdd:
        addRegion(region)
        print('region :',region)
        cur=conn.cursor()
        data_tuple = (region["id"],region["name"])
        cur.execute("INSERT INTO departement(id,name) VALUES (?,?)",data_tuple)
        conn.commit()

if len(sys.argv)>1:
    if sys.argv[1]=="clear":
        print("Clearing database")
        resetDatabase();
else :
    createTable()
    addRequestedRegions();
