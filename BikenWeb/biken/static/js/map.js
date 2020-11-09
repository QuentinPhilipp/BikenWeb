var mymap = L.map("mapid", { zoomControl: false }).setView(
  [48.8589507, 2.2770202],
  10
);
debugState = false;
routeList = [];
displayedPolyline = "";
currentDistance = 0;
currentDuration = 0;

L.tileLayer(
  "https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}",
  {
    attribution:
      'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: "mapbox/streets-v11",
    tileSize: 512,
    zoomOffset: -1,
    accessToken:
      "pk.eyJ1IjoiYmlrZW5kZXYiLCJhIjoiY2tndXZ6ZG1sMHo5ODJ6cDlmZjFoMWdheSJ9.Z8rE4hBJxztTXy5EX5mMUw",
  }
).addTo(mymap);

function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(setPosition);
  } else {
    print("User didn't allowed geolocation");
  }
}

function setPosition(position) {
  // Set position only if there is no itinerary requested in URL
  if (window.location.search == "" || window.location.search == undefined) {
    var pos = L.latLng(position.coords.latitude, position.coords.longitude);
    mymap.setView(pos, 10);
  }
}

function displayPolyline(polylineData) {
  var polyline = L.Polyline.fromEncoded(polylineData);
  polyline.setStyle({
    color: "#F67C5A",
  });
  polyline.addTo(mymap);
  routeList.push(polyline);
}

function displayMarker(point) {
  var marker = L.marker(point).addTo(mymap);
  routeList.push(marker);
}

function renderItinerary(itinerary) {
  // Render full polyline
  displayPolyline(itinerary.polyline);

  // Add markers at the beginning and the end
  var coordinates = L.Polyline.fromEncoded(itinerary.polyline).getLatLngs();
  if (itinerary["type"] == "oneway") {
    var start = L.latLng(coordinates[0].lat, coordinates[0].lng);
    var end = L.latLng(
      coordinates[coordinates.length - 1].lat,
      coordinates[coordinates.length - 1].lng
    );

    displayMarker(start);
    displayMarker(end);

    var bounds = L.latLngBounds(start, end);

    mymap.flyToBounds(bounds, {
      animate: true,
      duration: 1,
      padding: [90, 90],
    });

    // getElevation(dataItinerary.polyline);
  } else {
    var start = L.latLng(coordinates[0].lat, coordinates[0].lng);
    var middle = L.latLng(
      coordinates[Math.floor(coordinates.length / 2)].lat,
      coordinates[Math.floor(coordinates.length / 2)].lng
    );

    displayMarker(start);

    var bounds = L.latLngBounds(start, middle);

    mymap.flyToBounds(bounds, {
      animate: true,
      duration: 1,
      padding: [90, 90],
    });
  }
}

getLocation();
