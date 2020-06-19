import time
import utils
import Node
import Way


def aStarSearch(startNode,endNode):
    # The set of discovered nodes that may need to be (re-)expanded.
    # Initially, only the start node is known.
    # This is usually implemented as a min-heap or priority queue rather than a hash-set.

    startTimeASearch=time.time()

    openSet = [startNode]

    # List of nodes already discovered and explored.
    # Starts off empty
    # Once a node has been 'current' it then goes here
    closeSet = []


    # For node n, cameFrom[n] is the node immediately preceding it on the cheapest path from start
    # to n currently known.
    cameFrom = []

    startNode.distanceFromStart = 0

    startNode.distanceTotalEstimated = utils.distanceBetween(startNode,endNode)

    while openSet:
        current = utils.smallestDistanceToGoalInList(openSet)

        if current==endNode:
            totalTimeASearch=time.time()-startTimeASearch

            print("Route found in",totalTimeASearch,"secondes ")
            itinerarySize = endNode.distanceFromStart
            return [utils.reconstruct_path(endNode,startNode),itinerarySize]

        closeSet.append(current)

        openSet.remove(current)

        for neighbor in current.getNeighbor():
            # d(current,neighbor) is the weight of the edge from current to neighbor
            # tentative_gScore is the distance from start to the neighbor through current
            nextDistanceFromStart = current.distanceFromStart + utils.distanceBetween(current, neighbor)

            if nextDistanceFromStart<neighbor.distanceFromStart:
                neighbor.precedingNode = current
                neighbor.distanceFromStart=nextDistanceFromStart
                neighbor.distanceTotal = neighbor.distanceFromStart + utils.distanceBetween(neighbor,endNode)
                if neighbor not in closeSet :
                    openSet.append(neighbor)


    print("End not reached")
