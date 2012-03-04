
var websocket;

function do_submit(ev) {
  var address = $('#search').val();
  var geocoder = new google.maps.Geocoder();

  geocoder.geocode({ 'address': address }, function(results, status) {
    var latlon = results[0].geometry.location;
    $('#output').html('query: ' + latlon + '<br>');
    // TODO: we might want to make a regular query before asking for real-time updates.
    websocket.send(latlon);
  });
  return false;
}

$(document).ready(function() {
  $(document.search_box).bind('submit', do_submit);

  if ('WebSocket' in window) {
    websocket = new WebSocket('ws://' + document.domain + ':8080/query');
  } else {
    alert('WebSocket not supported');
  }

  websocket.onmessage = function (msg) {
    // TODO: process the incoming data and display it nicely.
    $('#output').append(msg.data + '<br>')
  };
});
