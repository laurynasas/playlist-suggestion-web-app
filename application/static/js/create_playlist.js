/**
 * Created by laurynas on 7/19/17.
 */
$(document).ready(function () {
    $('.to-show').animate({"opacity": "1"}, 500);
    var replace_content = "<div style='display: block'><h1>Import playlist: </h1><col><a href='/select-playlist' class='btn'><img class='youtube' src='../images/youtube-logo.png'></a></col>" +
        "<col><a href='/spotify-auth' class='btn spotify-btn'><img class='spotify' src='../images/spotify-logo.png'></a></col></div>";


    function remove_title() {
        var val = $(this).parent().attr('value');
        console.log("Will try to remove: ");
        console.log(val);

        var index = playlist.indexOf(val);
        console.log(index);
        if (index != -1) {
            playlist.splice(index, 1);
        }
        console.log(playlist);
        $(this).parent().hide(500);

        console.log(playlist.length, replace_content);
        if (playlist.length == 0 || (playlist.length == 1 && playlist[0] == "")) {
            $('#populate-container h1').fadeOut(500, function () {
                $('#populate-container h1').replaceWith(replace_content);
                $('.suggestion-params').hide(500);
            });
        }

    }

    var playlist = $('#search-box').data()['playlist'];
    if (typeof playlist == "string" && playlist != "") {
        playlist = JSON.parse(playlist);
    } else if (typeof playlist == "string" && playlist == "") {
        playlist = [];
    }
    console.log(playlist);
    if (playlist.length == 0) {
        $('#populate-container h1').replaceWith(replace_content);
    } else {
        $('.suggestion-params').show(500);
        $('#songs').show(500);

    }

    // var availableTags = $('#search-box').data()['suggestions'];


    // availableTags = availableTags.substring(3, availableTags.length - 2).split("', u'");

    $("#tags").autocomplete({
        source: function (request, response) {
            $.ajax({
                url: '/get-suggestions',
                dataType: "json",
                data: {term: request.term},
                success: function (data) {
                    response(JSON.parse(data['suggestions']));
                }
            });

        }
    });

    $('#tags').on('autocompleteselect', function (e, ui) {
        $("#add-btn").click(function () {


            var new_title = '<li type="button" class="list-group-item list-group-item-action" style="margin-bottom:-20px; opacity:0;" value="' + ui.item.value + '">' + ui.item.value + '<button style="float: right; background-color: transparent;" type="button" class="btn btn-xs remove-btn text-danger glyphicon glyphicon-remove"></button></li>';
            if (!playlist.includes(ui.item.value)) {
                console.log("Will add", new_title);
                $(new_title).appendTo("#songs").animate({'margin-bottom': '0', 'opacity': '1'}, 500);
                $(".remove-btn").on('click', remove_title);
                $("#add-btn").off("click");
                playlist.push(ui.item.value);

                var populate_container = $('#populate-container h1');
                console.log(populate_container.text());
                if (playlist.length != 0 && populate_container.text() == "Import playlist: ") {
                    populate_container.fadeOut(300, function () {
                        $('#populate-container').replaceWith("<div class='row logo-container'  id='populate-container'><h1>Suggest based on: </h1></div>").fadeIn();
                        $('.suggestion-params').show(500);
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

        post_to_url("/compute-results", {playlist: JSON.stringify(playlist), limit: limit, bands: bands}, "GET");

    });

    function create_and_post_form(path,params,method) {

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

    function post_to_url(path, params, method) {
        $('body .container').fadeOut();
        $('body').css({transition : 'background 0.5s ease-in-out', background:"#eee"});
        $('body .scene').show(700);
        $('body .loading').show(700);
        $.ajax({
            type: method,
            url: path,
            data: params,
            contentType: 'application/json;charset=UTF-8',
            success: function (data) {

                create_and_post_form("/result-playlist", {result_playlist: JSON.stringify(data)}, "POST")
            }
        });

    }

});



