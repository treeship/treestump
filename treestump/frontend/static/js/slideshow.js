$(document).ready(function() {

        $('.image-view').css("left", 0);
        $('.text-view').css("left", -$('.image-view').outerWidth());
        $('.text-view').addClass('current');
        $('.image-view').addClass('future');

        var date = new Date(2012, 3, 4);
        var data = [["image", 42.363539, -71, date, "Tom", "@tom", "what's up", "http://distilleryimage7.instagram.com/3e917a22654b11e180c9123138016265_7.jpg"],
["image", 42.363539, -71, date, "Tom", "@tom", "what's up", "http://distilleryimage7.instagram.com/3e917a22654b11e180c9123138016265_7.jpg"],
                    ["text", 42.363539, -71, date, "Tom", "@tom", "what's up", "http://distilleryimage7.instagram.com/3e917a22654b11e180c9123138016265_7.jpg"],
["image", 42.363539, -71, date, "Tom", "@tom", "what's up", "http://distilleryimage7.instagram.com/3e917a22654b11e180c9123138016265_7.jpg"],
                    ["text", 42.363539, -71, date, "Tom", "@tom", "what's up", "http://distilleryimage7.instagram.com/3e917a22654b11e180c9123138016265_7.jpg"]];

        // change view depending on data
        var i =0;
        setTimeout(update,3000);

        function update(){
            set_view(data[i]);
            i += 1;
            if (i < data.length) {
                setTimeout(update, 3000);
            }
        }

    });

function set_view(data) {

    var type = data[0];

    // remove current and set future to current
    $('.current').addClass('previous');
    $('.previous').remove();
    $('.future').addClass('current');
    $('.current').removeClass('future');

    if (type == "image") {
        // add new div and set left to edge of screen
        $("body").append('<div class="image-view panel future">'+
                         '<div class="image">'+
                         '<img src="'+data[7]+'".>'+
                         '</div></div>');
    } else if (type == "text") {
        // add new div and set left to edge of screen
        $("body").append('<div class="text-view panel future">'+
                                '<div class="tweet">'+
                                '<div>'+data[6]+'</div>'+
                         '</div></div>');
    }
    $(".future").css("left",$('.future').outerWidth());

    $('.current').animate({
            left: -$('.image-view').outerWidth()
                }, 1000, function() {
        });
    $('.future').animate({
            left: 0
                }, 1000, function() {
        });
}
