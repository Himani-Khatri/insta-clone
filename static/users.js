document.addEventListener('DOMContentLoaded', function() {
    const videos = document.querySelectorAll('.post video');
    videos.forEach(video => {
        video.addEventListener('click', function(e) {
            e.stopPropagation();
        });

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting && !video.paused) {
                    video.pause();
                }
            });
        }, { threshold: 0.5 });

        observer.observe(video);
    });

    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const postId = this.getAttribute('data-post-id');
            const heartIcon = this.querySelector('.heart-icon');
            const likeCount = this.querySelector('.like-count');

            try {
                const response = await fetch(`/like_post/${postId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    if (response.status === 401) {
                        window.location.href = '/login';
                        return;
                    }
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();
                
                likeCount.textContent = data.like_count;

                if (data.is_liked) {
                    heartIcon.classList.remove('far');
                    heartIcon.classList.add('fas');
                    this.classList.add('liked');
                    heartIcon.classList.add('pop');
                } else {
                    heartIcon.classList.remove('fas');
                    heartIcon.classList.add('far');
                    this.classList.remove('liked');
                }

                setTimeout(() => {
                    heartIcon.classList.remove('pop');
                }, 300);

            } catch (error) {
                console.error('Error:', error);
            }
        });
    });

    const followForm = document.getElementById('follow-form');
    if (followForm) {
        followForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                const response = await fetch(followForm.action, {
                    method: 'POST',
                    credentials: 'include'
                });
                if (response.ok) {
                    location.reload();
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }

    // Comment Section Logic
    document.querySelectorAll('.comment-button').forEach(button => {
        button.addEventListener('click', function(e) {
            const postId = this.getAttribute('data-post-id');
            const commentSection = document.getElementById(`comment-section-${postId}`);
            commentSection.style.display = commentSection.style.display === 'none' ? 'block' : 'none';

            if (commentSection.style.display === 'block') {
                fetchComments(postId);
            }
        });
    });

    document.querySelectorAll('.comment-submit').forEach(button => {
        button.addEventListener('click', function(e) {
            const postId = this.getAttribute('data-post-id');
            const commentText = document.querySelector(`.comment-text[data-post-id="${postId}"]`).value;
            if (commentText.trim() !== '') {
                addComment(postId, commentText);
            }
        });
    });

    async function fetchComments(postId) {
        try {
            const response = await fetch(`/get_profile_comments/${postId}`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            const commentsList = document.getElementById(`comments-list-${postId}`);
            commentsList.innerHTML = '';

            data.comments.forEach(comment => {
                const commentElement = document.createElement('div');
                commentElement.className = 'comment';
                commentElement.innerHTML = `
                    <div class="comment-header">
                        <img src="/static/uploads/${comment.profile_picture}" alt="${comment.username}" class="comment-profile-pic">
                        <span class="comment-username">${comment.username}</span>
                        <span class="comment-timestamp">${comment.timestamp}</span>
                        ${comment.can_delete ? `<button class="delete-comment" data-comment-id="${comment.comment_id}"><i class="fas fa-trash"></i></button>` : ''}
                    </div>
                    <div class="comment-content">${comment.content}</div>
                    <div class="comment-replies">
                        ${comment.replies.map(reply => `
                            <div class="reply">
                                <div class="reply-header">
                                    <img src="/static/uploads/${reply.profile_picture}" alt="${reply.username}" class="reply-profile-pic">
                                    <span class="reply-username">${reply.username}</span>
                                    <span class="reply-timestamp">${reply.timestamp}</span>
                                    ${reply.can_delete ? `<button class="delete-reply" data-reply-id="${reply.reply_id}"><i class="fas fa-trash"></i></button>` : ''}
                                </div>
                                <div class="reply-content">${reply.content}</div>
                            </div>
                        `).join('')}
                    </div>
                    <div class="reply-input">
                        <input type="text" class="reply-text" placeholder="Add a reply..." data-comment-id="${comment.comment_id}">
                        <button class="reply-submit" data-comment-id="${comment.comment_id}">Reply</button>
                    </div>
                `;
                commentsList.appendChild(commentElement);
            });

            document.querySelectorAll('.delete-comment').forEach(button => {
                button.addEventListener('click', function(e) {
                    const commentId = this.getAttribute('data-comment-id');
                    deleteComment(commentId, postId);
                });
            });

            document.querySelectorAll('.delete-reply').forEach(button => {
                button.addEventListener('click', function(e) {
                    const replyId = this.getAttribute('data-reply-id');
                    deleteReply(replyId, postId);
                });
            });

            document.querySelectorAll('.reply-submit').forEach(button => {
                button.addEventListener('click', function(e) {
                    const commentId = this.getAttribute('data-comment-id');
                    const replyText = document.querySelector(`.reply-text[data-comment-id="${commentId}"]`).value;
                    if (replyText.trim() !== '') {
                        addReply(commentId, replyText, postId);
                    }
                });
            });

        } catch (error) {
            console.error('Error:', error);
        }
    }

    async function addComment(postId, content) {
        try {
            const response = await fetch(`/comment/${postId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            if (data.success) {
                fetchComments(postId);
                document.querySelector(`.comment-text[data-post-id="${postId}"]`).value = '';
                document.querySelector(`#comment-count-${postId}`).textContent = data.comment_count;
                showToast('Comment added successfully!');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    async function addReply(commentId, content, postId) {
        try {
            const response = await fetch(`/reply/${commentId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            if (data.success) {
                fetchComments(postId);
                document.querySelector(`.reply-text[data-comment-id="${commentId}"]`).value = '';
                showToast('Reply added successfully!');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    async function deleteComment(commentId, postId) {
        try {
            const response = await fetch(`/delete_comment/${commentId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            if (data.success) {
                fetchComments(postId);
                showToast('Comment deleted successfully!');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    async function deleteReply(replyId, postId) {
        try {
            const response = await fetch(`/delete_reply/${replyId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            if (data.success) {
                fetchComments(postId);
                showToast('Reply deleted successfully!');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    // Toast Notification Function
    function showToast(message) {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
});
document.addEventListener('DOMContentLoaded', function() {
const followersModal = document.getElementById('followers-modal');
const followingModal = document.getElementById('following-modal');
const followersList = document.getElementById('followers-list');
const followingList = document.getElementById('following-list');
const closeButtons = document.querySelectorAll('.close');

// Open followers modal
document.querySelector('.stat[data-type="followers"]').addEventListener('click', function() {
fetchFollowers();
followersModal.style.display = 'block';
});

// Open following modal
document.querySelector('.stat[data-type="following"]').addEventListener('click', function() {
fetchFollowing();
followingModal.style.display = 'block';
});

// Close modals
closeButtons.forEach(button => {
button.addEventListener('click', function() {
    followersModal.style.display = 'none';
    followingModal.style.display = 'none';
});
});

// Close modals when clicking outside
window.addEventListener('click', function(event) {
if (event.target === followersModal) {
    followersModal.style.display = 'none';
}
if (event.target === followingModal) {
    followingModal.style.display = 'none';
}
});

// Fetch followers
async function fetchFollowers() {
try {
    const response = await fetch(`/get_followers/${user['username']}`);
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    const data = await response.json();
    followersList.innerHTML = data.followers.map(follower => `
        <div class="follower-item">
            <img src="/static/uploads/${follower.profile_picture}" alt="${follower.username}" class="follower-pic">
            <span class="follower-username">${follower.username}</span>
        </div>
    `).join('');
} catch (error) {
    console.error('Error:', error);
}
}

// Fetch following
async function fetchFollowing() {
try {
    const response = await fetch(`/get_following/${user['username']}`);
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    const data = await response.json();
    followingList.innerHTML = data.following.map(following => `
        <div class="following-item">
            <img src="/static/uploads/${following.profile_picture}" alt="${following.username}" class="following-pic">
            <span class="following-username">${following.username}</span>
        </div>
    `).join('');
} catch (error) {
    console.error('Error:', error);
}
}
});