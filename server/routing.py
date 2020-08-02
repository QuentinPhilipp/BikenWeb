import requests
import json
import time



def route(startCoord,endCoord,mode) :

    startLon = startCoord['lon']
    startLat = startCoord['lat']
    endLon = endCoord['lon']
    endLat = endCoord['lat']

    startTime = time.time()

    url = f"https://routing.openstreetmap.de/routed-{mode}/route/v1/driving/{startLon},{startLat};{endLon},{endLat}?overview=false&alternatives=false&steps=true&geometries=geojson"
    print("Url:",url)

    r = requests.get(url)
    data = r.json()
    startWaypoint = data['waypoints'][0]
    endWaypoint = data['waypoints'][1]


    print(f"\nDistance :{data['routes'][0]['distance']} meters")
    print(f"\nDuration :{data['routes'][0]['duration']//60} minutes")



    path = []
    for step in data['routes'][0]["legs"][0]["steps"]:
        path += step["geometry"]["coordinates"]

    print("\nNumber of point in the path :",len(path))

    endTime = time.time()
    print(f"~~~~~~~~~~~~\nTime for the request : {endTime-startTime} seconds")

    # Switch from lon,lat to lat,lon for leaflet
    returnedPath = [(coord[1], coord[0]) for coord in path]
    returnObject = {"waypoints":returnedPath,"distance":data["routes"][0]['distance'],"calculationTime":endTime-startTime}

    return returnObject


if __name__ == '__main__':

    start = {}
    end = {}
    start["lat"] = 48.997893
    start["lon"] = 7.379982
    end["lat"] =48.962728
    end["lon"] = 7.369994

    route(start,end,"bike")
