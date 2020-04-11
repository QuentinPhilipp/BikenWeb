import databaseManager
import time
import utils
import Node
import Way
from bisect import bisect_left 
from math import pi,cos,sin,sqrt,atan2
from operator import attrgetter

MAX_DISTANCE_FROM_START = 100

class itineraryCreator(object):
    def __init__(self,startLat,startLon):
        self._startLat=startLat
        self._startLon=startLon
        self._nodeList=[]
        self._nodeIdList=[]     #same order than nodeList but contain only id. Faster to iterate
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
        self.nodeList = localNodeList
        self.nodeIdList= localNodeIdList


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
        index = bisect_left(self.nodeIdList, nodeId, lo=0, hi=len(self.nodeIdList))
        return self.nodeList[index]




    def getItinerary(self,startPosition,finishPosition):


        # Search the closest node to the position
        # Look in the database the id of the closest point
        # Search in the object, the corresponding object

        db = databaseManager.DatabaseManager()


        startNodeId = db.getClosestNodes(startPosition["lat"],startPosition["lon"])[0][0]   #[0][0] only take id
        finishNodeId = db.getClosestNodes(finishPosition["lat"],finishPosition["lon"])[0][0]


        print("closest node from start : ",startNodeId)
        print("closest node from end : ",finishNodeId)

        startNodeId = 287305291
        # finishNodeId = 841874221     #work
        # finishNodeId=5843835950      #work
        # finishNodeId=1248703954    #work
        finishNodeId = 2432131729

        # creator.djikstraAlgorythm(startNodeId,finishNodeId)
        geoDataList = self.aStarSearch(startNodeId,finishNodeId)
        # return positionList

        return geoDataList





    def getNodesNearby(self,node):

        nodesNearby = []
        ways = node.ways
        # print("ways of node : ",node.ways)

        for currentWay in ways:
            nodes=currentWay.nodes
            index = self.getPositionInWay(node,currentWay)

            print("scan one way")

            for n in nodes:
                # print("numberOfWays : ",n.numberOfWays, n.id)
                if n.numberOfWays>1 and n.id!=node.id:
                    print("Add node nearby :",n.id)

                    nodesNearby.append(n)

        return nodesNearby


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


    def djikstraAlgorythm(self,startNod,endNod):
        startNodeId = 287305190
        endNodeId = 841874221
        print("\n\n\n Starting Algorythm \n\n\n")

        startItineraryTime = time.time()
        # Node * start = getNodeFromNodeId(startNodeId);
        # Node * finish = getNodeFromNodeId(finishNodeId);

        startNode = self.getNodeFromNodeId(startNodeId);
        endNode = self.getNodeFromNodeId(endNodeId);
        # print("startNode :",startNode.id,startNode.ways)

        # print("Route between node n°", startNode.id,"and node°", endNode.id)

        startNode.distance=0
        nodeToDeal = []

        # print("startNode :",startNode.id,startNode.ways)
       
        nodeToDeal.append(startNode)
        nodesNearby = self.getNodesNearby(nodeToDeal[0])

        # print("currentNode :",nodeToDeal[0].id,nodeToDeal[0].ways)

        # print("Node nearby :",nodesNearby)


        exitFlag = False    #use to get out of encas
        
        # Dijkstra
        while nodeToDeal:           #while not empty
            print("While")
            indexMin = 0

            print("nodeToDeal :",nodeToDeal)

            #which node is the closest to the start
            for i in range(1,len(nodeToDeal)):
                if(nodeToDeal[i].distance<nodeToDeal[indexMin].distance):
                    indexMin=i

            currentNode = nodeToDeal[indexMin]
            nodeToDeal.pop(indexMin)

            
            print("currentNode :")
            displayNode(currentNode)

            if currentNode.id == finishNodeId:
                print("\n\nFOUND\n\n")


            nodesNearby=self.getNodesNearby(currentNode)

            print("Node nearby :")
            for node in nodesNearby:
                print(node.id)
            print("\n")

            currentNode.marque=True

            for node in nodesNearby:
                if node.marque==False:
                    #Pour chacun de ces nodes, on regarde si la distance par rapport au départ en passant par
                    #currentNode est plus petite que l'ancienne distance par rapport au départ (stockée dans le node).
                    distanceBetweenNodes = self.distanceBetween(node,currentNode)
                    if node.distance>currentNode.distance+distanceBetweenNodes:
                        node.distance=currentNode.distance+distanceBetweenNodes
                        node.precedingNodeId=currentNode.id
                        node.marque=True
                        nodeToDeal.append(node)
                        if node.id == finishNodeId:
                            exit==True
                            print("End point reached")


        if exit==True:
            print("End point reached")


        else:
            print("End point not reached")




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
        nodeList = []

        nodeListLatLon = []

        current=endNode
        while current != startNode:
            nodeList.append(current)
            nodeListLatLon.append([current.latitude,current.longitude])
            current=current.precedingNode

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
                return self.reconstruct_path(endNode,startNode)

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

