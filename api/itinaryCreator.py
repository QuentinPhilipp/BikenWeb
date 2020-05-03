import databaseManager
import time
import utils
import Node
import Way
from bisect import bisect_left
from math import pi,cos,sin,sqrt,atan2,inf
from operator import attrgetter

MAX_DISTANCE_FROM_START = 50

class itineraryCreator(object):
    def __init__(self,startLat,startLon):
        self._startLat=startLat
        self._startLon=startLon
        self._nodesList=[]
        self._nodesIdList=[]     #same order than nodeList but contain only id. Faster to iterate
        self._waysList=[]

        self.createAllNodesObject()
        self.createAllWaysObject()
    # Getter and setter
    # Start Latitude
    @property
    def startLat(self):
        return self._startLat

    @startLat.getter
    def startLat(self):
        return self._startLat

    # Start Longitude
    @property
    def startLon(self):
        return self._startLon

    @startLon.getter
    def startLon(self):
        return self._startLon

    # Node List
    @property
    def nodesList(self):
        return self._nodesList

    @nodesList.getter
    def nodesList(self):
        return self._nodesList

    @nodesList.setter
    def nodesList(self,value):
        self._nodesList = value

    # NodeId List
    @property
    def nodesIdList(self):
        return self._nodesIdList

    @nodesIdList.getter
    def nodesIdList(self):
        return self._nodesIdList

    @nodesIdList.setter
    def nodesIdList(self,value):
        self._nodesIdList = value

    # Way List
    @property
    def waysList(self):
        return self._waysList

    @waysList.getter
    def waysList(self):
        return self._waysList

    @waysList.setter
    def waysList(self,value):
        self._waysList = value


    # Methods

    def createAllNodesObject(self):
        print("Create Node")

        db = databaseManager.DatabaseManager()


        north = utils.addKmToLatitude(self.startLat,MAX_DISTANCE_FROM_START)
        east = utils.addKmToLongitude(self.startLat,self.startLon,MAX_DISTANCE_FROM_START)
        west = utils.addKmToLongitude(self.startLat,self.startLon,-MAX_DISTANCE_FROM_START)
        south = utils.addKmToLatitude(self.startLat,-MAX_DISTANCE_FROM_START)

        print(north,west,south,east)

        startTimeFetch = time.time()
        data = db.getAllNodeInBoundingBox(north,west,south,east)
        print("All data fetch from database in ",time.time() - startTimeFetch, "seconds")


        startTimeCreation = time.time()
        localNodeList = []
        localNodeIdList = []    #copy of localNodeList but only Id
        for rawNode in data:
            idNode = rawNode[0]
            lat = rawNode[1]
            lon = rawNode[2]
            node = Node.Node(idNode,lat,lon)
            localNodeList.append(node)
            localNodeIdList.append(idNode)
        print("",len(localNodeList)," nodes created in ",time.time() - startTimeCreation, "seconds")
        self.nodesList = localNodeList
        self.nodesIdList= localNodeIdList


    def createAllWaysObject(self):
        print("Create Way")

        db = databaseManager.DatabaseManager()

        north = utils.addKmToLatitude(self.startLat,MAX_DISTANCE_FROM_START)
        east = utils.addKmToLongitude(self.startLat,self.startLon,MAX_DISTANCE_FROM_START)
        west = utils.addKmToLongitude(self.startLat,self.startLon,-MAX_DISTANCE_FROM_START)
        south = utils.addKmToLatitude(self.startLat,-MAX_DISTANCE_FROM_START)

        print(north,west,south,east)

        startTimeFetch = time.time()
        data = db.getAllWayInBoundingBox(north,west,south,east)
        print("All data fetch from database in ",time.time() - startTimeFetch, "seconds")


        wayNodesList = []  #list of all node in a way
        localWaysList = []      #list of all ways

        startTimeCreation = time.time()

        lastRawNode = [data[0][0]]   #init lastNode with the id of the first way
        for rawNode in data:
            # rawNode = [id_way,centerLat,centerLon,id_node_center,id_node,oneway,roundabout,maxspeed,type,latitude,longitude]
            if rawNode[0]!=lastRawNode[0]:          # End of the road, need to store the road and make a new one
                idWay=lastRawNode[0]                # All those data are the same for every node in the way
                centerNodeId = lastRawNode[3]
                oneway = lastRawNode[5]
                roundabout = lastRawNode[6]
                maxspeed = lastRawNode[7]
                roadType = lastRawNode[8]
                centerNode=self.getNodeFromNodeId(centerNodeId)
                way = Way.Way(idWay,wayNodesList,centerNode,oneway,roundabout,maxspeed,roadType)
                localWaysList.append(way)
                currentWayId=idWay
                wayNodesList=[]

            lastRawNode = rawNode

            # For each data we need to create the node
            idNode = rawNode[4]
            node = self.getNodeFromNodeId(idNode)
            wayNodesList.append(node)
            # node.addWayCount()      #+1 in the way counter


        # Add the last way
        idWay=lastRawNode[0]                # All those data are the same for every node in the way
        centerNodeId = lastRawNode[3]
        oneway = lastRawNode[5]
        roundabout = lastRawNode[6]
        maxspeed = lastRawNode[7]
        roadType = lastRawNode[8]
        centerNode=self.getNodeFromNodeId(centerNodeId)
        way = Way.Way(idWay,wayNodesList,centerNode,oneway,roundabout,maxspeed,roadType)
        localWaysList.append(way)


        # Add a reference to the road in every node
        for way in localWaysList:
            for node in way.nodes:
                node.addWay(way)


        print("",len(localWaysList)," ways created in ",time.time() - startTimeCreation, "seconds")

        self.waysList=localWaysList


    def getNodeFromNodeId(self,nodeId):
        # All node should be store ordered by id
        # Search into the list of id for the index and then take the good element in the node list
        # Use binary search
        index = bisect_left(self.nodesIdList, nodeId, lo=0, hi=len(self.nodesIdList))
        return self.nodesList[index]



    def resetAllNodes(self):
        # Reset points to allow a new request.
        for node in self.nodesList:
            # reseting the node before every new requests
            node.resetNode()

        print("All node reset, ready for a new request")

    def getItinerary(self,startPosition,finishPosition):
        startTime=time.time()

        # Search the closest node to the position
        # Search in the object, the corresponding object


        # Get closest crossroad bc the current algorythm use only crossroads and not all node to optimize performance
        startLat = float(startPosition["lat"])
        startLon = float(startPosition["lon"])

        goalLat = float(finishPosition["lat"])
        goalLon = float(finishPosition["lon"])

        closestDistanceToStart=inf
        closestDistanceToGoal=inf
        closestNodeToStart = None
        closestNodeToGoal = None


        for node in self.nodesList:
            # print("testDistance")

            distanceToStart = (startLat-node.latitude)**2 +(startLon-node.longitude)**2
            distanceToGoal = (goalLat-node.latitude)**2 +(goalLon-node.longitude)**2

            if (distanceToStart < closestDistanceToStart) and len(node.ways)>1:
                closestDistanceToStart = distanceToStart
                closestNodeToStart = node

            if (distanceToGoal < closestDistanceToGoal) and len(node.ways)>1:
                closestDistanceToGoal = distanceToGoal
                closestNodeToGoal = node


        startNodeId=closestNodeToStart.id
        finishNodeId=closestNodeToGoal.id

        print("from ",startNodeId,"to",finishNodeId)

        interTime=time.time()-startTime
        print("intertime :",interTime);


        geoData = self.aStarSearch(startNodeId,finishNodeId)
        # return positionList

        totalTime=time.time()-startTime

        returnObject = {"waypoints":geoData[0],"distance":geoData[1],"calculationTime":totalTime}
        return returnObject




    def distanceBetween(self,node1,node2):
        r=6371  #earth radius in km
        lat1 = node1.latitude*pi/180
        lon1 = node1.longitude*pi/180
        lat2 = node2.latitude*pi/180
        lon2 = node2.longitude*pi/180

        a = sin((lat2-lat1)/2)*sin((lat2-lat1)/2) + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)*sin((lon2-lon1)/2)
        c = 2*atan2(sqrt(a),sqrt(1-a))
        distance = r*c

        return distance





    def smallestDistanceToGoalInList(self,openSet):
        node = min(openSet, key=attrgetter('distanceTotal'))
        return node



    def nodeNeighbor(self,current):
        neighborList = []
        for way in current.ways:
            # search in multiple ways if the current node belong to multiple ways


            # indexOfCurrentNode = self.getPositionInWay(current,way)

            # if indexOfCurrentNode-1>=0:
            #     neighborList.append(way.nodes[indexOfCurrentNode-1])
            # if indexOfCurrentNode+1<len(way.nodes):
            #     neighborList.append(way.nodes[indexOfCurrentNode+1])



            # only add neighbor with more than one way.
            for node in way.nodes:
                if len(node.ways)>1:
                        neighborList.append(node)

        # s=""
        # for neighbor in neighborList:
        #     s+= str(neighbor.id)
        #     s+= ","
        # print("neighborList:",s)


        return neighborList



    def getPositionInWay(self,nodeToSearch,way):
        #return the index of a node in a way
        nodes = way.nodes
        wantedId=nodeToSearch.id
        if(nodes[0].id==wantedId):
            return 0
        elif nodes[-1].id == wantedId:
            return len(nodes)-1
        else:
            for i in range(len(nodes)):
                if nodes[i].id==wantedId:
                    return i

    def reconstruct_path(self,endNode,startNode):
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

            pos1 = self.getPositionInWay(currentNode,commonWay)
            pos2 = self.getPositionInWay(precedingNode,commonWay)

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

    def aStarSearch(self,startNodeId,endNodeId):
        # The set of discovered nodes that may need to be (re-)expanded.
        # Initially, only the start node is known.
        # This is usually implemented as a min-heap or priority queue rather than a hash-set.

        startTimeASearch=time.time()

        startNode = self.getNodeFromNodeId(startNodeId)
        endNode = self.getNodeFromNodeId(endNodeId)

        openSet = [startNode]

        # List of nodes already discovered and explored.
        # Starts off empty
        # Once a node has been 'current' it then goes here
        closeSet = []


        # For node n, cameFrom[n] is the node immediately preceding it on the cheapest path from start
        # to n currently known.
        cameFrom = []

        startNode.distanceFromStart = 0

        startNode.distanceTotalEstimated = self.distanceBetween(startNode,endNode)

        while openSet:
            current = self.smallestDistanceToGoalInList(openSet)

            if current==endNode:
                totalTimeASearch=time.time()-startTimeASearch

                print("End reached in ",totalTimeASearch,"secondes ")
                itinerarySize = endNode.distanceFromStart
                return [self.reconstruct_path(endNode,startNode),itinerarySize]

            closeSet.append(current)

            openSet.remove(current)


            for neighbor in self.nodeNeighbor(current):
                # d(current,neighbor) is the weight of the edge from current to neighbor
                # tentative_gScore is the distance from start to the neighbor through current
                nextDistanceFromStart = current.distanceFromStart + self.distanceBetween(current, neighbor)

                if nextDistanceFromStart<neighbor.distanceFromStart:
                    neighbor.precedingNode = current
                    neighbor.distanceFromStart=nextDistanceFromStart
                    neighbor.distanceTotal = neighbor.distanceFromStart + self.distanceBetween(neighbor,endNode)
                    if neighbor not in closeSet :
                        openSet.append(neighbor)


        print("End not reached")


    # DEBUG FUNCTION

    def printAllNodes(self):
        print("All nodes :")
        for node in self.nodeList:
            # print(node.id, " Latitude: ",node.latitude," Longitude: ",node.longitude," marque: ",node.marque)
            print(node.id, " Latitude: ",node.latitude," Longitude: ",node.longitude," marque: ",node.marque," ways: ",node.ways)

    def printAllWays(self):
        print("All ways :")
        for way in self.waysList:
            nodeString = ""
            for node in way.nodes:
                nodeString += str(node.id)
                nodeString += "|"
            print(way.id,":",nodeString)




def displayNode(node):
    print("id : ",node.id,"marque:",node.marque,"ways:")
    for way in node.ways:
        print(way.id)

if __name__ == "__main__" :
    creator = itineraryCreator(49.0008188, 7.3787709)
    creator.createAllNodesObject()
    creator.createAllWaysObject()

    # creator.printAllNodes()
    # creator.printAllWays()

    startNodeId = 287305190
    # finishNodeId = 841874221
    finishNodeId=5843835950

    geoDataList = creator.aStarSearch(startNodeId,finishNodeId)

    # print("id : ",creator.waysList[0].nodes[0].id," : ",creator.waysList[0].nodes[0].marque)

    # creator.waysList[0].nodes[0].marque = True

    # print("id : ",creator.waysList[0].nodes[0].id," : ",creator.waysList[0].nodes[0].marque)

    # creator.printAllNodes()

    # node1 = Node.Node(1,5,5)
    # node2 = Node.Node(2,5,5)
    # node3 = Node.Node(3,5,5)

    # way = Way.Way(10,[node1,node2,node3],node2)

    # print("Node 1 lat :",node1.distance)

    # way.nodes[0].distance = 10

    # print("Node 1 lat :",node1.distance)

    # print("Node 1 in way :",way.nodes[0].distance,"id : ",way.nodes[0].id)
