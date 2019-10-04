$(document).ready(function(){
    // Initiate superfish on nav menu
    $('.nav-menu').superfish({
        animation: {
            opacity: 'show'
        },
        speed: 400
    });

    // Mobile Navigation
    if ($('#nav-menu-container').length) {
        var $mobile_nav = $('#nav-menu-container').clone().prop({
            id: 'mobile-nav'
        });
        $mobile_nav.find('> ul').attr({
            'class': '',
            'id': ''
        });
        $('body').append($mobile_nav);
        $('body').prepend('<button type="button" id="mobile-nav-toggle"><i class="fa fa-bars" aria-hidden="true"></i></button>');
        $('body').append('<div id="mobile-body-overly"></div>');
        $('#mobile-nav').find('.menu-has-children').prepend('<i class="lnr lnr-chevron-down"></i>');

        $(document).on('click', '.menu-has-children i', function (e) {
            $(this).next().toggleClass('menu-item-active');
            $(this).nextAll('ul').eq(0).slideToggle();
            $(this).toggleClass("lnr-chevron-up lnr-chevron-down");
        });

        $(document).on('click', '#mobile-nav-toggle', function (e) {
            $('body').toggleClass('mobile-nav-active');
            $('#mobile-nav-toggle i').toggleClass('lnr-cross lnr-menu');
            $('#mobile-body-overly').toggle();
        });

        $(document).click(function (e) {
            var container = $("#mobile-nav, #mobile-nav-toggle");
            if (!container.is(e.target) && container.has(e.target).length === 0) {
                if ($('body').hasClass('mobile-nav-active')) {
                    $('body').removeClass('mobile-nav-active');
                    $('#mobile-nav-toggle i').toggleClass('lnr-cross lnr-menu');
                    $('#mobile-body-overly').fadeOut();
                }
            }
        });
    } else if ($("#mobile-nav, #mobile-nav-toggle").length) {
        $("#mobile-nav, #mobile-nav-toggle").hide();
    }

    // Header scroll class
    $(window).scroll(function () {
        if ($(this).scrollTop() > 50) {
            $('#header').addClass('header-scrolled');
        } else {
            $('#header').removeClass('header-scrolled');
        }
    });

    // provider services show more
    $('.provider-details ul .toggle-services').on('click', function(e){
        e.preventDefault();

        let list = $(this).parent();
        if(list.hasClass('hide')){
            list.find('.more').removeClass('d-none');
            list.removeClass('hide').addClass('show');
            $(this).text('أقل');
        }
        else{
            list.find('.more').addClass('d-none');
            list.removeClass('show').addClass('hide');
            $(this).text('لمزيد');
        }
    });

    $('.select2').select2();
});

$(window).on('load', function () {
    // WOW JS
    new WOW().init();
    // Preloader
    $('.preloader').fadeOut(500);
});

// end theme scripts