function previewMedia(input, type) {
    const previewDiv = document.getElementById(`${type}-preview`);
    previewDiv.innerHTML = '';

    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            if (type === 'photo') {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.className = 'preview-image';
                previewDiv.appendChild(img);
            } else {
                const video = document.createElement('video');
                video.src = e.target.result;
                video.className = 'preview-video';
                video.controls = true;
                previewDiv.appendChild(video);
            }

            const removeBtn = document.createElement('button');
            removeBtn.className = 'remove-media';
            removeBtn.innerHTML = '<i class="fas fa-times"></i>';
            removeBtn.onclick = function() {
                input.value = '';
                previewDiv.innerHTML = '';
            };
            previewDiv.appendChild(removeBtn);
        };

        reader.readAsDataURL(input.files[0]);
    }
}

// Show success popup on successful post
function showSuccessPopup(event) {
    event.preventDefault();  // Prevent form submission to show popup first
    document.getElementById('success-popup').style.display = 'block';
    setTimeout(function() {
        document.getElementById('success-popup').style.display = 'none';
        event.target.submit();  // Submit form after showing popup
    }, 1500);  // Delay form submission to show popup
}

// Close the popup
function closePopup() {
    document.getElementById('success-popup').style.display = 'none';
}