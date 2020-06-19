
class Way(object):
    """Represent an OSM Way"""

    def __init__(self,id,nodes,centerNode,oneway=False,roundabout=False,maxspeed=0,roadType="None"):
        self._id = id
        self._nodes = nodes
        self._centerNode = centerNode
        self._oneway=oneway
        self._roundabout=roundabout
        self._maxspeed=maxspeed
        self._roadType=roadType

    # Getter and setter
    # ID
    @property
    def id(self):
        return self._id

    @id.getter
    def id(self):
        return self._id

    # Nodes
    @property
    def nodes(self):
        return self._nodes

    @nodes.getter
    def nodes(self):
        return self._nodes

    # CenterNode
    @property
    def centerNode(self):
        return self._centerNode

    @centerNode.getter
    def centerNode(self):
        return self._centerNode

    # Methods

    def getNodePosition(self,node):
        #return the index of a node in a way
        nodes = self.nodes
        wantedId=node.id
        if(nodes[0].id==wantedId):
            return 0
        elif nodes[-1].id == wantedId:
            return len(nodes)-1
        else:
            for i in range(len(nodes)):
                if nodes[i].id==wantedId:
                    return i
