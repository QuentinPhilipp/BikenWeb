from math import inf


class Node(object):
    """Represent a OSM node. Some attribute are used for Djikstra algorythm"""

    def __init__(self, id, lat, lon):
        self._id = id
        self._latitude = lat
        self._longitude = lon
        self._distance = inf
        self._precedingNodeId = 0
        self._marque = False
        self._numberOfWays = 0
        self._ways = []


       # Getter and setter
    # ID
    @property
    def id(self):
        return self._id

    @id.getter
    def id(self):
        return self._id

    # Latitude
    @property
    def latitude(self):
        return self._latitude
    
    @latitude.getter
    def latitude(self):
        return self._latitude
   
    # Longitude
    @property
    def longitude(self):
        return self._longitude
    
    @longitude.getter
    def longitude(self):
        return self._longitude


    # Distance
    @property
    def distance(self):
        return self._distance
    
    @distance.getter
    def distance(self):
        return self._distance  
    
    @distance.setter
    def distance(self,value):
        self._distance = value


    # Preceding Node
    @property
    def precedingNodeID(self):
        return self._precedingNodeID

    @precedingNodeID.getter
    def precedingNodeID(self):
        return self._precedingNodeID

    @precedingNodeID.setter
    def precedingNodeID(self,value):
        self._precedingNodeID = value


    # Marque
    @property
    def marque(self):
        return self._marque
    
    @marque.getter
    def marque(self):
        return self._marque  
    
    @marque.setter
    def marque(self,value):
        self._marque = value


    #  Number of Ways
    @property
    def numberOfWays(self):
        return self._numberOfWays

    @numberOfWays.getter
    def numberOfWays(self):
        return self._numberOfWays

    @numberOfWays.setter
    def numberOfWays(self,value):
        self._numberOfWays = value

    #  Number of Ways
    @property
    def ways(self):
        return self._ways

    @ways.getter
    def ways(self):
        return self._ways

    # Methods

    def addWay(self, way):
        self._ways.append(way)


    def addWayCount(self):
        self._numberOfWays += 1
