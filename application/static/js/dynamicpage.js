$(document).ready(function () {
    $('nav a').click(function (e) {
        e.preventDefault();
        var $a = $(this);
        var url = $a.attr('href');
        if ($a.attr('href') == "/") {
            // url += "?" + $.param({insert: 1});
            location.reload();
        }
        console.log(url);
        $('#main-content').load(url);



    });
});
// $(document).ready(function () {
//     $('a').click(function (e) {
//         e.preventDefault();
//         console.log(this);
//         $("#dynamic").load($(this).attr('href'));
//     });
// });
// $(function () {
//
//     var newHash = "",
//         $mainContent = $("#main-content"),
//         $pageWrap = $("#page-wrap"),
//         baseHeight = 0,
//         $el;
//
//     $pageWrap.height($pageWrap.height());
//     baseHeight = $pageWrap.height() - $mainContent.height();
//
//     $("nav").delegate("a", "click", function () {
//         window.location.hash = $(this).attr("href");
//         return false;
//     });
//
//     $(window).bind('hashchange', function () {
//
//         newHash = window.location.hash.substring(1);
//
//         if (newHash) {
//             $mainContent
//                 .find("#guts")
//                 .fadeOut(200, function () {
//                     $mainContent.hide().load(newHash + " #guts", function () {
//                         $mainContent.fadeIn(200, function () {
//                             $pageWrap.animate({
//                                 height: baseHeight + $mainContent.height() + "px"
//                             });
//                         });
//                         $("nav a").removeClass("current");
//                         $("nav a[href=" + newHash + "]").addClass("current");
//                     });
//                 });
//         }
//         ;
//
//     });
//
//     $(window).trigger('hashchange');
//
// });