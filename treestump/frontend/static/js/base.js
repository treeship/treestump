
function do_submit() {
  var keyword = $('#search').val();

  ws.onmessage = function (msg) {
    // TODO: process the incoming data and display it nicely.
    $('#output').append(msg.data+'<br>')
  };

  $('#output').html('');

  ws.send(keyword);
  return false;
}

$(document).ready(function() {
  $(document.search_box).bind('submit', do_submit);

  if ('WebSocket' in window) {
    ws = new WebSocket('ws://' + document.domain + ':8080/query');
  } else {
    alert('WebSocket not supported');
  }
});
