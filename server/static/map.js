
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

  var start = document.getElementById('start').value;
  var finish = document.getElementById('finish').value;

  getLocations(start,finish).then(data =>  {
    console.log(data);
    // check if itinerary or route
    if (getRequestType()=="route")
    {
      var distance = document.getElementById('distanceSlider').value
      var url = "api/1.0/route?start="+startCoords+"&distance="+distance;
    }
    else {
      var url = "api/1.0/itinerary?coords="+data;
    }


      var xhttp = new XMLHttpRequest();

      xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
          var response = JSON.parse(xhttp.responseText);
          var startPos = response.data.startPos;
          var finishPos = response.data.finishPos;
          var distance = response.distance;
          var waypoints = response.data.waypoints;
          var calculationTime = response.calculationTime;

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

          document.getElementById("total-distance").innerHTML = "Total distance : "+distance+"km";
          document.getElementById("itineraryTime").innerHTML ="Route calculated in "+calculationTime+" s";

          document.getElementById("total-distance").hidden=false;
          document.getElementById("itineraryTime").hidden=false;
          document.getElementById("").hidden=false;

        }
      };
      xhttp.open("GET", url, true);
      xhttp.send();
  });
}


async function getLocations(location1,location2){
  var endpoint = "https://nominatim.openstreetmap.org/search/"
  var query1 = endpoint+location1+"?format=json&limit=1"
  var query2 = endpoint+location2+"?format=json&limit=1"
  console.log("query1:",query1);
  console.log("query2:",query2);
  let response1 = await fetch(query1);
  let response2 = await fetch(query2);

  let data1 = await response1.json();
  let data2 = await response2.json();

  var coords = ""+data1[0].lat+","+data1[0].lon+";"+data2[0].lat+","+data2[0].lon

  return coords
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
