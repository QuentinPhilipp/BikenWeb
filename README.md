# Biken API

REST API in Python Flask for Biken, a school project of pathfinding. This was originally a software in C++ using Qt. This project is to transform the old project into a web based application.



# Development instruction

Setup Flask : [Setup Flask for a Python API](https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask)

Install flask_cors module. 
> pip3 install -U flask-cors

To start the server, execute 
> python3 api/api.py

The web interface is located in frontend/index.html

## Request

Currently the only request available from the interface is : Enter a start and finish point (name of the city) and the interface will put a marker on those location on the map

## Endpoint

We call **Itinerary** a path between two town and **Route** a circular path that goes back to the start point after n km

When you specify an address :
 - Itinerary : http://127.0.0.1:5000/api/1.0/itinerary?start={startPoint}&finish={endPoint}
 - Route http://127.0.0.1:5000/api/1.0/route?start={startPoint}&distance={km}

If start and finish are latitude and longitude 

 - Itinerary :  http://127.0.0.1:5000/api/1.0/itinerary?startPos=48.577043,7.759002&finishPos={endPoint}
 - Route :http://127.0.0.1:5000/api/1.0/route?startPos=48.577043,7.759002&distance={km}

## Database generation

 - Select which department should be downloaded : 

> Edit data/departements.json and put download:1 to all department you need
 - Build the database :
> python3 generateDatabase.py

 - clean the database :
>  python3 generateDatabase.py clear

