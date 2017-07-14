$(function () {

    var availableTags = $('#search-box').data()['suggestions'];

    availableTags = availableTags.substring(2, availableTags.length - 2).split("', '");

    $("#tags").autocomplete({
        source:  function(request, response) {
            var results = $.ui.autocomplete.filter(availableTags, request.term);
            response(results.slice(0, 10));
        }
    });
});

$(document).ready(function () {
    var playlist = $('#search-box').data()['playlist'];
    playlist = playlist.substring(3, playlist.length - 2).split("', u'");

    $('#tags').on('autocompleteselect', function (e, ui) {
        $("#add-btn").click(function () {
            var new_title = '<li>' + ui.item.value + '</li>';
            if (!playlist.includes(ui.item.value)) {
                $('#songs').find('ul').append(new_title);
                playlist.push(ui.item.value);
            }
        });

    });

    $("#submit-playlist-btn").click(function () {
        console.log("Will submit the playlist");
        post_to_url("/result-playlist", {playlist: playlist});

    });

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

});



