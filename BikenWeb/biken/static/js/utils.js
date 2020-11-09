async function exportGPX(itineraryID = undefined, itineraryName = undefined) {
  if (itineraryID != undefined && itineraryName != undefined) {
    url = "getGPX?itinerary=" + itineraryID + "&name=" + itineraryName;
  } else {
    url =
      "getGPX?itinerary=" +
      sessionStorage.getItem("itineraryID") +
      "&name=" +
      sessionStorage.getItem("itineraryID");
  }

  let response = await fetch(url);
  await response.json().then((gpxData) => {
    if (gpxData.success == true) {
      var fileUrl = window.location.origin + "/" + gpxData.filename;
      window.open(fileUrl);
    } else {
      console.log("Fail to create GPX file");
    }
  });
}

async function showError(message, timeout = 1000, colorCode = "warning") {
  box = document.getElementById("warning-box");

  var color;
  if (colorCode == "warning") {
    color = "#f0ad4e";
  } else if (colorCode == "success") {
    color = "#5cb85c";
  } else if (colorCode == "danger") {
    color = "#d9534f";
  }

  box.style.background = color;
  box.innerHTML = message;
  box.hidden = false;
  setTimeout(function () {
    box.hidden = true;
  }, timeout);
}
