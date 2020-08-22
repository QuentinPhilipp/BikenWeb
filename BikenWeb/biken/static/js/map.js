
var mymap = L.map('mapid',{ zoomControl: false }).setView([48.8589507,2.2770202], 10);
debugState = false;
squareList = [];
routeList = [];
currentDistance = 0;
currentDuration = 0;



function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(setPosition);
  } else {
    print("User didn't allowed geolocation")
  }
}

function setPosition(position) {
  var pos = L.latLng(position.coords.latitude, position.coords.longitude);
  mymap.flyTo(pos,10);
}

getLocation()


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
      return response;
    }
  };
  xhttp.open("GET", query, true);
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

  // Padding to show the itiinerary even with the infos displayed
  mymap.flyToBounds(bounds,{
        animate: true,
        duration: 1,
        padding: [90,90]
});
}


function displayMarker(point) {
  console.log(point);
  var marker = L.marker([point.lat, point.lon]).addTo(mymap);
  routeList.push(marker);
}

function addKmToLatitude(originalLat,kmToAdd) {
    return originalLat + kmToAdd/111.1;
  }

function addKmToLongitude(originalLat,originalLon,kmToAdd) {
    var r_earth = 6378;
    return originalLon + (kmToAdd / r_earth) * (180 / Math.PI) / Math.cos(originalLat *Math.PI/180);
  }



function fitItinerary(waypoints) {
  //Fit an itinerary on the screen


  // Get 6 points splited on the itinerary
  var waypointsLen = waypoints.length;
  var coords0 = waypoints[0];
  var coords1 = waypoints[parseInt(waypointsLen/6)];
  var coords2 = waypoints[parseInt(2*waypointsLen/6)];
  var coords3 = waypoints[parseInt(3*waypointsLen/6)];
  var coords4 = waypoints[parseInt(4*waypointsLen/6)];
  var coords5 = waypoints[parseInt(5*waypointsLen/6)];

  //get the max distance between all the coords
  var distance1 = distance(coords0[0],coords0[1],coords3[0],coords3[1]);
  var distance2 = distance(coords1[0],coords1[1],coords4[0],coords4[1]);
  var distance3 = distance(coords2[0],coords2[1],coords5[0],coords5[1]);

  if (distance1>distance2 && distance1>distance3) {
    var corner1 = L.latLng(coords0[0], coords0[1]);
    var corner2 = L.latLng(coords3[0],coords3[1]);
  }
  else if (distance2>distance1 && distance2>distance3) {
    var corner1 = L.latLng(coords1[0],coords1[1]);
    var corner2 = L.latLng(coords4[0],coords4[1]);
  }
  else {
    var corner1 = L.latLng(coords2[0],coords2[1]);
    var corner2 = L.latLng(coords5[0],coords5[1]);
  }

  var bounds = L.latLngBounds(corner1, corner2);

  // Padding to show the itiinerary even with the infos displayed
  mymap.flyToBounds(bounds,{
        animate: true,
        duration: 1,
        padding: [90,90]
});

}


function distance(lat1, lon1, lat2, lon2) {
  // https://www.geodatasource.com/developers/javascript
	if ((lat1 == lat2) && (lon1 == lon2)) {
		return 0;
	}
	else {
		var radlat1 = Math.PI * lat1/180;
		var radlat2 = Math.PI * lat2/180;
		var theta = lon1-lon2;
		var radtheta = Math.PI * theta/180;
		var dist = Math.sin(radlat1) * Math.sin(radlat2) + Math.cos(radlat1) * Math.cos(radlat2) * Math.cos(radtheta);
		if (dist > 1) {
			dist = 1;
		}
		dist = Math.acos(dist);
		dist = dist * 180/Math.PI;
		dist = dist * 60 * 1.1515;
		dist = dist * 1.609344
		return dist;
	}
}
