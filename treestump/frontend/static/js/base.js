
function start_fetching(address) {
  var websocket;

  if ('WebSocket' in window) {
    websocket = new WebSocket('ws://' + document.domain + ':8080/query');
  } else {
    alert('WebSocket not supported');
    return;
  }

  websocket.onmessage = function (msg) {
    // TODO: process the incoming data and display it nicely.
    $('#output').append(msg.data + '<br>')
  };

  websocket.onerror = function (evt) {
    $('#output').html('DISCONNECTED');
    // TODO: should reconnect and re-query
  }

  var geocoder = new google.maps.Geocoder();
  geocoder.geocode({ 'address': address }, function(results, status) {
    var latlon = results[0].geometry.location;
    $('#output').html('query: ' + latlon + '<br>');
    var query = { 'lat': latlon.lat(), 'lng': latlon.lng() };
    // for some reason JSON sent as binary doesn't get through to gevent
    websocket.send(JSON.stringify(query));
  });
}

