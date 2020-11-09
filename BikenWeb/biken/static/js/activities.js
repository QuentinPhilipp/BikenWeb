function convertStravaActivity(polyline, distance, time) {
  sendDataToConvert("/convertToItinerary", {
    polyline: polyline,
    distance: distance,
    time: time,
    gpx: false,
    name: "None",
  }).then((data) => {
    // redirect to home page with itinerary ID in parameter
    window.location =
      window.location.origin + "/home?itinerary=" + data["itineraryID"];
  });
}

// Example POST method implementation:
async function sendDataToConvert(url = "", data = {}) {
  // Default options are marked with *
  const response = await fetch(url, {
    method: "POST", // *GET, POST, PUT, DELETE, etc.
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return response.json(); // parses JSON response into native JavaScript objects
}

function convertStravaActivityToGPX(polyline, distance, time, name) {
  // Request GPX file instead of itinerary ID
  sendDataToConvert("/convertToItinerary", {
    polyline: polyline,
    distance: distance,
    time: time,
    gpx: true,
    name: name,
  }).then((data) => {
    // Download the file
    if (data.success == true) {
      var fileUrl = window.location.origin + "/" + data.filename;
      window.open(fileUrl);
    } else {
      showError("Fail to create GPX file", 1500, "warning");
    }
  });
}
