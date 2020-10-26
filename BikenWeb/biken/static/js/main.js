


$(document).ready(function() {

  $('.submit_on_enter').keydown(function(event) {
    // enter has keyCode = 13, change it if you want to use another button
    if (event.keyCode == 13) {
      this.form.submit();
      return false;
    }
  });

});


$('input[name=checkbox-mode]').change(function(){
    if($(this).is(':checked')) {
      // document.getElementById("switch-type-label").innerHTML = "Route";
      document.getElementById("finish").hidden=true;
      document.getElementById("finish").required=false;
      document.getElementById("distance").hidden=false;
      document.getElementById("distance").required=true;

    } else {
        // Checkbox is not checked..
        // document.getElementById("switch-type-label").innerHTML = "Itinerary";
        document.getElementById("finish").value ="";
        document.getElementById("finish").hidden=false;
        document.getElementById("finish").required=true;
        document.getElementById("distance").hidden=true;
        document.getElementById("distance").required=false;

    }
});





function getRequestType()
{
  if (document.getElementById("customSwitches").checked)
  {
    return "route";
  }
  else {
    return "itinerary";
  }

}


function saveItinerary(gpx=false) {

  var alertContainer = document.getElementById('alertContainer');

  if (routeList.length==0) {
    alertContainer.innerHTML ='<div class="alert">You need to create an itinerary before</div>';
    setTimeout(function(){
        alertContainer.innerHTML = '';
    }, 2000);
  }
  else {
    routeList.forEach((route, i) => {

      if (route._path!=undefined) {
        console.log("call Save")

        $.post( "/save", {
            polyline: displayedPolyline,
            distance: currentDistance,
            duration: currentDuration
        },
        function(data, status){
            if (data["text"]=="Already Stored") {
              alertContainer.innerHTML ='<div class="alert warning">This itinerary has already been saved</div>';
              setTimeout(function(){
                  alertContainer.innerHTML = '';
              }, 2000);
              if(gpx==false) 
              {
                showSaveExportPopup(data["itineraryCode"])
              }
              else
              {
                exportGPX(data["itineraryCode"])
              }            }
            else if (data["text"]=="OK - User not logged in" || data["text"]=="Already Stored - User not logged in"){
              // Only show the share popup if not connected
              if(gpx==false) 
              {
                showSaveExportPopup(data["itineraryCode"])
              }
              else
              {
                exportGPX(data["itineraryCode"])
              }
            }
            else {
              alertContainer.innerHTML ='<div class="alert success">The itinerary has been saved</div>';

              setTimeout(function(){
                  alertContainer.innerHTML = '';
              }, 2000);
              if(gpx==false) 
              {
                showSaveExportPopup(data["itineraryCode"])
              }
              else
              {
                exportGPX(data["itineraryCode"])
              }            }
          });
      }

    });


  }

}

async function showSaveExportPopup(itineraryCode){
  // Get the popup
  var popup = document.getElementById("popupSave");
  popup.style.display = "block";

  // Write the current url
  var myInput = document.getElementById("urlCopyInput");
  myInput.value = window.location.origin + "/home?itinerary="+itineraryCode;
}


function sendRequest() {

  var start = document.getElementById('start').value;
  var finish = document.getElementById('finish').value;
  var distance = document.getElementById('distance').value;
  var url = "";


  if (getRequestType()=="route")
  {
    finish = "None";
  }


  getLocations(start,finish).then(data =>  {
    // Remove old routes
    routeList.forEach((route, i) => {
      route.remove();
    });

    var loader = document.getElementById('loader');

    // check if itinerary or route

    if (getRequestType()=="itinerary")
    {
      if (window.location.pathname=="/" || window.location.pathname=="/home") {
        loader.hidden=false;
        url = "routing/itinerary?coords="+data+"&render=false";
        getItinerary(url).then(dataItinerary => {



          // Query elevation of this path to the server
          getElevation(dataItinerary.polyline)

          // display the cursor at the start and finish position
          displayStartFinish(dataItinerary.polyline);

          // display the new route
          displayPolyline(dataItinerary.polyline);

          // Show elevation, distance and time
          showSummary(dataItinerary);
          loader.hidden=true;

        });
      }
      else {
        url = "routing/itinerary?coords="+data+"&render=true";
        window.location.href=url;
      }



    }
    else {
      if (window.location.pathname=="/" || window.location.pathname=="/home") {
        loader.hidden=false;
        url = "routing/route?start="+data+"&distance="+distance+"&render=false";
        // console.log('Not implemented',url);
        getItinerary(url).then(dataItinerary => {

          // Query elevation of this path to the server
          getElevation(dataItinerary.polyline)

          // // Display start point
          var coordinates = L.Polyline.fromEncoded(dataItinerary.polyline).getLatLngs();
          displayMarker(coordinates[0]);

          // display the new route
          displayPolyline(dataItinerary.polyline);

          // Show elevation, distance and time
          showSummary(dataItinerary);

          // // Fit the itinerary in the screen
          // fitItinerary(dataItinerary.polyline);
          loader.hidden=true;

        });
      }
      else {
        url = "routing/route?start="+data+"&distance="+distance+"&render=true";
        window.location.href=url;
      }

    }

  });
}

function closeInfo() {
  document.getElementById("info-bottom").hidden = true;
}


function showSummary(data) {
  // console.log(data);
  document.getElementById("info-bottom").hidden = false;
  var distance = data.distance;
  var estimatedTime = data.duration;

  displayedPolyline=data.polyline;
  currentDistance=distance;
  currentDuration=estimatedTime;

  // Display the distance and calculation time
  document.getElementById("itinerary-distance").innerHTML = '<i class="fas fa-arrows-alt-h px-2"></i>'+distance+" km";
  document.getElementById("itinerary-time").innerHTML ='<i class="fas fa-stopwatch px-2"></i>'+timeConvert(estimatedTime);

}


function timeConvert(n) {
var num = n;
var hours = (num / 60);
var rhours = Math.floor(hours);
var minutes = (hours - rhours) * 60;
var rminutes = Math.round(minutes);
var str = "";

if (rhours>1) {
  str += rhours + " hours and ";
}
else if (rhours==1) {
  str += "1 hour and ";
}
if (rminutes>1) {
  str += rminutes + " minutes";
}
else {
  str += rminutes + "minute";
}
return str;
}

async function getItinerary(url){
  let response = await fetch(url);

  let data = await response.json();

  return data
}




async function getLocations(location1,location2){
  if (location2 != "None") {
    var endpoint = "https://nominatim.openstreetmap.org/search/";
    var query1 = endpoint+location1+"?format=json&limit=1";
    var query2 = endpoint+location2+"?format=json&limit=1";
    let response1 = await fetch(query1);
    let response2 = await fetch(query2);

    let data1 = await response1.json();
    let data2 = await response2.json();

    var coords = ""+data1[0].lat+","+data1[0].lon+";"+data2[0].lat+","+data2[0].lon;
    return coords;
  }
  else {
    // Route mode
    var endpoint = "https://nominatim.openstreetmap.org/search/";
    var query1 = endpoint+location1+"?format=json&limit=1";
    let response1 = await fetch(query1);
    let data1 = await response1.json();
    var coords = ""+data1[0].lat+","+data1[0].lon;
    return coords;

  }

}


// Popup save

// Get the popup
var popup = document.getElementById("popupSave");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  popup.style.display = "none";
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
  copyButton.innerHTML="Copied!"

}


function exportGPX(itineraryCode) {

  var alertContainer = document.getElementById('alertContainer');

  url = "getGPX?itinerary="+itineraryCode;


  getGPXfile(url).then(gpxData => {
    if(gpxData.success==true) {
      console.log("Success to create GPX file")
      var fileUrl = window.location.href + gpxData.filename
      window.open(fileUrl)
    }
    else {
      console.log("Fail to create GPX file")

      alertContainer.innerHTML ='<div class="alert warning">Fail to download the itinerary</div>';
      setTimeout(function(){
          alertContainer.innerHTML = '';
      }, 2000);
    }
  });

}


async function getGPXfile(url) {
  let response = await fetch(url);
  console.log(response)
  let data = await response.json();

  return data
}

