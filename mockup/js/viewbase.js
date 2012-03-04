// Temporary Data
var textlocation = "Cambridge, MA";
var permanentheadline = "AngelHackathon Wows the Kendall Square Clientele";
var backgroundcontent = "This is just a shitload of text In publishing and graphic design, lorem ipsum[1] is placeholder text (filler text) commonly used to demonstrate the graphics elements of a document or visual presentation, such as font, typography, and layout. The lorem ipsum text is typically a section of a Latin text by Cicero with words altered, added and removed that make it nonsensical in meaning and not proper Latin.[1]This is just a shitload of text In publishing and graphic design, lorem ipsum[1] is placeholder text (filler text) commonly used to demonstrate the graphics elements of a document or visual presentation, such as font, typography, and layout. The lorem ipsum text is typically a section of a Latin text by Cicero with words altered, added and removed that make it nonsensical in meaning and not proper Latin.[1]This is just a shitload of text In publishing and graphic design, lorem ipsum[1] is placeholder text (filler text) commonly used to demonstrate the graphics elements of a document or visual presentation, such as font, typography, and layout. The lorem ipsum text is typically a section of a Latin text by Cicero with words altered, added and removed that make it nonsensical in meaning and not proper Latin.[1]This is just a shitload of text In publishing and graphic design, lorem ipsum[1] is placeholder text (filler text) commonly used to demonstrate the graph"

function insertFieldAddress() {
 $('#headline').append("<h4>"+textlocation+"</h4>");
}

function insertPermanentHeadline() {
 $('#headline').append("<h2>"+permanentheadline+"</h2>");
}

function createNewDiv(imgurl, partext) {
  var id = removeDiv();
  var imgurlhtml='';
  var partexthtml='';
  //<div class="text_view" id="0">
  //  <img src="../css/00.jpg">
  //  <h1>This is just a text, you know l</h1>
  //</div>
  var newhtml = '<div class="text_view" id="'+id+'">';
  if (imgurl.length > 0) {
    var imgurlhtml = '<img src="'+imgurl+'">';
  }
  if (partext.length > 0) {
    var partexthtml = '<h1>'+partext+'</h1>';
  }
  newhtml =  newhtml+imgurlhtml+partexthtml+'</div>';
  $('#overlayB').append($(newhtml));
}

function removeDiv() {
  var maxNum = 5;
  var allelements = $('.text_view');
  var allids = $.map(allelements, function(lel, index) {return lel.id});
  if (allids.length > (maxNum-1)) {
    var id = allids.pop()
  }
  $('#'+id).fadeOut('slow');
  return id;
}

function backgroundtext() {
 $('#background-text').append(backgroundcontent);
 $('#background-text').append(backgroundcontent);
 $('#background-text').append(backgroundcontent);
 $('#background-text').append(backgroundcontent);
 $('#background-text').append(backgroundcontent);
 $('#background-text').append(backgroundcontent);
 $('#background-text').append(backgroundcontent);
}

$(document).ready(function() {
  window.setTimeout('backgroundtext()', 100);
  window.setTimeout('insertFieldAddress()', 500);
  window.setTimeout('insertPermanentHeadline()', 1000);
  window.setTimeout("../css/00.jpg", "THIS IS COMPLETELY NEW")', 1500);
});
