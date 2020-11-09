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
  var itineraryID = sessionStorage.getItem("itineraryID");

  sendDataForSave("/save", {
    itineraryID: itineraryID,
  }).then((data) => {
    if (data.error == "notLoggedIn") {
      window.location.href = window.origin + "/login";
    } else {
      showError("Saved", 1000, "success");
    }
  });
}

async function sendDataForSave(url = "", data = {}) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return response.json(); // parses JSON response into native JavaScript objects
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
      window.location.origin +
      "/plan/itinerary?start=" +
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
      window.location.origin +
      "/plan/itinerary?start=" +
      startInput.value +
      "&destination=" +
      destinationInput.value +
      "&distance=" +
      distanceInput.value +
      "&type=round&render=false";

    let response = await fetch(url);
    await response.json().then((dataItinerary) => {
      // Store locally the itinerary ID
      sessionStorage.setItem("itineraryID", dataItinerary["uniqueId"]);

      renderItinerary(dataItinerary);

      console.log(dataItinerary);
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
  url = window.location.origin + "/plan/elevation?id=" + itineraryID;

  let response = await fetch(url);

  try {
    await response.json().then((elevationData) => {
      if (elevationData.profile.length > 0) {
        createChart(elevationData);
      } else {
        console.log("Error while getting elevation");
      }
    });
  } catch (error) {
    console.log("Error while getting elevation");
  }
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

function shareItinerary() {
  var popupShare = document.getElementById("share-menu");
  popupShare.hidden = false;

  // Test
  // sessionStorage.setItem("itineraryID", "ugex4r1UMjKA29E0");

  // Write the current url
  var myInput = document.getElementById("urlCopyInput");
  myInput.value =
    window.location.origin +
    "/home?itinerary=" +
    sessionStorage.getItem("itineraryID");

  // Set the sharing links
  // Whatsapp
  var whatsappLink = document.getElementById("whatsapp-redirect");
  var text = "Check this itinerary I made with BikenApp " + myInput.value;
  whatsappLink.href = "https://web.whatsapp.com/send?text=" + encodeURI(text);

  // Twitter
  var twitterLink = document.getElementById("twitter-redirect");
  var text = "Check this itinerary I made with BikenApp " + myInput.value;
  twitterLink.href = "https://twitter.com/intent/tweet?text=" + encodeURI(text);
}

function copyOnClick() {
  /* Get the text field */
  var copyText = document.getElementById("urlCopyInput");
  /* Select the text field */
  copyText.select();
  copyText.setSelectionRange(0, 99999); /*For mobile devices*/

  /* Copy the text inside the text field */
  document.execCommand("copy");
  var copyButton = document.getElementById("copyButton");
  copyButton.innerHTML = "Copied!";
}

function closeShareMenu() {
  document.getElementById("share-menu").hidden = true;
}

// shareItinerary();
