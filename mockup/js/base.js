function helloworld() {
  var test = $("#search").val();
  $.getJSON('http://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&sensor=true?alt=json-in-script&callback=myFunction', function(data){
    alert(data);
  })
  return false;
}

$(document).ready(function() {
  $(document.search_box).bind('submit', helloworld);
});
