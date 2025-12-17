async function toggleLike(btn, postId) {
    try {
        const response = await fetch(`/like_post/${postId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update like button state
            btn.classList.toggle('liked', data.is_liked);
            
            // Update like count
            const likeCount = btn.nextElementSibling;
            likeCount.textContent = `${data.like_count} likes`;
        } else {
            console.error('Error:', data.error);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}