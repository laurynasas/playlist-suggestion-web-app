/**
 * Created by laurynas on 7/19/17.
 */
function post_to_url(path, params, method) {
    method = method || "post";

    var form = document.createElement("form");


    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for (var key in params) {
        var hiddenField = document.createElement("input");
        hiddenField.setAttribute("type", "hidden");
        hiddenField.setAttribute("name", key);
        hiddenField.setAttribute("value", params[key]);

        form.appendChild(hiddenField);
    }

    document.body.appendChild(form);
    form.submit();
}

$(document).ready(function () {

    var selected_playlist;
    var previous_selection;

    $(".list-group a").click(function () {
        if (previous_selection){
            $(previous_selection).removeClass("active");
        }
        selected_playlist =  $(this).data("playlist-id");
        $(this).addClass("active");
        console.log("You selected " + selected_playlist);
        previous_selection = this;
    });


    $("#submit-playlist-selection-btn").click(function () {
        console.log("Will submit the playlist_id" + selected_playlist);

        post_to_url("/", {playlist_id: selected_playlist});

    });
});