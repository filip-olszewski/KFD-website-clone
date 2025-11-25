/* Sticky Menu Script */
$(document).ready(function() {
    // Sprawdzamy czy element .header-top w ogóle istnieje
    if ($('.header-top').length) {
        // Zapamiętujemy, jak daleko od góry strony jest pasek w momencie załadowania
        var menuOffset = $('.header-top').offset().top;
        
        // Funkcja uruchamiana przy każdym ruchu rolką myszki
        $(window).scroll(function() {
            var scrollPos = $(window).scrollTop(); // Ile przewinęliśmy
            
            // Jeśli przewinęliśmy więcej niż pozycja paska -> Przyklej go
            if (scrollPos >= menuOffset) {
                $('.header-top').addClass('is-sticky');
                // Opcjonalnie: dodaj margines do body, żeby strona nie "podskoczyła"
                // $('body').css('padding-top', $('.header-top').outerHeight()); 
            } else {
                // Jeśli wróciliśmy na górę -> Odklej go
                $('.header-top').removeClass('is-sticky');
                // $('body').css('padding-top', 0);
            }
        });
    }
});