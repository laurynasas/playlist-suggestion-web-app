$(document).ready(function () {
    $('.to-show').animate({"opacity": "1"}, 500);

    $(".result-song").click(function (e) {
        e.preventDefault();
        // var selected_title = $(this).find('a').text();
        var $preview_container = $(this).find(".preview-container");
        // if (selected_title != "" && $preview_container.is(':empty') ) {
        //     console.log("Will try to get preview of this song: " + selected_title);
        //     $.ajax({
        //         url: '/get-preview-url',
        //         dataType: "json",
        //         data: {title: selected_title},
        //         success: function (data) {
        //             console.log(data);
        //             if (data['preview_url'] != null) {
        //                 var html = "<audio controls='' name='media'><source src=" + data['preview_url'] + " type='audio/mpeg'></audio>"
        //             } else {
        //                 var html = "<h6>No preview for this song</h6>"
        //             }
        //             $preview_container.append(html);
        //
        //         }
        //     });
        // }
        $preview_container.slideToggle("slow");
    });

});