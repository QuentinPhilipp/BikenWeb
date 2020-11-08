var elevationChart;

// submit on "Enter"
$(document).ready(function () {
  $(".submit_on_enter").keydown(function (event) {
    // enter has keyCode = 13, change it if you want to use another button
    if (event.keyCode == 13) {
      this.form.submit();
      return false;
    }
  });
});

function saveItinerary() {
  var dataToSend = sessionStorage.getItem("itineraryID");
  console.log("Data to send:", dataToSend);

  $.ajax({
    url: "/save",
    type: "POST",
    data: { itineraryId: dataToSend },
    dataType: "json",
  });
}

async function requestItinerary() {
  // Clear all the data from previous requests
  clearOldData();

  var startInput = document.getElementById("start");
  var destinationInput = document.getElementById("finish");
  var distanceInput = document.getElementById("distance");
  var radio1 = document.getElementById("radio1-label");

  if (radio1.classList.contains("active")) {
    // Oneway mode
    url =
      window.location.href +
      "plan/itinerary?start=" +
      startInput.value +
      "&destination=" +
      destinationInput.value +
      "&distance=" +
      distanceInput.value +
      "&type=oneway&render=false";

    let response = await fetch(url);
    await response.json().then((dataItinerary) => {
      // Store locally the itinerary ID
      sessionStorage.setItem("itineraryID", dataItinerary["uniqueId"]);

      renderItinerary(dataItinerary);

      // Show elevation, distance and time
      showItineraryDetail(dataItinerary);
    });
  } else {
    // Round mode
    url =
      window.location.href +
      "plan/itinerary?start=" +
      startInput.value +
      "&destination=" +
      destinationInput.value +
      "&distance=" +
      distanceInput.value +
      "&type=round&render=false";

    let response = await fetch(url);
    await response.json().then((dataItinerary) => {
      console.log(dataItinerary);

      // Store locally the itinerary ID
      sessionStorage.setItem("itineraryID", dataItinerary["uniqueId"]);

      renderItinerary(dataItinerary);

      // Show elevation, distance and time
      showItineraryDetail(dataItinerary);
    });
  }
}

// Selector trip type
function selectRoundTrip() {
  var finishInput = document.getElementById("finish");
  var distanceInput = document.getElementById("distance");

  // disable one way
  finishInput.required = false;
  finishInput.hidden = true;

  // Enable round trip
  distanceInput.required = true;
  distanceInput.hidden = false;
}

function selectOneWayTrip() {
  var finishInput = document.getElementById("finish");
  var distanceInput = document.getElementById("distance");

  // disable round trip
  distanceInput.required = false;
  distanceInput.hidden = true;

  // enable one way
  finishInput.required = true;
  finishInput.hidden = false;
}

function toggleIconPanel() {
  console.log("Toggle");
  var toggleButtonUp = document.getElementById("toggleButtonUp");
  var toggleButtonDown = document.getElementById("toggleButtonDown");
  if (toggleButtonUp.hidden) {
    toggleButtonUp.hidden = false;
    toggleButtonDown.hidden = true;
  } else {
    toggleButtonUp.hidden = true;
    toggleButtonDown.hidden = false;
  }
}

function showItineraryDetail(itinerary) {
  document.getElementById("itinerary-details").hidden = false;
  var distance = Math.round(itinerary["distance"] / 10) / 100;
  document.getElementById("kilometer-display").innerHTML = distance + " km";

  // Query elevation of this path to the server
  getElevation(itinerary["uniqueId"]);

  var hours = Math.floor(itinerary["duration"] / 60);
  var minutes = Math.round(itinerary["duration"] % 60);

  if (minutes < 10) {
    // Add 0 before to have always 2 digits for the minutes
    var minutes = "0" + minutes;
  }

  if (hours > 0) {
    var duration = hours + "h" + minutes;
  } else {
    var duration = minutes + " min";
  }
  document.getElementById("duration-display").innerHTML = duration;
}

function createChart(data) {
  document.getElementById("elevation-container").hidden = false;
  elevationChart = new Chart(document.getElementById("elevationChart"), {
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
            ticks: {
              display: true, //this will remove the label
              maxTicksLimit: 4,
              mirror: true,
            },
            gridLines: {
              display: true,
              drawTicks: false,
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

async function getElevation(itineraryID) {
  url = window.location.href + "plan/elevation?id=" + itineraryID;

  let response = await fetch(url);

  await response.json().then((elevationData) => {
    if (elevationData.profile.length > 0) {
      createChart(elevationData);
    } else {
      console.log("Error");
    }
  });
}

async function clearOldData() {
  console.log("Clear old data");
  // clear leaflet map
  clearMap();

  // remove the elevation chart
  elevationChart.destroy();
}

function clearMap() {
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
}
