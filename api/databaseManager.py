import sqlite3
import time
from Node import *
from Way import *


class DatabaseManager():
    """The datamanager contain all the useful
     function to link the program
     with the database"""

    def __init__(self):
        self.path = "../data/Database.db"
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()


    def getData(self):
        for id in self.cursor.execute("SELECT DISTINCT id_node FROM roads ORDER BY id_node"):
            print(id)

    def getClosestNodes(self,lat,lon):

        self.cursor.execute("""
        SELECT id_node,latitude,longitude FROM roads
        ORDER BY (((?-latitude)*(?-latitude)) + ((?-longitude)*(?-longitude)))
        LIMIT 1
        """,(lat,lat,lon,lon,))
        point = self.cursor.fetchall()
        # print("Closest Point : ",point)
        return point

    def getDownloadPoints(self):
        self.cursor.execute("SELECT * FROM downloadPoints")
        values = self.cursor.fetchall()
        # print(values)
        return values

    def getAllDataDB(self):
        self.cursor.execute("""SELECT DISTINCT * FROM roads""")
        return self.cursor.fetchall()


    def getAllNodeInBoundingBox(self,north,west,south,east):
        self.cursor.execute("""
        SELECT DISTINCT id_node,latitude,longitude FROM roads
        WHERE (latitude<?) AND (latitude>?) AND (longitude>?) AND (longitude<?)
        ORDER BY id_node
        """,(north,south,west,east,))
        return self.cursor.fetchall()


    def getAllWayInBoundingBox(self,north,west,south,east):
        self.cursor.execute("""
        SELECT DISTINCT id_way,centerLat,centerLon,id_node_center,id_node,oneway,roundabout,maxspeed,type,latitude,longitude FROM roads
        WHERE (centerLat<?) AND (centerLat>?) AND (centerLon>?) AND (centerLon<?)
        ORDER BY id_way
        """,(north,south,west,east,))
        return self.cursor.fetchall()



if __name__ == '__main__' :
    db = DatabaseManager()


    startTimeB = time.time()
    data = db.getAllWayInBoundingBox(49.278,6.55,48.6723,7.7917)
    interTimeB = time.time()-startTimeB
    print("size of data : ", len(data))    
    finalTimeB = time.time()-interTimeB
    print("In : ",interTimeB,"s for request and ", finalTimeB,"s for display")

