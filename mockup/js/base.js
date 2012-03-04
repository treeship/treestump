var geocoder;
var latlonresult;

function getFieldInput() {
  geocoder = new google.maps.Geocoder();
  var data = $("#search").val();
  codeAddress(data);
  return false;
}

function codeAddress(address) {
  geocoder.geocode({ 'address': address}, function(results, status) {
    latlonresult = results[0].geometry.location;
    alert(latlonresult);
  });
}

$(document).ready(function() {
  $(document.search_box).bind('submit', getFieldInput);
});
