
function editName(itineraryID) {
  // Replace the name div with an input field

  // If click on the edit button to confirm
  if ($("#new-title").value != "") {
    console.log("Validate with the button")
    $("#name-form").submit();
  }


  var strID = "#activityName"+itineraryID;
  var url = "itineraries?itinerary="+itineraryID;
  $( strID ).replaceWith( '<form id="name-form" method="POST" action='+url+'><input id="new-title" class="submit_on_enter" type="text" name="name" placeholder="New name"></form>' );

  $("#new-title").focus();

  //set the name
}



function deleteItinerary(itineraryID) {
  $.ajax({
  url: 'itineraries?itinerary='+itineraryID,
  method: 'DELETE',
  success: function(response) {
     location.reload();
   }
 });
}



function strToWaypoints(itineraryString) {
  // transform a string of coords to a list of waypoints
  var extractRegex = /((.+?),(.+?);)/g;
  var waypointsList = [];
  var result;
  while((result = extractRegex.exec(itineraryString)) !== null) {
      var coord = [result[2],result[3]];
      waypointsList.push(coord);
  }

  return waypointsList

}
