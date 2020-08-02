
var mymap = L.map('mapid',{ zoomControl: false }).setView([48.8589507,2.2770202], 10);
debugState = false;
squareList = [];
routeList = [];


L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoiYmlrZW5kZXYiLCJhIjoiY2sxeHp3amcwMGdvYTNobDh6Ym55ZW1ibSJ9.lGWM8-RyVB2NoQRSgIL9nQ'
}).addTo(mymap);




function geocode(location)
{
   // This function use nominatim to get the GPS point of an address
  var endpoint = "https://nominatim.openstreetmap.org/search/"
  var query = endpoint+location+"?format=json&limit=1"

  var xhttp = new XMLHttpRequest();

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var responseRaw = JSON.parse(xhttp.responseText);
      var response = ""+responseRaw[0].lat+","+responseRaw[0].lon;
      console.log(response);
      return response;
    }
  };
  xhttp.open("GET", query, true);
  xhttp.send();
}



function sendRequest() {


  // startPos = geocode(start);
  // finishPos = geocode(finish);

  // console.log("Send data");
  // console.log("Start : ",startPos," | Finish : ",finishPos);

  //check if itinerary or route
  var requestType = getRequestType();

  if (requestType=="route")
  {
    var start = document.getElementById('start').value
    var distance = document.getElementById('distanceSlider').value
    var url = "api/1.0/route?start="+start+"&distance="+distance;
  }
  else {
    var start = document.getElementById('start').value
    var finish = document.getElementById('finish').value
    var url = "api/1.0/itinerary?start="+start+"&finish="+finish;
  }

  // var url = "api/1.0/testThread";

  // var xmlHttp = new XMLHttpRequest();
  // xmlHttp.open( "GET", url,true ); // false for synchronous request
  // xmlHttp.send();
  //console.log("API : ",xmlHttp.responseText);

  var xhttp = new XMLHttpRequest();

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var response = JSON.parse(xhttp.responseText);
      var startPos = response.data.startPos;
      var finishPos = response.data.finishPos;
      var distance = response.distance;
      var waypoints = response.data.waypoints;
      var calculationTime = response.calculationTime;
      var geolocalisationTime = response.geolocalisationTime;

      console.log("response : ",response);

      console.log("Start : ",startPos);
      console.log("Finish : ",finishPos);
      console.log("Distance : ",distance);
      console.log("Time : ",calculationTime);



      routeList.forEach((route, i) => {
        route.remove();
      });


      displayStartFinish([startPos,finishPos]);
      displayRoute(waypoints);

      distance = (distance/1000).toFixed(2);
      calculationTime = calculationTime.toFixed(5);
      geolocalisationTime = geolocalisationTime.toFixed(5);

      document.getElementById("total-distance").innerHTML = "Total distance : "+distance+"km";
      document.getElementById("itineraryTime").innerHTML ="Route calculated in "+calculationTime+" s";
      document.getElementById("geolocalisationTime").innerHTML ="Position calculated in "+geolocalisationTime+"s";

      document.getElementById("total-distance").hidden=false;
      document.getElementById("itineraryTime").hidden=false;
      document.getElementById("geolocalisationTime").hidden=false;

    }
  };
  xhttp.open("GET", url, true);
  xhttp.send();


}


function displayRoute(waypoints) {

var polyline = L.polyline(waypoints, {
  color: '#F67C5A',
  weight:6
}).addTo(mymap);
routeList.push(polyline);
}


function displayStartFinish(pointList) {
  pointList.forEach((
    point, i) => {
      var marker = L.marker([point.lat, point.lon]).addTo(mymap);
      routeList.push(marker);

  });

  var corner1 = L.latLng(pointList[0].lat, pointList[0].lon);
  var corner2 = L.latLng(pointList[1].lat, pointList[1].lon);
  var bounds = L.latLngBounds(corner1, corner2);

  mymap.flyToBounds(bounds);
}


function addKmToLatitude(originalLat,kmToAdd) {
    return originalLat + kmToAdd/111.1;
  }

function addKmToLongitude(originalLat,originalLon,kmToAdd) {
    var r_earth = 6378;
    return originalLon + (kmToAdd / r_earth) * (180 / Math.PI) / Math.cos(originalLat *Math.PI/180);
  }









////// DEBUG FUNCTION ///////

function displayDebug() {
  debugState = !debugState;

  if (debugState) {
    console.log("Debug ON")

    displayDownloadedSquares();
    drawAllSquare();

    var corner1 = L.latLng(50.2, -5.7);
    var corner2 = L.latLng(49.5, 9.5);
    var bounds = L.latLngBounds(corner1, corner2);
    mymap.flyToBounds(bounds);
  }
  else {
    console.log("Debug OFF")
    mymap.removeLayer(L);
    squareList.forEach((square, i) => {
      square.remove();
    });

  }
}

function getDownloadPoints() {
  var url = "/api/1.0/debugDownload"
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", url, false ); // false for synchronous request
  xmlHttp.send();
  // console.log("API : ",xmlHttp.responseText);
  var response = JSON.parse(xmlHttp.responseText);
  // console.log(response);
  return response.data
}


function displayDownloadedSquares() {
    var squares = getDownloadPoints();
    squares.forEach((square, i) => {
      addSquare(square.lat,square.lon,"#0ef92c")
    });
  }

function addSquare(lat,lon,colorRectangle="rgba(77, 102, 108, 0.34)") {
  // Draw a square centered on lat,lon
  var squareSize = 70
  lat1 = addKmToLatitude(lat,-squareSize/2)
  lon1 = addKmToLongitude(lat,lon,-squareSize/2)
  lat2 = addKmToLatitude(lat,squareSize/2)
  lon2 = addKmToLongitude(lat,lon,squareSize/2)

  var corner1 = L.latLng(lat1, lon1);
  var corner2 = L.latLng(lat2, lon2);
  var bounds = L.latLngBounds(corner1, corner2);

  var rect = L.rectangle(bounds,{
    color:colorRectangle
  })
  rect.addTo(mymap);
  squareList.push(rect);

}

function drawAllSquare()
{
  var startLat = 50.8;
  var startLon = 7.81;
  var maxLat = 42;
  var maxLon = -5;

  var currentLat = startLat
  var currentLon = startLon
  while (currentLat>maxLat)
  {
    currentLon=startLon;
    while (currentLon>maxLon)
    {
      addSquare(currentLat,currentLon);
      currentLon = addKmToLongitude(currentLat,currentLon,-65);
    }
    currentLat = addKmToLatitude(currentLat,-65);
  }
}
