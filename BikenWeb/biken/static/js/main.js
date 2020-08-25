
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



async function getElevation(itinerary)
{
  // $.ajax({
  //   type: 'GET',
  //   url: '/elevation',
  //   dataType: 'application/json',
  //   processData: false,
  //   data: $.param({'waypoints' : itinerary }),
  //   success: function(resp){
  //       console.log(resp);
  //   }
  // });


  $.post( "/elevation", {
      waypoints: JSON.stringify(itinerary)
  },
  function(data, status){
      console.log(data);
    });
}


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


function saveItinerary() {

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
        console.log(route._latlngs);

        var waypointsList = ["12;23","45;56","78;91"];
        $.post( "/save", {
            waypoints: JSON.stringify(route._latlngs),
            distance: currentDistance,
            duration: currentDuration
        },
        function(data, status){
            if (data=="Already Stored") {
              alertContainer.innerHTML ='<div class="alert warning">This itinerary has already been saved</div>';
              setTimeout(function(){
                  alertContainer.innerHTML = '';
              }, 2000);
            }
            else {
              alertContainer.innerHTML ='<div class="alert success">The itinerary has been saved</div>';

              setTimeout(function(){
                  alertContainer.innerHTML = '';
              }, 2000);
            }
          });
      }

    });


  }




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
    // check if itinerary or route

    var loader = document.getElementById('loader');

    if (getRequestType()=="itinerary")
    {
      if (window.location.pathname=="/" || window.location.pathname=="/home") {
        loader.hidden=false;
        url = "itinerary?coords="+data+"&render=false";
        getItinerary(url).then(dataItinerary => {

          getElevation(dataItinerary.waypoints)
          // Remove old routes
          routeList.forEach((route, i) => {
                route.remove();
          });
          // display the cursor at the start and finish position
          var start = {"lat":dataItinerary.waypoints[0][0],"lon":dataItinerary.waypoints[0][1]}
          var finish = {"lat":dataItinerary.waypoints[dataItinerary.waypoints.length-1][0],"lon":dataItinerary.waypoints[dataItinerary.waypoints.length-1][1]}

          displayStartFinish([start,finish]);

          // display the new route
          displayRoute(dataItinerary.waypoints);
          showSummary(dataItinerary);
          loader.hidden=true;

        });
      }
      else {
        url = "itinerary?coords="+data+"&render=true";
        window.location.href=url;
      }

      //
      // url = "itinerary?coords="+data;
      // window.location.href = url;


    }
    else {
      if (window.location.pathname=="/" || window.location.pathname=="/home") {
        loader.hidden=false;
        url = "route?start="+data+"&distance="+distance+"&render=false";
        // console.log('Not implemented',url);
        getItinerary(url).then(dataItinerary => {

          // Remove old routes
          routeList.forEach((route, i) => {
                route.remove();
          });

          // Display start point
          var start = {"lat":dataItinerary.waypoints[0][0],"lon":dataItinerary.waypoints[0][1]}
          displayMarker(start)
          // display the new route
          displayRoute(dataItinerary.waypoints);

          showSummary(dataItinerary);

          // Fit the itinerary in the screen
          fitItinerary(dataItinerary.waypoints);
          loader.hidden=true;

        });
      }
      else {
        url = "route?start="+data+"&distance="+distance+"&render=true";
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


  currentDistance=distance;
  currentDuration=estimatedTime;

  // Display the distance and calculation time
  document.getElementById("itinerary-distance").innerHTML = "Total distance: "+distance+" km";
  document.getElementById("itinerary-time").innerHTML = "Estimated time: "+timeConvert(estimatedTime);

}


function timeConvert(n) {
var num = n;
var hours = (num / 60);
var rhours = Math.floor(hours);
var minutes = (hours - rhours) * 60;
var rminutes = Math.round(minutes);
var str = "" + rhours;

if (rhours>1) {
  str += " hours and ";
}
else {
  str += " hour and ";
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
