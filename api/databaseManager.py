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
        print("Closest Point : ",self.cursor.fetchall())

    def getDownloadPoints(self):
        self.cursor.execute("SELECT * FROM downloadPoints")
        values = self.cursor.fetchall()
        # print(values)
        return values


if __name__ == '__main__' :
    db = DatabaseManager()

    # db.getClosestNodes(49.0478,7.4446)

    node1=Node(1, 49.0478,7.4446)
    node2=Node(2, 49.0278,7.4546)

    way= Way(5,[node1,node2],node1)


    print(way)
