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
