window.HELP_IMPROVE_VIDEOJS = false;


$(document).ready(function() {
    // Check for click events on the navbar burger icon

    var options = {
        slidesToScroll: 1,
        slidesToShow: 1,
        loop: true,
        infinite: true,
        autoplay: false,
        autoplaySpeed: 5000,
    }

    // Initialize all div with carousel class
    var carousels = bulmaCarousel.attach('.carousel', options);

    // For each carousel, add event listener to pause/play videos when sliding
    carousels.forEach(carousel => {
        carousel.on('before:show', () => {
            const videos = carousel.element.getElementsByTagName('video');
            Array.from(videos).forEach(video => {
                video.pause();
            });
        });
        
        carousel.on('shown', () => {
            const currentSlide = carousel.element.querySelector('.slider-item.is-active');
            if (currentSlide) {
                const video = currentSlide.querySelector('video');
                if (video) {
                    video.play();
                }
            }
        });
    });
	
    bulmaSlider.attach();

})
