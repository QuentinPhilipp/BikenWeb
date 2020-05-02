
var mymap = L.map('mapid').setView([48.8589507,2.2770202], 10);

debugState = false;
squareList = [];

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    zoomControl: false,
    accessToken: 'pk.eyJ1IjoiYmlrZW5kZXYiLCJhIjoiY2sxeHp3amcwMGdvYTNobDh6Ym55ZW1ibSJ9.lGWM8-RyVB2NoQRSgIL9nQ'
}).addTo(mymap);


function sendRequest() {
  var start = document.getElementById('start').value
  var finish = document.getElementById('finish').value

  console.log("Send data");
  console.log("Start : ",start," | Finish : ",finish);

  var url = "http://127.0.0.1:5000/api/1.0/itinerary?start="+start+"&finish="+finish


  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", url, false ); // false for synchronous request
  xmlHttp.send();
  //console.log("API : ",xmlHttp.responseText);
  var response = JSON.parse(xmlHttp.responseText);
  var startPos = response.data.startPos;
  var finishPos = response.data.finishPos;
  var finishPos = response.data.finishPos;
  var waypoints = response.data.waypoints;

  console.log("Start : ",startPos);
  console.log("Finish : ",finishPos);
  console.log("Distance : ",response.finishPos);

  console.log("Waypoints : ",waypoints);

  displayStartFinish([startPos,finishPos]);
  displayRoute(waypoints);
}


function displayRoute(waypoints) {

var polyline = L.polyline(waypoints, {
  color: '#F67C5A',
  weight:6
}).addTo(mymap);

}


function displayStartFinish(pointList) {
  pointList.forEach((
    point, i) => {
      var marker = L.marker([point.lat, point.lon]).addTo(mymap);
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
  var url = "http://127.0.0.1:5000/api/1.0/debugDownload"
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
      addSquare(square.lat,square.lon,"#ff0000")
    });
  }

function addSquare(lat,lon,colorRectangle="#3388ff") {
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
