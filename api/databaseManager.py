import sqlite3


class DatabaseManager():
    """The datamanager contain all the useful
     function to link the program
     with the database"""

    def __init__(self):
        self.path = "../data/Database.db"
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()
        print("Database manager created")


    def getData(self):
        for id in self.cursor.execute("SELECT DISTINCT id_node FROM roads ORDER BY id_node"):
            print(id)


    def getClosestNodes(self):
        # self.cursor.execute("SELECT * FROM roads ORDER BY (ABS(49.000-latitude)+ABS(7.378850-longitude)) LIMIT 1")
        self.cursor.execute("SELECT id_node,latitude,longitude FROM roads ORDER BY ABS(-4.624981-longitude) LIMIT 1")
        print("Closest longitude to -4.624981 : ",self.cursor.fetchall())

        self.cursor.execute("SELECT id_node,latitude,longitude FROM roads ORDER BY ABS(48.3851639-latitude) LIMIT 1")
        print("Closest latitude to : 48.3851639",self.cursor.fetchall())


        self.cursor.execute("""
        SELECT id_node,latitude,longitude FROM roads
        ORDER BY (((48.3851642-latitude)*(48.3851642-latitude)) + ((-4.624976-longitude)*(-4.624976-longitude)))
        LIMIT 1
        """)
        print("Closest Point : ",self.cursor.fetchall())

    def getClosestNodesTest(self):
        # self.cursor.execute("SELECT * FROM roads ORDER BY (ABS(49.000-latitude)+ABS(7.378850-longitude)) LIMIT 1")
        self.cursor.execute("SELECT id_node,latitude,longitude FROM roads ORDER BY ABS(7.4446-longitude) LIMIT 1")
        print("Closest longitude to 7.4446 : ",self.cursor.fetchall())

        self.cursor.execute("SELECT id_node,latitude,longitude FROM roads ORDER BY ABS(49.0478-latitude) LIMIT 1")
        print("Closest latitude to : 49.0478",self.cursor.fetchall())


        self.cursor.execute("""
        SELECT id_node,latitude,longitude FROM roads
        ORDER BY (((49.043658-latitude)*(49.043658-latitude)) + ((7.427702-longitude)*(7.427702-longitude)))
        LIMIT 1
        """)
        print("Closest Point : ",self.cursor.fetchall())


    def getDownloadPoints(self):
        self.cursor.execute("SELECT * FROM downloadPoints")
        values = self.cursor.fetchall()
        # print(values)
        return values


if __name__ == '__main__' :
    db = DatabaseManager()
    db.getClosestNodesTest()
