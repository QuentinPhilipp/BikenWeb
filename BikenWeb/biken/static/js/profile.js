
function editName(itineraryID) {
  // Replace the name div with an input field
  nameField = document.getElementById('itinerary-name');
  console.log(nameField);


  var url = "api/1.0/itineraries?itinerary="+itineraryID;

  $( "#itinerary-name" ).replaceWith( '<form method="POST" action='+url+'><input class="submit_on_enter" type="text" name="name" placeholder="New name"></form>' );

  //set the name
}





function deleteItinerary(itineraryID) {
  $.ajax({
  url: '/api/1.0/itineraries?itinerary='+itineraryID,
  method: 'DELETE',
  success: function(response) {
     location.reload();
   }
  })
}
