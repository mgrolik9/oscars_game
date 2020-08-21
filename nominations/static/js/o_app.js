
$(document).ready(function() {
    $('#view_movies_cat').hide();
    $("#choose_movie").on('click', function () {
       $('#view_movies_cat') .toggle();
    });
});


$(document).ready(function() {
    $('#view_best_cat').hide();
    $("#choose_best").on('click', function () {
       $('#view_best_cat') .toggle();
    });
});


$(document).ready(function() {
    $('#movie_div').hide();
    $("#view_movie").on('click', function () {
       $('#movie_div') .toggle();
    });
});


$(document).ready(function() {
    $('#people_div').hide();
    $("#view_people").on('click', function () {
       $('#people_div') .toggle();
    });
});


$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip()
});

