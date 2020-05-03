


$('input[name=checkbox-mode]').change(function(){
    if($(this).is(':checked')) {
      document.getElementById("switch-type-label").innerHTML = "Route";
      document.getElementById("finish").placeholder = "Choose distance";

    } else {
        // Checkbox is not checked..
        document.getElementById("switch-type-label").innerHTML = "Itinerary";
        document.getElementById("finish").placeholder = "Choose destination";

    }
});



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
