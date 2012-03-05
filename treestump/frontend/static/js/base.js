
function insertFieldAddress(address) {
 $('#headline > h3').html(address);
}

function insertPermanentHeadline(headline) {
 $('#headline > h2').html(headline);
}

var things_to_add = Array();
var currently_adding = false;

function process_things_to_add() {
  if (currently_adding)
    return;
  if (things_to_add.length == 0)
    return;
  currently_adding = true;
  addNewItem();
}

function addDiv() {
  if (things_to_add.length == 0)
    return;
  var thing = things_to_add.shift();
  var imgurl = thing["img"];
  var partext = thing["title"];
  var imgurlhtml='';
  var partexthtml='';
  //<div class="text_view" id="0">
  //  <img src="../css/00.jpg">
  //  <h1>This is just a text, you know l</h1>
  //</div>
  var newhtml = '<div class="text_view">';
  if (imgurl.length > 0) {
    var imgurlhtml = '<img src="'+imgurl+'">';
  }
  if (partext.length > 0) {
    var partexthtml = '<h4>'+partext+'</h4>';
  }
  newhtml =  newhtml+imgurlhtml+partexthtml+'</div>';
  var added = $(newhtml);
  added.hide();
  $('#overlayB').append(added);
  $(added).fadeIn('slow', function() {
    if (things_to_add.length > 0) {
      window.setTimeout(addNewItem, 1000);
    } else {
      currently_adding = false;
    }
  });
}

function addNewItem() {
  var maxNum = 5;
  var allelements = $('#overlayB').children();
  if (allelements.size() > (maxNum-1)) {
    var removed = $(allelements[0]);
    removed.fadeOut('slow', function() {
      removed.remove();
      addDiv();
    });
  } else {
    addDiv();
  }
}

function new_element(imgurl, title) {
  things_to_add.push({'img': imgurl, 'title': title });
  process_things_to_add();
}

function backgroundtext(text) {
  $('#background-text').html('');
  var bam = "";
  for (var i = 0; i < 1000; ++i) {
    bam += text + " ";
  }
  $('#background-text').append(bam);
}

function get_hashtags(location) {
  function sort_fun(a, b) {
    return b["count"] - a["count"];
  }
  $.get('/tweets', location, function(data) {
    data = JSON.parse(data);
    var tags = Array();
    for (var key in data) {
      if (data.hasOwnProperty(key)) {
        var count = data[key];
        tags.push({"hashtag":key, "count":count});
      }
    }
    tags.sort(sort_fun);
    backgroundtext(tags[0]["hashtag"]);
  });
}


function start_fetching(address) {
//  insertFieldAddress(address);

//  if (address.substring(0, 6) != '42.364')
  insertPermanentHeadline(address);

  if (address == '1 Broadway, Cambridge, MA')
    address = '42.364, -71.084'

  var websocket;

  if ('WebSocket' in window) {
    websocket = new WebSocket('ws://' + document.domain + ':8080/query');
  } else {
    alert('WebSocket not supported');
    return;
  }

  websocket.onmessage = function (msg) {
    var data = JSON.parse(msg.data);
    for (var i = 0; i < data.length; ++i) {
      var d = data[i];
      var imgurl = '';
      if (d.imgurls.length > 0)
        imgurl = d.imgurls[0];
      new_element(imgurl, d.title);
    }
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

    get_hashtags(query);
  });
}

