/**
 * Created by laurynas on 7/19/17.
 */
function post_to_url(path, params, method) {
    method = method || "post";

    var form = document.createElement("form");


    form.setAttribute("method", method);
    form.setAttribute("action", path);
    form.setAttribute("id", "playlist-form");
    console.log($.type(params['playlist_id']));
    for (var key in params) {
        var hiddenField = document.createElement("input");
        hiddenField.setAttribute("type", "hidden");
        hiddenField.setAttribute("name", key);
        hiddenField.setAttribute("value", params[key]);
        hiddenField.required = true;


        form.appendChild(hiddenField);
    }
    console.log(form);
    // console.log("Will validate")
    // $('#playlist-form').validate({
    //     rules:{
    //         playlist_id: "required"
    //     }
    // });
    console.log("ss");
    document.body.appendChild(form);
    form.submit();
}

$(document).ready(function () {

    var selected_playlist;
    var previous_selection;
    var api = $("#songs").data("api");

    $(".list-group a").click(function () {
        if (previous_selection) {
            $(previous_selection).removeClass("active");
        }
        selected_playlist = $(this).data("playlist-id");
        $(this).addClass("active");
        console.log("You selected " + selected_playlist);
        previous_selection = this;
    });


    $("#submit-playlist-selection-btn").click(function () {
        if (typeof selected_playlist == "undefined") {
            $(".error-container .error-message").text("Please select playlist");
            $(".error-message").stop().css("color", "#FC0404")
                .animate({color: "#eee"}, 1500);
            console.log("Will submit the playlist_id" + selected_playlist);

        } else {
            console.log("api"+api);
            post_to_url("/", {playlist_id: selected_playlist, api: api});
        }

    });
});