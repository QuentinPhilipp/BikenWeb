function showSearchBar()
{
  var searchBar = document.getElementById("searchBar");
  var searchToggleButton = document.getElementById("searchShowButton");
  // showAnimation();
  searchBar.style.display="block";
  searchToggleButton.hidden=true;
  console.log("Show");
}
//
// function showAnimation() {
//   var elem = document.getElementById("searchBar");
//   var pos = -300;
//   var id = setInterval(frame, 1);
//   function frame() {
//     if (pos >= 15) {
//       clearInterval(id);
//       elem.style.left = "15px";
//
//     } else {
//       pos= pos+10;
//       elem.style.left = pos + "px";
//     }
//   }
// }
//
function hideSearchBar()
{
  var searchBar = document.getElementById("searchBar");
  var searchToggleButton = document.getElementById("searchShowButton");
  searchBar.style.display="none";
  searchToggleButton.hidden=false;
  console.log("Hide");
}

$('input[name=checkbox-mode]').change(function(){
    if($(this).is(':checked')) {
      document.getElementById("switch-type-label").innerHTML = "Route";
      document.getElementById("finish").hidden=true;
      document.getElementById("distanceSlider").hidden=false;
      document.getElementById("slider-value").hidden=false;

    } else {
        // Checkbox is not checked..
        document.getElementById("switch-type-label").innerHTML = "Itinerary";
        document.getElementById("finish").value ="";
        document.getElementById("finish").hidden=false;
        document.getElementById("distanceSlider").hidden=true;
        document.getElementById("slider-value").hidden=true;


    }
});

var slider = document.getElementById("distanceSlider");
var output = document.getElementById("slider-value");
output.innerHTML = slider.value + "km"; // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
slider.oninput = function() {
  output.innerHTML = this.value + "km";
}


function getRequestType()
{
  console.log(document.getElementById("customSwitches"));
  if (document.getElementById("customSwitches").checked)
  {
    return "route";
  }
  else {
    return "itinerary";
  }


}
