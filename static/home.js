        // Comment Button - Toggle Comments Section
        document.querySelectorAll('.comment-button').forEach(button => {
            button.addEventListener('click', function() {
                const postId = this.getAttribute('data-post-id');
                const commentSection = document.getElementById(`comment-section-${postId}`);
                commentSection.classList.toggle('visible'); // Toggle the visibility of the comment section
            });
        });
            document.addEventListener("DOMContentLoaded", function() {
                // Like Button Functionality
                document.querySelectorAll('.like-button').forEach(button => {
                    button.addEventListener('click', async function(e) {
                        e.preventDefault();
                        const postId = this.getAttribute('data-post-id');
                        const heartIcon = this.querySelector('.heart-icon');
                        const likeCount = this.querySelector('.like-count');
        
                        try {
                            const response = await fetch(`/like_post/${postId}`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' }
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
        
                // Comment Button - Toggle Comments Section
                document.querySelectorAll('.comment-button').forEach(button => {
                    button.addEventListener('click', function() {
                        const postId = this.getAttribute('data-post-id');
                        const commentList = document.getElementById(`comments-list-${postId}`);
                        commentList.classList.toggle('hidden');
                    });
                });
        
                // Reply Toggle Button
                document.querySelectorAll('.reply-toggle-button').forEach(button => {
                    button.addEventListener('click', function() {
                        const replyForm = this.nextElementSibling;
                        replyForm.classList.toggle('hidden');
                    });
                });
        
                // Comment Submission
                document.querySelectorAll('.comment-form').forEach(form => {
                    form.addEventListener('submit', async function(e) {
                        e.preventDefault();
                        const postId = this.getAttribute('data-post-id');
                        const input = this.querySelector('input');
                        const content = input.value.trim();
                        
                        if (!content) return;
        
                        try {
                            const response = await fetch(`/comment/${postId}`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ content })
                            });
        
                            const data = await response.json();
        
                            if (!response.ok) {
                                showPopup(data.error || 'Error posting comment', 'error');
                                return;
                            }
        
                            // Update comment count
                            const commentCount = document.querySelector(`#comment-count-${postId}`);
                            commentCount.textContent = data.comment_count;
        
                            // Add new comment to the list
                            const commentsList = document.querySelector(`#comments-list-${postId}`);
                            const newComment = document.createElement('li');
                            newComment.className = 'comment';
                            newComment.setAttribute('data-comment-id', data.comment_id);
                            
                            newComment.innerHTML = `
                                <div class="comment-content">
                                    <img src="/static/uploads/${data.profile_picture || 'd1.jpg'}" alt="Profile Picture" class="comment-profile-pic">
                                    <div class="comment-details">
                                        <span class="comment-username">${data.username}</span>
                                        <span class="comment-text">${data.content}</span>
                                        <span class="comment-timestamp">${data.timestamp}</span>
                                        
                                        <button class="reply-toggle-button">
                                            <i class="fas fa-reply"></i> Reply
                                        </button>
                                        
                                        <form class="reply-form hidden" data-comment-id="${data.comment_id}">
                                            <input type="text" placeholder="Write a reply..." required>
                                            <button type="submit">Reply</button>
                                        </form>
                                        
                                        <div class="replies-container">
                                            <ul class="replies-list"></ul>
                                        </div>
                                    </div>
                                    <button class="delete-comment" data-comment-id="${data.comment_id}">
                                        <i class="fas fa-trash-alt"></i>
                                    </button>
                                </div>
                            `;
        
                            commentsList.insertBefore(newComment, commentsList.firstChild);
                            input.value = '';
        
                            // Add event listeners to new elements
                            const replyToggle = newComment.querySelector('.reply-toggle-button');
                            const replyForm = newComment.querySelector('.reply-form');
                            const deleteBtn = newComment.querySelector('.delete-comment');
        
                            replyToggle.addEventListener('click', function() {
                                replyForm.classList.toggle('hidden');
                            });
        
                            attachReplyFormListener(replyForm);
                            attachDeleteCommentListener(deleteBtn);
        
                            // Show success popup
                            showPopup('Comment posted successfully!', 'success');
        
                        } catch (error) {
                            console.error('Error:', error);
                            showPopup('Error posting comment', 'error');
                        }
                    });
                });
        
                // Reply Submission
                function attachReplyFormListener(form) {
                    form.addEventListener('submit', async function(e) {
                        e.preventDefault();
                        const commentId = this.getAttribute('data-comment-id');
                        const input = this.querySelector('input');
                        const content = input.value.trim();
                        
                        if (!content) return;
        
                        try {
                            const response = await fetch(`/reply/${commentId}`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ content })
                            });
        
                            const data = await response.json();
        
                            if (!response.ok) {
                                showPopup(data.error || 'Error posting reply', 'error');
                                return;
                            }
        
                            // Add new reply to the list
                            const repliesList = this.closest('.comment-details').querySelector('.replies-list');
                            const newReply = document.createElement('li');
                            newReply.className = 'reply';
                            newReply.setAttribute('data-reply-id', data.reply_id);
                            
                            newReply.innerHTML = `
                                <div class="reply-content">
                                    <img src="/static/uploads/${data.profile_picture || 'd1.jpg'}" alt="Profile Picture" class="reply-profile-pic">
                                    <div class="reply-details">
                                        <span class="reply-username">${data.username}</span>
                                        <span class="reply-text">${data.content}</span>
                                        <span class="reply-timestamp">${data.timestamp}</span>
                                    </div>
                                    <button class="delete-reply" data-reply-id="${data.reply_id}">
                                        <i class="fas fa-trash-alt"></i>
                                    </button>
                                </div>
                            `;
        
                            repliesList.insertBefore(newReply, repliesList.firstChild);
                            input.value = '';
                            this.classList.add('hidden');
        
                            // Add event listener to new delete button
                            const deleteBtn = newReply.querySelector('.delete-reply');
                            attachDeleteReplyListener(deleteBtn);
        
                            // Show success popup
                            showPopup('Reply posted successfully!', 'success');
        
                        } catch (error) {
                            console.error('Error:', error);
                            showPopup('Error posting reply', 'error');
                        }
                    });
                }
        
                // Attach reply form listeners to existing forms
                document.querySelectorAll('.reply-form').forEach(form => {
                    attachReplyFormListener(form);
                });
        
                // Delete Comment
                function attachDeleteCommentListener(button) {
            button.addEventListener('click', async function(e) {
                e.preventDefault();
                const commentId = this.getAttribute('data-comment-id');
                const commentElement = this.closest('.comment');
                const postId = commentElement.closest('.post').getAttribute('data-post-id');
                const commentCountElement = document.querySelector(`#comment-count-${postId}`);
        
                try {
                    const response = await fetch(`/delete_comment/${commentId}`, {
                        method: 'DELETE',
                        headers: { 'Content-Type': 'application/json' }
                    });
        
                    if (!response.ok) {
                        throw new Error('Failed to delete comment');
                    }
        
                    commentElement.remove();
                    if (commentCountElement) {
                        commentCountElement.textContent = Math.max(0, parseInt(commentCountElement.textContent) - 1);
                    }
        
                    setTimeout(() => {
                        showPopup('Comment deleted successfully!', 'success');
                    }, 100);
        
                } catch (error) {
                    console.error('Error:', error);
                    showPopup('Error deleting comment', 'error');
                }
            });
        }
        
        
                // Attach delete listeners to existing comment delete buttons
                document.querySelectorAll('.delete-comment').forEach(button => {
                    attachDeleteCommentListener(button);
                });
        
                // Delete Reply
                function attachDeleteReplyListener(button) {
                    button.addEventListener('click', async function(e) {
                        e.preventDefault();
                        const replyId = this.getAttribute('data-reply-id');
                        const replyElement = this.closest('.reply');
        
                        try {
                            const response = await fetch(`/delete_reply/${replyId}`, {
                                method: 'DELETE',
                                headers: { 'Content-Type': 'application/json' }
                            });
        
                            if (!response.ok) {
                                throw new Error('Failed to delete reply');
                            }
        
                            replyElement.remove();
                            showPopup('Reply deleted successfully!', 'success');
                        } catch (error) {
                            console.error('Error:', error);
                            showPopup('Error deleting reply', 'error');
                        }
                    });
                }
        
                // Attach delete listeners to existing reply delete buttons
                document.querySelectorAll('.delete-reply').forEach(button => {
                    attachDeleteReplyListener(button);
                });
        
                // Enhanced popup function
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