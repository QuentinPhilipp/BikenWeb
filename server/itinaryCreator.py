## Library ##
import time
from math import inf

## My modules ##
import databaseManager
import utils
import search
import Node
import Way


MAX_DISTANCE_FROM_START = 1000

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
                centerNode=utils.getNodeFromNodeId(self.nodesIdList,self.nodesList,centerNodeId)
                way = Way.Way(idWay,wayNodesList,centerNode,oneway,roundabout,maxspeed,roadType)
                localWaysList.append(way)
                currentWayId=idWay
                wayNodesList=[]

            lastRawNode = rawNode

            # For each data we need to create the node
            idNode = rawNode[4]
            node = utils.getNodeFromNodeId(self.nodesIdList,self.nodesList,idNode)
            wayNodesList.append(node)
            # node.addWayCount()      #+1 in the way counter


        # Add the last way
        idWay=lastRawNode[0]                # All those data are the same for every node in the way
        centerNodeId = lastRawNode[3]
        oneway = lastRawNode[5]
        roundabout = lastRawNode[6]
        maxspeed = lastRawNode[7]
        roadType = lastRawNode[8]
        centerNode=utils.getNodeFromNodeId(self.nodesIdList,self.nodesList,centerNodeId)
        way = Way.Way(idWay,wayNodesList,centerNode,oneway,roundabout,maxspeed,roadType)
        localWaysList.append(way)


        # Add a reference to the road in every node
        for way in localWaysList:
            for node in way.nodes:
                node.addWay(way)


        print("",len(localWaysList)," ways created in ",time.time() - startTimeCreation, "seconds")

        self.waysList=localWaysList

    def resetAllNodes(self):
        # Reset points to allow a new request.
        for node in self.nodesList:
            # reseting the node before every new requests
            node.resetNode()

        print("All nodes ready for a new request")

    def getItinerary(self,startPosition,finishPosition):
        startTime=time.time()

        # Search the closest node to the position
        # Search in the object, the corresponding object


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

            # Get closest crossroad bc the current algorythm use only crossroads and not all node to optimize performance
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
        print("Start and endpoint localised :",interTime);

        startNode = utils.getNodeFromNodeId(self.nodesIdList,self.nodesList,startNodeId)
        finishNode = utils.getNodeFromNodeId(self.nodesIdList,self.nodesList,finishNodeId)

        geoData = search.aStarSearch(startNode,finishNode) #[waypoints, distance]
        # return positionList

        totalTime=time.time()-startTime

        returnObject = {"waypoints":geoData[0],"distance":geoData[1],"calculationTime":totalTime}
        return returnObject


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

    geoDataList = search.aStarSearch(startNodeId,finishNodeId)

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
