# coding: utf-8

import sqlite3
import requests
import time
import json
import sys
from math import *


beforeData = 0
afterData = 0
conn = sqlite3.connect("../routing/Data/Database.db")

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


    except :
        pass

def getData(lat,lon,rad):
    global requestTime,stockageTime,fetchingTime

    startRequestTime = time.time()
    urlString = 'http://overpass-api.de/api/interpreter?data=%3Cosm-script%20output%3D%22json%22%3E%0A%20%20%3Cquery%20type%3D%22way%22%3E%0A%20%20%20%20%20%20%3Caround%20lat%3D%22'+lat+'%22%20lon%3D%22'+lon+"%22%20radius%3D%22"+rad+"%22%2F%3E%0A%20%20%20%20%20%20%3Chas-kv%20k%3D%22highway"+"%22%20regv%3D%22primary%7Csecondary%7Ctertiary"+"%22%2F%3E%0A%20%20%3C%2Fquery%3E%0A%20%20%3Cunion%3E%0A%20%20%20%20%3Citem%2F%3E%0A%20%20%20%20%3"+"Crecurse%20type%3D%22down%22%2F%3E%0A%20%20%3C%2Funion%3E%0A%20%20%3Cprint%2F%3E%0A%3C%2Fosm-script%3E";

    #make the request
    r = requests.get(urlString)

    endRequestTime = time.time()
    requestTime+=endRequestTime-startRequestTime         #timer
    # print('Request Done')
    # print urlString

    #parse elements
    elems = r.json()["elements"]

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
                nodeIdVector.append(nodeId)

                if(i==len(elem["nodes"])/2-1):        #on est au milieu
                    centerNode = findNodeInNodeVector(nodeId,nodesVector)
                i+=1

            w = Way(idWay,nodeIdVector,centerNode,oneway,roundabout,maxspeed,highway)
            wayVector.append(w)

    endFetchingTime = time.time()
    fetchingTime+=endFetchingTime-startFetchingTime

    # print "\nNode vector size : ",len(nodesVector)
    # print "Way vector size : ",len(wayVector),"\n"

    startStockageTime = time.time()
    addValues(nodesVector,wayVector)
    endStockageTime = time.time()
    stockageTime+=endStockageTime-startStockageTime

def findNodeInNodeVector(idNode,nodeVector):
    i = len(nodeVector)-1
    prev_i=0
    temporaryValue=0
    valueToSubstract=0
    while(True):
        node = nodeVector[i]
        id =node.getId()
        if(id==idNode):
            return node
        else :
            temporaryValue=i
            if(i>prev_i):
                valueToSubstract=(i-prev_i)/2
            else :
                valueToSubstract=(prev_i-i)/2

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

def fixingError(errorList):
    while (len(errorList)!=0):
        print 'Still ',len(errorList),' errors'
        try:
            getData(errorList[len(errorList)-1][0],errorList[len(errorList)-1][1],"55000")
            errorList.pop()
        except Exception as e:
            pass

def addId(args):
    list = []
    cur = conn.cursor()
    with open('../routing/Data/regionCoord.json') as json_file:
        data = json.load(json_file)
        for j in range(len(sys.argv)):
            for i in range(len(data)):
                if j==0:
                    pass

                elif data[i]["ID"] == str(sys.argv[j]):
                    name = data[i]["Name"]
                    print(name,j)
                    list.append((sys.argv[j],name));

    print('Ajout de :',list)
    cur.executemany("INSERT INTO departement(id,name) VALUES (?,?)",list)
    conn.commit()

def checkDataIn():
    #return the list of departement to add to avoid double values in the database
    cur = conn.cursor()
    entryList = []
    alreadyInList = []
    outputList = []

    #check which region we want
    for arg in sys.argv:
        if arg==sys.argv[0]:
            pass
        else:
            entryList.append(arg)

    #check which region we have
    cur.execute("SELECT * FROM departement")
    rows = cur.fetchall()

    for row in rows:
        alreadyInList.append(row[0])


    print("alreadyInList : ",alreadyInList)
    print("entryList : ",entryList)

    for e in entryList:
        if e not in alreadyInList:
            outputList.append(e)

    #get the difference
    return outputList

createTable()

regionToAdd = checkDataIn()
print("add :",regionToAdd)


with open('../routing/Data/regionCoord.json') as json_file:
    distance = 25           #distance*2 = size between two requestPoint
    errorList=[]
    data = json.load(json_file)
    for j in range(len(regionToAdd)):
        for i in range(len(data)):
            if data[i]["ID"] == str(regionToAdd[j]):
                print "Nom :",data[i]["Name"]," | ID : ",data[i]["ID"]," | Coordonnées du centre : ",data[i]["Latitude"]," : ",data[i]["Longitude"]
                lat1 = str(data[i]["Latitude"]+distance/111.11)
                lon1 = str(data[i]["Longitude"]+distance/(111.11*cos(data[i]["Latitude"])))
                lat2 = str(data[i]["Latitude"]-distance/111.11)
                lon2 = str(data[i]["Longitude"]-distance/(111.11*cos(data[i]["Latitude"])))

                radius = "55000"
                try:
                    getData(lat1,lon1,radius)                #71km fais un cercle qui englobe tout le carre
                    print("one tile added")
                except Exception as e:
                    errorList.append((lat1,lon1))
                    print e

                try:
                    getData(lat2,lon1,radius)                #71km fais un cercle qui englobe tout le carre
                    print("one tile added")
                except Exception as e:
                    errorList.append((lat2,lon1))
                    print e

                try:
                    getData(lat1,lon2,radius)                #71km fais un cercle qui englobe tout le carre
                    print("one tile added")
                except Exception as e:
                    errorList.append((lat1,lon2))
                    print e

                try:
                    getData(lat2,lon2,radius)                #71km fais un cercle qui englobe tout le carre
                    print("one tile added")
                except Exception as e:
                    errorList.append((lat2,lon2))
                    print e

    fixingError(errorList)

    addId(regionToAdd)

conn.close()

#creer 4 carré equidistant
#requetes d'environ 50~60 km de rayon (il faut que les cercles se croisent assez)






#top
