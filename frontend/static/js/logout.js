document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('confirmation-modal');
    const cancelBtn = document.getElementById('cancel-btn');

    // Show the modal
    modal.style.display = 'flex';

    // Handle cancel button click
    cancelBtn.addEventListener('click', () => {
        // Redirect to the home page
        window.location.href = "/home"; // Adjust the URL as needed
    });
});