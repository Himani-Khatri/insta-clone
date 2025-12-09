document.addEventListener("DOMContentLoaded", function () {
    const chatMessages = document.querySelector(".chat-messages");
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Scroll to the bottom when a new message is sent
    const chatForm = document.getElementById("chat-form");
    if (chatForm) {
        chatForm.addEventListener("submit", function () {
            setTimeout(() => {
                if (chatMessages) {
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
            }, 100); // Delay to ensure the message is added
        });
    }

    // Bee emoji button functionality
    const beeEmojiBtn = document.getElementById("bee-emoji-btn");
    const messageTextarea = document.querySelector("textarea[name='message']");
    
    if (beeEmojiBtn && messageTextarea && chatForm) {
        beeEmojiBtn.addEventListener("click", function () {
            messageTextarea.value += "🐝"; // Append instead of replace
            chatForm.submit();
        });
    }

    // Voice recording functionality
    const recordBtn = document.getElementById("record-btn");
    const audioInput = document.getElementById("audio-input");
    const audioPreview = document.getElementById("audio-preview");
    let mediaRecorder, audioChunks = [];

    if (recordBtn && audioInput && audioPreview) {
        recordBtn.addEventListener("click", async () => {
            if (!mediaRecorder || mediaRecorder.state === "inactive") {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);

                    mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                        const audioUrl = URL.createObjectURL(audioBlob);

                        audioPreview.src = audioUrl;
                        audioPreview.style.display = "block";

                        const file = new File([audioBlob], "voice_message.webm", { type: "audio/webm" });
                        const dataTransfer = new DataTransfer();
                        dataTransfer.items.add(file);
                        audioInput.files = dataTransfer.files;

                        audioChunks = [];
                    };

                    mediaRecorder.start();
                    recordBtn.innerHTML = '<i class="fas fa-stop"></i>';
                } catch (error) {
                    console.error("Microphone access denied:", error);
                }
            } else if (mediaRecorder.state === "recording") {
                mediaRecorder.stop();
                recordBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            }
        });
    }

    // Emoji picker functionality
    const emojiBtn = document.getElementById("emoji-btn");
    const emojiDropdown = document.getElementById("emoji-dropdown");

    if (emojiBtn && emojiDropdown && messageTextarea) {
        emojiBtn.addEventListener("click", function (event) {
            event.stopPropagation();
            emojiDropdown.style.display = (emojiDropdown.style.display === "block") ? "none" : "block";
        });

        const emojiOptions = document.querySelectorAll(".emoji-option");
        emojiOptions.forEach((option) => {
            option.addEventListener("click", function () {
                messageTextarea.value += this.dataset.emoji; 
            });
        });

        document.addEventListener("click", function (event) {
            if (!emojiDropdown.contains(event.target) && event.target !== emojiBtn) {
                emojiDropdown.style.display = "none";
            }
        });
    }
});
