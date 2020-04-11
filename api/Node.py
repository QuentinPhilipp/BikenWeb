from math import inf


class Node(object):
    """Represent a OSM node. Some attribute are used for Djikstra algorythm"""

    def __init__(self, id, lat, lon):
        self._id = id
        self._latitude = lat
        self._longitude = lon
        self._distanceToGoal = inf
        self._distanceFromStart = inf
        self._distanceTotal = inf
        self._precedingNode = 0
        self._marque = False
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


    # DistanceFromStart
    @property
    def distanceFromStart(self):
        return self._distanceFromStart
    
    @distanceFromStart.getter
    def distanceFromStart(self):
        return self._distanceFromStart  
    
    @distanceFromStart.setter
    def distanceFromStart(self,value):
        self._distanceFromStart = value

    # DistanceToGoal
    @property
    def distanceToGoal(self):
        return self._distanceToGoal
    
    @distanceToGoal.getter
    def distanceToGoal(self):
        return self._distanceToGoal  
    
    @distanceToGoal.setter
    def distanceToGoal(self,value):
        self._distanceToGoal = value

    # DistanceTotal
    @property
    def distanceTotal(self):
        return self._distanceTotal
    
    @distanceTotal.getter
    def distanceTotal(self):
        return self._distanceTotal  
    
    @distanceTotal.setter
    def distanceTotal(self,value):
        self._distanceTotal = value

    # Preceding Node
    @property
    def precedingNode(self):
        return self._precedingNode

    @precedingNode.getter
    def precedingNode(self):
        return self._precedingNode

    @precedingNode.setter
    def precedingNode(self,value):
        self._precedingNode = value


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
    def ways(self):
        return self._ways

    @ways.getter
    def ways(self):
        return self._ways

    # Methods

    def addWay(self, way):
        self._ways.append(way)

