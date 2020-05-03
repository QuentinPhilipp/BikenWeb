
# Biken Web

Web version of Biken in Python using Flask. Biken was a school project of pathfinding. This was originally a software in C++ using Qt. This project is to transform the old project into a web based application.



# Development instruction

Install requirements. 
> pip3 install -r requirements.txt

To start the server, execute 
> python3 api.py

The local web interface is located in http://127.0.0.1:6060
The online version is http://176.31.51.157:6060

Request are working only in all downloaded tiles. Check if the city you want to request is in the downloaded data by clicking on the debug button on the interface. Downloaded tiles appear in green. To modify which tiles should be downloaded, check the section "Database generation"

## Endpoint

We call **Itinerary** a path between two town and **Route** a circular path that goes back to the start point after n km

 - Itinerary : /api/1.0/itinerary?start={start}&finish={destination}
 - Route /api/1.0/route?start={start}&distance={km}


## Database generation

 - Select which tiles should be downloaded : 

> Edit data/tiles.json and put download:1 to all tiles you need
 - Build the database :
> python3 generateDatabase.py

 - clean the database :
>  python3 generateDatabase.py clear

