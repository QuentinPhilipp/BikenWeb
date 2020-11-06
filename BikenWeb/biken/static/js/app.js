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

  // ,
  // function(data, status){
  //   console.log(status);
  //   if (data["text"]=="OK") {
  //     console.log("Save to the profile");
  //   }
  //   else if (data["text"]=="Fail") {
  //     console.log("Failed to save to the profile");
  //   }
  //   else {
  //     console.log("Unkown error");
  //   }
  // });
}

async function exportGPX() {
  console.log("Export GPX");

  url =
    "getGPX?itinerary=" +
    sessionStorage.getItem("itineraryID") +
    "&name=" +
    sessionStorage.getItem("itineraryID");
  let response = await fetch(url);
  await response.json().then((gpxData) => {
    if (gpxData.success == true) {
      console.log("Success to create GPX file");
      var fileUrl = window.location.href + gpxData.filename;
      window.open(fileUrl);
    } else {
      console.log("Fail to create GPX file");
    }
  });
}

async function requestItinerary() {
  var startInput = document.getElementById("start");
  var destinationInput = document.getElementById("finish");
  var distanceInput = document.getElementById("distance");
  var radio1 = document.getElementById("radio1-label");

  console.log(radio1.classList);

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
      console.log(dataItinerary);

      // Store locally the itinerary ID
      sessionStorage.setItem("itineraryID", dataItinerary["uniqueId"]);

      renderItinerary(dataItinerary);

      //   // Query elevation of this path to the server
      //   getElevation(dataItinerary.polyline)

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

      //   // Query elevation of this path to the server
      //   getElevation(dataItinerary.polyline)

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

  // TOFIX

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
