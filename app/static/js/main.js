function myFunction(x) {
    x.classList.toggle("change");
    var x = document.getElementById("burger-menu");
    if (x.className === "burger-open") {
        x.className = "burger-close";
    } else {
        x.className = "burger-open";
    }
}

$('#dropdown-btn-blog').on('click', function () {
    $('#drop-down-blog').slideToggle('slow');
});

$('#dropdown-btn-profile').on('click', function () {
    $('#drop-down-profile').slideToggle('slow');
});

$('#dropdown-btn-store').on('click', function () {
    $('#drop-down-store').slideToggle('slow');
});

$('#dropdown-btn-tools').on('click', function () {
    $('#drop-down-tools').slideToggle('slow');
});