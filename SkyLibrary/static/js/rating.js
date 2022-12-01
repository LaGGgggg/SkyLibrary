const rating = document.querySelectorAll('.rating');

if (rating !== null) {
    getRating(rating);
}

function getRating(rating) {
    for (const rate of rating.values()) {

        const ratingStars = rate.querySelector('.rating__stars');
        const ratingValue = parseFloat(rate.querySelector('.rating__value').innerHTML.replace(',', '.'));

        ratingStars.style.width = `${ratingValue / 0.05}%`;
    }
}
