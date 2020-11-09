function convertStravaActivity(polyline, distance, time) {
  console.log("Convert Strava activity to Biken itinerary");
  console.log(polyline);
  console.log(distance);
  console.log(time);

  sendDataToConvert("/convertToItinerary", {
    polyline: polyline,
    distance: distance,
    time: time,
  }).then((data) => {
    console.log(data); // JSON data parsed by `data.json()` call
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

async function renderStravaItinerary(data) {
  console.log("Strava:", data);
}

function convertStravaActivityToGPX() {
  console.log("Convert Strava activity to GPX");
}
