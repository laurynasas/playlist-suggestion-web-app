/**
 * Created by laurynas on 7/19/17.
 */
$(document).ready(function () {
    var replace_content = "<h1>Import playlist: </h1><a href='/select-playlist'><img src='../images/youtube-icon.png' style='width:100px;height:100px;'></a>";



    function remove_title() {
        var val = $(this).parent().attr('value');
        console.log("Will try to remove: " + val);

        var index = playlist.indexOf(val);
        if (index != -1) {
            playlist.splice(index, 1);
        }
        console.log(playlist);
        $(this).parent().fadeOut(500);

        console.log(playlist.length, replace_content);
        if (playlist.length == 0 || playlist[0] == "") {
            $('#populate-container h1').fadeOut(300, function () {
                $('#populate-container h1').replaceWith(replace_content).fadeIn(300);
            });
        }

    }

    var playlist = $('#search-box').data()['playlist'];
    playlist = playlist.substring(3, playlist.length - 2).split("', u'");

    console.log(playlist.length);
    if (playlist ==null || playlist.length == 0 || playlist[0] ==""){
        $('#populate-container h1').replaceWith(replace_content);
    }

    var availableTags = $('#search-box').data()['suggestions'];
    availableTags = availableTags.substring(2, availableTags.length - 2).split("', '");

    $("#tags").autocomplete({
        source: function (request, response) {
            var results = $.ui.autocomplete.filter(availableTags, request.term);
            response(results.slice(0, 10));
        }
    });

    $('#tags').on('autocompleteselect', function (e, ui) {
        $("#add-btn").click(function () {


            var new_title = '<li type="button" class="list-group-item list-group-item-action" value="' + ui.item.value + '">' + ui.item.value + '<button style="float: right; background-color: transparent;" type="button" class="btn btn-xs remove-btn text-danger glyphicon glyphicon-remove"></button></li>';
            if (!playlist.includes(ui.item.value)) {
                console.log("Will add", new_title);
                $(new_title).hide().appendTo("#songs").fadeIn(500);
                $(".remove-btn").on('click', remove_title);
                $("#add-btn").off("click");
                playlist.push(ui.item.value);

                var populate_container = $('#populate-container h1');
                console.log(populate_container.text());
                if (playlist.length !=0 && populate_container.text() == "Import playlist: ") {
                    populate_container.fadeOut(300, function () {
                        $('#populate-container').replaceWith("<div class='row' id='populate-container'><h1>Suggest based on: </h1></div>").fadeIn(300);
                    });
                }

                console.log(playlist);
            }
        });


    });
    $(".remove-btn").click(remove_title);

    $("#submit-playlist-btn").click(function () {
        console.log("Will submit the playlist");
        var limit = $("#limit-input").val();
        var bands = $("#limit-bands").val();
        console.log(limit);
        console.log(bands);

        post_to_url("/result-playlist", {playlist: playlist, limit: limit, bands: bands});

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



