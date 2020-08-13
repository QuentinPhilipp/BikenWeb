
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
