$(document).ready(function () {
    $('.my-blog-articles').slick({
        dots: true,
        infinite: true,
        slidesToShow: 3,
        slidesToScroll: 3,
        responsive: [
            {
            breakpoint: 992,
            settings: {
            slidesToShow: 2,
            slidesToScroll: 2
            }
        },
            {
            breakpoint: 768,
            settings: {
            slidesToShow: 1,
            slidesToScroll: 1
            }
        }
        ]
    });
});