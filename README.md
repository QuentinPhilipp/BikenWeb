# BikenAPI
REST-API in Python for Biken

Set up Flask like in this tutorial : https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask

run python3 api.py

If start and finish is an address
  Itinerary : http://127.0.0.1:5000/api/1.0/itinerary?start={startPoint}&finish={endPoint}
  Route : http://127.0.0.1:5000/api/1.0/route?start={startPoint}&distance={km}

If start and finish are latitude and longitude</h3>
  Itinerary : http://127.0.0.1:5000/api/1.0/itinerary?startPos=48.577043,7.759002&finishPos={endPoint}
  Route : http://127.0.0.1:5000/api/1.0/route?startPos=48.577043,7.759002&distance={km}
  
Those endpoint just return basic information. 
