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
  var pos = L.latLng(position.coords.latitude, position.coords.longitude);
  mymap.setView(pos, 10);
}

getLocation();

function createChart(data) {
  document.getElementById("elevation-container").hidden = false;
  new Chart(document.getElementById("elevationChart"), {
    type: "line",
    data: {
      labels: data.profile,
      datasets: [
        {
          data: data.profile,
          borderColor: "#3e95cd",
          fill: false,
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      scales: {
        xAxes: [
          {
            ticks: {
              display: false, //this will remove the label
            },
            gridLines: {
              display: false,
            },
          },
        ],
        yAxes: [
          {
            gridLines: {
              display: false,
            },
          },
        ],
      },
      legend: {
        display: false,
      },
      elements: {
        point: {
          radius: 0,
        },
      },
    },
  });
}

async function getElevation(itinerary) {
  var alertContainer = document.getElementById("alertContainer");

  $.post(
    "/routing/elevation",
    {
      waypoints: JSON.stringify(itinerary),
    },
    function (data, status) {
      console.log(data);
      if (data.profile.length > 0) {
        createChart(data);
      } else {
        alertContainer.innerHTML =
          '<div class="alert warning">This itinerary is too long to get the elevation</div>';
        setTimeout(function () {
          alertContainer.innerHTML = "";
        }, 2000);
      }
    }
  );
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
  displayPolyline(itinerary.polyline);

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
    displayMarker(coordinates[0]);
  }
}
