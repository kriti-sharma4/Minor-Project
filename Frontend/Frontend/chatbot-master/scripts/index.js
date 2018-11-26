/**
 * Constants
 */
const slider_finish_timeout = 9000; 

function showList(){
    $('#intro-list').fadeIn('slow');
}



function removeCarousel(interval_id){
    clearInterval(interval_id);
    $('.carousel').fadeOut('slow', () => {
        showList();
    })
}


document.addEventListener('DOMContentLoaded', function() {
    let elem = document.querySelector('.carousel');
    let instances = M.Carousel.init(elem);
    let instance = M.Carousel.getInstance(elem);
    let interval_id = setInterval(() => {
        instance.next();
    },3000);
    setTimeout(() => {
        removeCarousel(interval_id)
    },slider_finish_timeout);
});