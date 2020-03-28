var mymap = L.map('mapid').setView([48.8589507,2.2770202], 10);


L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    zoomControl: false,
    accessToken: 'pk.eyJ1IjoiYmlrZW5kZXYiLCJhIjoiY2sxeHp3amcwMGdvYTNobDh6Ym55ZW1ibSJ9.lGWM8-RyVB2NoQRSgIL9nQ'
}).addTo(mymap);




function sendData() {
  var start = document.getElementById('start').value
  var finish = document.getElementById('finish').value

  console.log("Send data");
  console.log("Start : ",start," | Finish : ",finish);

  var url = "http://127.0.0.1:5000/api/1.0/itinerary?start="+start+"&finish="+finish


  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", url, false ); // false for synchronous request
  xmlHttp.send();
  console.log("API : ",xmlHttp.responseText);
  var response = JSON.parse(xmlHttp.responseText);
  var startPos = response.data.startPos;
  var finishPos = response.data.finishPos;
  console.log("Start : ",startPos);
  console.log("Finish : ",finishPos);
  displayStartFinish([startPos,finishPos]);
}


function displayStartFinish(pointList) {
  pointList.forEach((
    point, i) => {
      var marker = L.marker([point.lat, point.lon]).addTo(mymap);
  });

  var corner1 = L.latLng(pointList[0].lat, pointList[0].lon);
  var corner2 = L.latLng(pointList[1].lat, pointList[1].lon);
  var bounds = L.latLngBounds(corner1, corner2);
  mymap.flyToBounds(bounds);
}
