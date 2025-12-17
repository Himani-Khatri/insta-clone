document.addEventListener("DOMContentLoaded", function() {
    // Load comments when the comment button is clicked
    document.querySelectorAll('.comment-button').forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.dataset.postId;
            const commentSection = document.querySelector(`#comment-section-${postId}`);
            
            if (commentSection.style.display === 'none') {
                commentSection.style.display = 'block';
                loadComments(postId);
            } else {
                commentSection.style.display = 'none';
            }
        });
    });

    // Function to load comments
    function loadComments(postId) {
        fetch(`/get_profile_comments/${postId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const commentsList = document.querySelector(`#comment-section-${postId} .comments-list`);
                    commentsList.innerHTML = '';
                    
                    data.comments.forEach(comment => {
                        const commentElement = createCommentElement(comment, postId);
                        commentsList.appendChild(commentElement);
                    });
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // Function to create comment element
    function createCommentElement(comment, postId) {
        const div = document.createElement('div');
        div.className = 'comment';
        div.dataset.commentId = comment.comment_id;

        div.innerHTML = `
            <div class="comment-header">
                <img src="/static/uploads/${comment.profile_picture}" alt="Profile Picture" class="comment-profile-pic">
                <span class="comment-username">${comment.username}</span>
                <span class="comment-timestamp">${comment.timestamp}</span>
                ${comment.can_delete ? `
                    <button class="delete-comment-btn" onclick="deleteComment(${comment.comment_id}, ${postId})">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                ` : ''}
            </div>
            <div class="comment-content">${comment.content}</div>
            <div class="comment-actions">
                <button class="reply-toggle-btn" onclick="toggleReplyForm(${comment.comment_id})">
                    <i class="fas fa-reply"></i> Reply
                </button>
            </div>
            <div class="reply-form hidden" id="reply-form-${comment.comment_id}">
                <div class="add-reply">
                    <textarea class="reply-input" placeholder="Write a reply..."></textarea>
                    <button class="post-reply-btn" onclick="postReply(${comment.comment_id}, ${postId})">Reply</button>
                </div>
            </div>
            <div class="replies-container">
                ${comment.replies.map(reply => `
                    <div class="reply" data-reply-id="${reply.reply_id}">
                        <div class="reply-header">
                            <img src="/static/uploads/${reply.profile_picture}" alt="Profile Picture" class="reply-profile-pic">
                            <span class="reply-username">${reply.username}</span>
                            <span class="reply-timestamp">${reply.timestamp}</span>
                            ${reply.can_delete ? `
                                <button class="delete-reply-btn" onclick="deleteReply(${reply.reply_id}, ${postId})">
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            ` : ''}
                        </div>
                        <div class="reply-content">${reply.content}</div>
                    </div>
                `).join('')}
            </div>
        `;

        return div;
    }

    // Add these functions to the global scope
    window.toggleReplyForm = function(commentId) {
        const replyForm = document.getElementById(`reply-form-${commentId}`);
        replyForm.classList.toggle('hidden');
    };

    window.postReply = function(commentId, postId) {
        const replyForm = document.getElementById(`reply-form-${commentId}`);
        const replyInput = replyForm.querySelector('.reply-input');
        const content = replyInput.value.trim();

        if (content) {
            fetch(`/reply/${commentId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content: content })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    replyInput.value = '';
                    loadComments(postId);
                    showPopup('Reply posted successfully!', 'success');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showPopup('Error posting reply', 'error');
            });
        }
    };

    window.deleteComment = function(commentId, postId) {
fetch(`/delete_comment/${commentId}`, {
method: 'DELETE'
})
.then(response => response.json())
.then(data => {
if (data.success) {
    loadComments(postId);
    showPopup('Comment deleted successfully!', 'success');
    
    // Update comment count
    const commentCount = document.querySelector(`#comment-count-${postId}`);
    if (commentCount) {
        const currentCount = parseInt(commentCount.textContent);
        commentCount.textContent = Math.max(0, currentCount - 1);
    }
}
})
.catch(error => {
console.error('Error:', error);
showPopup('Error deleting comment', 'error');
});
};

window.deleteReply = function(replyId, postId) {
fetch(`/delete_reply/${replyId}`, {
method: 'DELETE'
})
.then(response => response.json())
.then(data => {
if (data.success) {
    loadComments(postId);
    showPopup('Reply deleted successfully!', 'success');
}
})
.catch(error => {
console.error('Error:', error);
showPopup('Error deleting reply', 'error');
});
};
    // Post new comment
    document.querySelectorAll('.post-comment-btn').forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.dataset.postId;
            const commentInput = this.previousElementSibling;
            const content = commentInput.value.trim();

            if (content) {
                fetch(`/comment/${postId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ content: content })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        commentInput.value = '';
                        loadComments(postId);
                        
                        // Update comment count
                        const commentCount = document.querySelector(`#comment-count-${postId}`);
                        if (commentCount) {
                            commentCount.textContent = data.comment_count;
                        }
                        
                        showPopup('Comment posted successfully!', 'success');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showPopup('Error posting comment', 'error');
                });
            }
        });
    });

    function showPopup(message, type = 'success') {
        const popup = document.createElement('div');
        popup.className = `popup ${type}`;
        popup.textContent = message;
        document.body.appendChild(popup);

        setTimeout(() => {
            popup.classList.add('fade-out');
            setTimeout(() => popup.remove(), 500);
        }, 2500);
    }
});

document.addEventListener("DOMContentLoaded", function () {
const editModal = document.getElementById('editModal');
const deleteModal = document.getElementById('deleteModal');
let currentPostId = null;

function closeModal(modal) {
modal.style.display = 'none';
}

function hideDropdownMenus() {
document.querySelectorAll(".dropdown-menu").forEach(menu => {
    menu.style.display = "none";
});
}

window.onclick = function(event) {
if (event.target === editModal) {
    closeModal(editModal);
}
if (event.target === deleteModal) {
    closeModal(deleteModal);
}
}

document.querySelectorAll('.close, .cancel-btn').forEach(button => {
button.onclick = function() {
    closeModal(editModal);
    closeModal(deleteModal);
}
});

document.querySelectorAll('.edit-post-btn').forEach(button => {
button.addEventListener('click', function () {
    currentPostId = this.dataset.postId;
    const currentContent = document.querySelector(`#post-content-${currentPostId}`).textContent;
    document.getElementById('editContent').value = currentContent;
    editModal.style.display = 'block';
    hideDropdownMenus();
});
});

document.querySelector('#editModal .save-btn').addEventListener('click', function() {
const newContent = document.getElementById('editContent').value.trim();

if (newContent && currentPostId) {
    fetch(`/edit_post/${currentPostId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: newContent })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.querySelector(`#post-content-${currentPostId}`).textContent = newContent;
            closeModal(editModal);
        } else {
            alert(data.error || 'Something went wrong.');
        }
    })
    .catch(error => console.error('Error:', error));
}
});

document.querySelectorAll('.delete-post-btn').forEach(button => {
button.addEventListener('click', function () {
    currentPostId = this.dataset.postId;
    deleteModal.style.display = 'block';
    hideDropdownMenus();
});
});

document.querySelector('#deleteModal .delete-btn').addEventListener('click', function() {
if (currentPostId) {
    fetch(`/delete_post/${currentPostId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const postElement = document.querySelector(`#post-${currentPostId}`);
            postElement.remove();
            closeModal(deleteModal);
        } else {
            alert(data.error || 'Something went wrong.');
        }
    })
    .catch(error => console.error('Error:', error));
}
});

document.querySelectorAll('.like-button').forEach(button => {
button.addEventListener('click', function() {
    const postId = this.dataset.postId;
    const likeIcon = this.querySelector('i');
    const likeCount = this.querySelector('.like-count');

    fetch(`/like_post/${postId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            likeCount.textContent = data.like_count;
            if (data.is_liked) {
                likeIcon.classList.add('liked');
            } else {
                likeIcon.classList.remove('liked');
            }
        }
    })
    .catch(error => console.error('Error:', error));
});
});

document.querySelectorAll(".menu-icon i").forEach(icon => {
icon.addEventListener("click", function (e) {
    const dropdown = this.nextElementSibling;
    const allDropdowns = document.querySelectorAll(".dropdown-menu");

    allDropdowns.forEach(menu => {
        if (menu !== dropdown) {
            menu.style.display = "none";
        }
    });

    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
    e.stopPropagation();
});
});

document.addEventListener("click", function () {
hideDropdownMenus();
});

document.querySelectorAll(".dropdown-menu").forEach(menu => {
menu.addEventListener("click", function (e) {
    e.stopPropagation();
});
});
});
