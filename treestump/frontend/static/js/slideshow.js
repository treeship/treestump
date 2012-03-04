$(document).ready(function() {

        $('.image-view').css("left", 0);
        $('.image-view2').css("left", -$('.image-view2').outerWidth());

        var date = new Date(2012, 3, 4);
        var data = ["image", 42.363539, -71, date, "Tom", "@tom", "what's up", "http://distilleryimage7.instagram.com/3e917a22654b11e180c9123138016265_7.jpg"];

        // change view depending on data
        set_view(data);

    });

function set_view(data) {

    var type = data[0];

    if (type == "image") {

        if (parseInt($('.image-view').css("left")) < 0) {
            $('.image-view').css("left", $('.image-view').outerWidth());

        $('.image-view2').animate({
                left: -$('.image-view').outerWidth()
                    }, 1000, function() {
                setTimeout(function(){set_view(data)},3000);
            });
        $('.image-view').animate({
                left: 0
                    }, 1000, function() {
            });

        } else if (parseInt($('.image-view2').css("left")) < 0) {
            $('.image-view2').css("left", $('.image-view2').outerWidth());

            $('.image-view').animate({
                left: -$('.image-view').outerWidth()
                    }, 1000, function() {
            });
            $('.image-view2').animate({
                left: 0
                    }, 1000, function() {
                    setTimeout(function(){set_view(data)},3000);
            });

        }
    }
}
