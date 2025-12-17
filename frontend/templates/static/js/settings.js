 // Toggle Followers and Following visibility
 function toggleFollowers() {
    const followersSection = document.getElementById('followers-section');
    followersSection.style.display = followersSection.style.display === 'none' ? 'block' : 'none';
}

function toggleFollowing() {
    const followingSection = document.getElementById('following-section');
    followingSection.style.display = followingSection.style.display === 'none' ? 'block' : 'none';
}

// Handle deletion confirmation modal
document.getElementById("delete-account-link").addEventListener("click", function (e) {
    e.preventDefault();
    document.getElementById("confirmation-modal").style.display = "block";
    document.getElementById("overlay").style.display = "block";
});

document.getElementById("cancel-delete").addEventListener("click", function () {
    document.getElementById("confirmation-modal").style.display = "none";
    document.getElementById("overlay").style.display = "none";
});

document.getElementById("confirm-delete").addEventListener("click", async function () {
    const username = document.getElementById("username-input").value; 
    const currentUsername = "{{ session.get('username') }}";  // Get the logged-in username from the session

    if (!username) {
        alert("Username is required to delete the account.");
        return;
    }

    if (username !== currentUsername) {
        alert("You can only delete your own account.");
        return;
    }

    try {
        const response = await fetch('/delete_account', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username }), 
        });

        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            window.location.href = '/'; 
        } else {
            alert(result.error || 'Failed to delete the account.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An unexpected error occurred.');
    }
});