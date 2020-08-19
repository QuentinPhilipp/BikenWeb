
var mymap = L.map('mapid',{ zoomControl: false }).setView([48.8589507,2.2770202], 10);
debugState = false;
squareList = [];
routeList = [];
currentDistance = 0;
currentDuration = 0;

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

function saveItinerary() {

  if (routeList.length==0) {
    alert("You need to create an itinerary before saving")
  }

  routeList.forEach((route, i) => {

    if (route._path!=undefined) {
      console.log(route._latlngs);

      var waypointsList = ["12;23","45;56","78;91"];
      $.post( "/api/1.0/save", {
          waypoints: JSON.stringify(route._latlngs),
          distance: currentDistance,
          duration: currentDuration,
      });
    }

  });

}


function sendRequest() {

  var start = document.getElementById('start').value;
  var finish = document.getElementById('finish').value;
  var distance = document.getElementById('distance').value;
  var url = "";


  if (getRequestType()=="route")
  {
    finish = "None";
  }


  getLocations(start,finish).then(data =>  {
    // check if itinerary or route

    if (getRequestType()=="itinerary")
    {
      url = "api/1.0/itinerary?coords="+data;
      getItinerary(url).then(dataItinerary => {

        // Remove old routes
        routeList.forEach((route, i) => {
              route.remove();
        });

        // display the cursor at the start and finish position
        displayStartFinish([dataItinerary.data.startPos,dataItinerary.data.finishPos]);

        // display the new route
        displayRoute(dataItinerary.data.waypoints);



        showSummary(dataItinerary);

      });
    }
    else {
      url = "api/1.0/route?start="+data+"&distance="+distance;
      // console.log('Not implemented',url);
      getItinerary(url).then(dataItinerary => {

        // Remove old routes
        routeList.forEach((route, i) => {
              route.remove();
        });

        // Display start point
        startPoint = {lat : dataItinerary.data.waypoints[0][0],lon : dataItinerary.data.waypoints[0][1]}
        displayStart(startPoint)
        // display the new route
        displayRoute(dataItinerary.data.waypoints);

        showSummary(dataItinerary);

        // Fit the itinerary in the screen
        fitItinerary(dataItinerary.data.waypoints);

      });
    }

  });
}

function closeInfo() {
  document.getElementById("info-bottom").hidden = true;
}


function showSummary(data) {
  console.log(data);
  document.getElementById("info-bottom").hidden = false;
  var distance = data.distance;
  var estimatedTime = data.duration;


  currentDistance=distance;
  currentDuration=estimatedTime;

  // Display the distance and calculation time
  document.getElementById("itinerary-distance").innerHTML = "Total distance: "+distance+" km";
  document.getElementById("itinerary-time").innerHTML = "Estimated time: "+timeConvert(estimatedTime);

}


function timeConvert(n) {
var num = n;
var hours = (num / 60);
var rhours = Math.floor(hours);
var minutes = (hours - rhours) * 60;
var rminutes = Math.round(minutes);
var str = "" + rhours;

if (rhours>1) {
  str += " hours and ";
}
else {
  str += " hour and ";
}
if (rminutes>1) {
  str += rminutes + " minutes";
}
else {
  str += rminutes + "minute";
}
return str;
}

async function getItinerary(url){
  let response = await fetch(url);

  let data = await response.json();

  return data
}


async function getLocations(location1,location2){
  if (location2 != "None") {
    var endpoint = "https://nominatim.openstreetmap.org/search/";
    var query1 = endpoint+location1+"?format=json&limit=1";
    var query2 = endpoint+location2+"?format=json&limit=1";
    let response1 = await fetch(query1);
    let response2 = await fetch(query2);

    let data1 = await response1.json();
    let data2 = await response2.json();

    var coords = ""+data1[0].lat+","+data1[0].lon+";"+data2[0].lat+","+data2[0].lon;
    return coords;
  }
  else {
    // Route mode
    var endpoint = "https://nominatim.openstreetmap.org/search/";
    var query1 = endpoint+location1+"?format=json&limit=1";
    let response1 = await fetch(query1);
    let data1 = await response1.json();
    var coords = ""+data1[0].lat+","+data1[0].lon;
    return coords;

  }

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


function displayStart(point) {
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
  console.log("Fit",waypoints);



  // Get 6 points splited on the itinerary

  var waypointsLen = waypoints.length;

  console.log("waypoints :",waypointsLen);

  var coords0 = waypoints[0];
  var coords1 = waypoints[parseInt(waypointsLen/6)];
  var coords2 = waypoints[parseInt(2*waypointsLen/6)];
  var coords3 = waypoints[parseInt(3*waypointsLen/6)];
  var coords4 = waypoints[parseInt(4*waypointsLen/6)];
  var coords5 = waypoints[parseInt(5*waypointsLen/6)];


  // var marker0 = L.marker([coords0[0], coords0[1]]).addTo(mymap);
  // var marker1 = L.marker([coords1[0], coords1[1]]).addTo(mymap);
  // var marker2 = L.marker([coords2[0], coords2[1]]).addTo(mymap);
  // var marker3 = L.marker([coords3[0], coords3[1]]).addTo(mymap);
  // var marker4 = L.marker([coords4[0], coords4[1]]).addTo(mymap);
  // var marker5 = L.marker([coords5[0], coords5[1]]).addTo(mymap);


  //get the max distance between all the coords
  var distance1 = distance(coords0[0],coords0[1],coords3[0],coords3[1]);
  var distance2 = distance(coords1[0],coords1[1],coords4[0],coords4[1]);
  var distance3 = distance(coords2[0],coords2[1],coords5[0],coords5[1]);

  console.log("Distance 1:",distance1);
  console.log("Distance 2:",distance2);
  console.log("Distance 3:",distance3);


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

  // var corner1 = L.latLng(pointList[0].lat, pointList[0].lon);
  // var corner2 = L.latLng(pointList[1].lat, pointList[1].lon);
  // var bounds = L.latLngBounds(corner1, corner2);

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
