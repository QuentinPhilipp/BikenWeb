import databaseManager
import time
import utils
import Node
import Way
from bisect import bisect_left 

MAX_DISTANCE_FROM_START = 0.5

class itineraryCreator(object):
    def __init__(self,startLat,startLon):
        self._startLat=startLat
        self._startLon=startLon
        self._nodeList=[]
        self._nodeIdList=[]     #same order than nodeList but contain only id. Faster to iterate
        self._waysList=[]
        self.db = databaseManager.DatabaseManager()
        

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
    def nodeList(self):
        return self._nodeList
    
    @nodeList.getter
    def nodeList(self):
        return self._nodeList  
    
    @nodeList.setter
    def nodeList(self,value):
        self._nodeList = value
    
    # NodeId List
    @property
    def nodeIdList(self):
        return self._nodeIdList
    
    @nodeIdList.getter
    def nodeIdList(self):
        return self._nodeIdList  
    
    @nodeIdList.setter
    def nodeIdList(self,value):
        self._nodeIdList = value

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

        north = utils.addKmToLatitude(self.startLat,MAX_DISTANCE_FROM_START)
        east = utils.addKmToLongitude(self.startLat,self.startLon,MAX_DISTANCE_FROM_START)
        west = utils.addKmToLongitude(self.startLat,self.startLon,-MAX_DISTANCE_FROM_START)
        south = utils.addKmToLatitude(self.startLat,-MAX_DISTANCE_FROM_START)
  
        print(north,west,south,east)

        startTimeFetch = time.time()
        data = self.db.getAllNodeInBoundingBox(north,west,south,east)     
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
        self.nodeList = localNodeList
        self.nodeIdList= localNodeIdList


    def createAllWaysObject(self):
        print("Create Way")

        north = utils.addKmToLatitude(self.startLat,MAX_DISTANCE_FROM_START)
        east = utils.addKmToLongitude(self.startLat,self.startLon,MAX_DISTANCE_FROM_START)
        west = utils.addKmToLongitude(self.startLat,self.startLon,-MAX_DISTANCE_FROM_START)
        south = utils.addKmToLatitude(self.startLat,-MAX_DISTANCE_FROM_START)
        
        print(north,west,south,east)

        startTimeFetch = time.time()
        data = self.db.getAllWayInBoundingBox(north,west,south,east)     
        print("All data fetch from database in ",time.time() - startTimeFetch, "seconds")


        wayNodesList = []  #list of all node in a way
        localWaysList = []      #list of all ways
        crossroadsNodes = []  # List of node who are at least in two roads

        

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
            node.addWayCount()      #+1 in the way counter

            if node.numberOfWays==2:
                crossroadsNodes.append(node)


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
        index = bisect_left(self.nodeIdList, nodeId, lo=0, hi=len(self.nodeIdList))
        return self.nodeList[index]




    def getItinerary(self):
        positionList = []
        for node in self.waysList[0].nodes :
            positionList.append([node.latitude,node.longitude])

        return positionList


    # DEBUG FUNCTION

    def printAllNodes(self):
        print("All nodes :")
        for node in self.nodeList:
            print(node.id, " Latitude: ",node.latitude," Longitude: ",node.longitude," marque: ",node.marque)
    
    def printAllWays(self):
        print("All ways :")
        for way in self.waysList:
            nodeString = ""
            for node in way.nodes:
                nodeString += str(node.id)
                nodeString += "|"
            print(way.id,":",nodeString)

if __name__ == "__main__" :
    creator = itineraryCreator(49.005115, 7.373121)
    creator.createAllNodesObject()
    creator.createAllWaysObject()

    # creator.printAllNodes()
    # creator.printAllWays()

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


