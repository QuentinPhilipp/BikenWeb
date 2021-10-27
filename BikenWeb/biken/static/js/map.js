var mymap = L.map("mapid", { zoomControl: false }).setView(
  [48.8589507, 2.2770202],
  10
);
debugState = false;
routeList = [];
polyline = L.polyline([]);
markers = []
currentDistance = 0;
currentDuration = 0;

L.tileLayer(
  "https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}",
  {
    attribution:
      'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: "mapbox/outdoors-v11",
    tileSize: 512,
    zoomOffset: -1,
    accessToken:
      "pk.eyJ1IjoiYmlrZW5kZXYiLCJhIjoiY2tndXZ6ZG1sMHo5ODJ6cDlmZjFoMWdheSJ9.Z8rE4hBJxztTXy5EX5mMUw",
  }
).addTo(mymap);

console.log(mymap);

polyline.on("click", function(e){
  var mp = new L.Marker([e.latlng.lat, e.latlng.lng]).addTo(mymap);
});

function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(setPosition);
  } else {
    print("User didn't allowed geolocation");
  }
}


function clearRoute() {
  // Remove all routes from map
  for (i in mymap._layers) {
    if (
      mymap._layers[i]._bounds != undefined ||
      mymap._layers[i]._latlng != undefined
    ) {
      try {
        mymap.removeLayer(mymap._layers[i]);
      } catch (e) {
        console.log("problem with " + e + mymap._layers[i]);
      }
    }
  }

  markers.forEach(function(marker){
    marker.addTo(mymap);
  })
}

function setPosition(position) {
  // Set position only if there is no itinerary requested in URL
  if (window.location.search == "" || window.location.search == undefined) {
    var pos = L.latLng(position.coords.latitude, position.coords.longitude);
    mymap.setView(pos, 10);
  }
}

function displayPolyline(polylineData) {
  polyline = L.Polyline.fromEncoded(polylineData);
  polyline.setStyle({
    color: "#fa5514",
  });
  polyline.addTo(mymap);
}

function addWaypoints(point) {
  console.log(point);
  var marker = L.marker(point, {draggable: 'true'});
  marker.addTo(mymap);
  marker.on("dragend", function(e) {
    console.log("Recalculate itinerary");
    var position = marker.getLatLng();
    console.log(position);
    recalculateItinerary(marker.lat, marker.lon);
  })
  markers.push(marker)

  // marker.on('dragend', function(event){
  //   var marker_ = event.target;
  //   var position = marker_.getLatLng();
  //   marker_.setLatLng(new L.LatLng(position.lat, position.lng),{draggable:'true'});
  //   mymap.panTo(new L.LatLng(position.lat, position.lng))
  // });
}

async function recalculateItinerary() { 
  var radio1 = document.getElementById("radio1-label");

  if (radio1.classList.contains("active")) {
    // Oneway
    url =window.location.origin + "/plan/itinerary?render=false&type=oneway&waypoints=" 

    markers.forEach(function(marker) {
      var position = marker.getLatLng();
      url += position.lat + ";" + position.lng + "/"
    });
  }
  else
  {
    // Round trip
    url =window.location.origin + "/plan/recalculateItinerary?waypoints=" 

    markers.forEach(function(marker) {
      var position = marker.getLatLng();
      url += position.lat + ";" + position.lng + "/"
    });

  }
    let response = await fetch(url);
    await response.json().then((dataItinerary) => {
      // Store locally the itinerary ID
      sessionStorage.setItem("itineraryID", dataItinerary["uniqueId"]);

      renderItinerary(dataItinerary, waypointsRendering=false);

      // Show elevation, distance and time
      showItineraryDetail(dataItinerary);
    });
}

function renderItinerary(itinerary, waypointsRendering=true) {
  // Render full polyline
  clearRoute()
  displayPolyline(itinerary.polyline);

  console.log("Itinerary type: ", itinerary["type"]);

  // Add markers at the beginning and the end
  var coordinates = L.Polyline.fromEncoded(itinerary.polyline).getLatLngs();
  if (itinerary["type"] == "oneway") {
    var start = L.latLng(coordinates[0].lat, coordinates[0].lng);
    var end = L.latLng(
      coordinates[coordinates.length - 1].lat,
      coordinates[coordinates.length - 1].lng
    );

    if (waypointsRendering == true) {
      addWaypoints(start);
      addWaypoints(end);
          
      var bounds = L.latLngBounds(start, end);

      mymap.flyToBounds(bounds, {
        animate: true,
        duration: 1,
        padding: [90, 90],
      });
    }

  } else {
    console.log(itinerary);

    var start = L.latLng(coordinates[0].lat, coordinates[0].lng);
    var middle = L.latLng(
      coordinates[Math.floor(coordinates.length / 2)].lat,
      coordinates[Math.floor(coordinates.length / 2)].lng
    );

    if (waypointsRendering == true) {
      itinerary.waypoints.forEach(element => {
        addWaypoints(element)
      });
          
      var bounds = L.latLngBounds(start, middle);

      mymap.flyToBounds(bounds, {
        animate: true,
        duration: 1,
        padding: [90, 90],
      });
    }

  }
}

getLocation();
