from math import cos,pi,inf,sin,sqrt,atan2
from bisect import bisect_left
import Way
import Node
from operator import attrgetter
import time


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

def getNodeFromNodeId(nodesIdList,nodesList,nodeId):
    # All node should be store ordered by id in the two lists nodesIdList and nodeList
    # Search into the list of id for the index and then take the good element in the node list
    # Use binary search
    index = bisect_left(nodesIdList, nodeId, lo=0, hi=len(nodesIdList))
    return nodesList[index]

def getClosestNode(nodesList,lat,lon):

    bestDistance = inf
    bestNode = None
    for node in nodesList:
        newDistance = (lat-node.latitude)**2 +(lon-node.longitude)**2

        if(newDistance<bestDistance):
            bestDistance = newDistance
            bestNode = node

    print("Best Distance : ",bestDistance)

    return [bestNode,bestDistance]

def distanceBetween(node1,node2):
    r=6371  #earth radius in km
    lat1 = node1.latitude*pi/180
    lon1 = node1.longitude*pi/180
    lat2 = node2.latitude*pi/180
    lon2 = node2.longitude*pi/180

    a = sin((lat2-lat1)/2)*sin((lat2-lat1)/2) + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)*sin((lon2-lon1)/2)
    c = 2*atan2(sqrt(a),sqrt(1-a))
    distance = r*c

    return distance

def smallestDistanceToGoalInList(listOfNodes):
    node = min(listOfNodes, key=attrgetter('distanceTotal'))
    return node

def reconstruct_path(endNode,startNode):
    startReconstruct=time.time()

    nodeList = []

    nodeListLatLon = []

    # the itinerary only have crossroad. We need to fill in with all the points
    currentNode = endNode

    while currentNode!=startNode:
        roadsFromCurrentNode = currentNode.ways
        precedingNode = currentNode.precedingNode
        roadsFromPrecedingNode = precedingNode.ways

        # We need to check the common way between the two nodes
        commonWay = roadsFromCurrentNode[0]
        for r1 in roadsFromCurrentNode:
            for r2 in roadsFromPrecedingNode:
                if r1==r2:
                    commonWay=r1

        pos1 = commonWay.getNodePosition(currentNode)
        pos2 = commonWay.getNodePosition(precedingNode)

        nodesInCommonWay = commonWay.nodes
        if pos1<pos2:
            for i in range(pos1,pos2):
                nodeList.append(nodesInCommonWay[i])
                nodeListLatLon.append([nodesInCommonWay[i].latitude,nodesInCommonWay[i].longitude])


        else:
            for i in range(pos1,pos2+1,-1):
                nodeList.append(nodesInCommonWay[i])
                nodeListLatLon.append([nodesInCommonWay[i].latitude,nodesInCommonWay[i].longitude])

        currentNode=precedingNode


    totalTimeReconstruct=time.time()-startReconstruct

    print("Path reconstructed in ",totalTimeReconstruct,"secondes ")

    return nodeListLatLon
