from math import cos,pi

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
    print(type(originalLat))
    print(type(kmToAdd))
    # +km go north, -km go south
    return originalLat + kmToAdd/111.1  #almost 111km everywhere on the planet

def addKmToLongitude(originalLat,originalLon,kmToAdd):
    print(type(originalLat))
    print(type(originalLon))
    print(type(kmToAdd))
    # +km go east  -km go west
    r_earth = 6378
    return originalLon + (kmToAdd / r_earth) * (180 / pi) / cos(originalLat *pi/180) #longitude to km depend on the latitude. 111km at equador but 0 in the pole
