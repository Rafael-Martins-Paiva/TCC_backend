
document.addEventListener('DOMContentLoaded', () => {
    let currentIndex = 0;
    const gifContainer = document.getElementById('gifContainer');
    let currentImage = document.getElementById('activeImage');

    // Preload images
    images.forEach(src => {
        const img = new Image();
        img.src = src;
    });

    // Initialize first image and tab
    const imageIndex = parseInt(currentImage.dataset.imageIndex) || 0;
    currentImage.src = images[imageIndex];
    currentIndex = imageIndex;

    const tabs = document.querySelectorAll('.tabs span');
    tabs.forEach(tab => {
        tab.classList.remove('active');
        if (parseInt(tab.dataset.tabIndex) === imageIndex) {
            tab.classList.add('active');
        }

        tab.addEventListener('click', () => {
            const index = parseInt(tab.dataset.tabIndex);
            if (index === currentIndex) return;

            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const newImage = document.createElement('img');
            newImage.src = images[index];
            newImage.alt = 'Preview GIF';
            newImage.dataset.imageIndex = index;
            newImage.id = 'activeImage';

            const enteringFrom = index > currentIndex ? 'enter-right' : 'enter-left';
            const exitingTo = index > currentIndex ? 'exit-left' : 'exit-right';

            newImage.classList.add(enteringFrom);
            gifContainer.appendChild(newImage);

            requestAnimationFrame(() => {
                newImage.classList.add('enter-active');
                currentImage.classList.add(exitingTo);
            });

            setTimeout(() => {
                gifContainer.removeChild(currentImage);
                newImage.classList.remove(enteringFrom, 'enter-active');
                currentImage = newImage;
                currentIndex = index;
            }, 500);
        });
    });
});
