if ($('.loadgeo').length > 0) {

var markers = [];
function selectLoc() {
	var elem = document.getElementById("map-canvas");
	elem.setAttribute("style","display: block;");
	var head = document.getElementById("headtxt");
	head.setAttribute("style","display: block;");
  var mapOptions = {
    zoom: 16,
    center: new google.maps.LatLng(42.39088182665314,-72.52500057220459 )
  };
  var map = new google.maps.Map(document.getElementById('map-canvas'),
      mapOptions);

  google.maps.event.addListener(map, 'click', function(e) {
	setAllMap(null);
	markers = [];
    placeMarker(e.latLng, map);
	
	$( "input[name='Lat']" ).attr( "value", e.latLng.d );
    $( "input[name='Long']" ).attr( "value",  e.latLng.e );
  });
  
}

function placeMarker(position, map) {
  var marker = new google.maps.Marker({
    position: position,
    map: map
  });
  markers.push(marker);
  map.panTo(position);
}

function setAllMap(map) {
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
  }
}

function atLoc() {
    if (navigator.geolocation) {
    // Use method getCurrentPosition to get coordinates
    navigator.geolocation.getCurrentPosition(function (position) {
		console.log("hello");
        $( "input[name='Lat']" ).attr( "value", position.coords.latitude );
        $( "input[name='Long']" ).attr( "value",  position.coords.longitude );

    });
};

}



google.maps.event.addDomListener(window, 'load', initialize);
};
