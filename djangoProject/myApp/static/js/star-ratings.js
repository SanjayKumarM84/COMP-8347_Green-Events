document.addEventListener("DOMContentLoaded", function() {
    const stars = document.querySelectorAll('.star-rating');
    const radioButtons = document.querySelectorAll('.star-rating-input');

    function updateColors() {
        stars.forEach((star, index) => {
            if (radioButtons[index].checked) {
                star.style.color = '#ffff00'; // Yellow color for selected stars
            } else {
                star.style.color = '#ccc'; // Default color
            }
        });
    }

    stars.forEach((star, index) => {
        star.addEventListener('mouseover', function() {
            // Set all previous stars including this to white
            for (let i = 0; i <= index; i++) {
                stars[i].style.color = '#fff'; // White color for hover
            }
        });

        star.addEventListener('mouseout', updateColors);

        // Update colors upon selection
        radioButtons[index].addEventListener('change', updateColors);
    });

    // Initial color update on page load
    updateColors();
});