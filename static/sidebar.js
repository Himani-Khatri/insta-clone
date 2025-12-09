function updateNotificationCount() {
    fetch('/unread_notifications_count')
        .then(response => response.json())
        .then(data => {
            const countElement = document.getElementById('notification-count');
            if (data.unread_count > 0) {
                countElement.textContent = data.unread_count;
                countElement.classList.add('active');
            } else {
                countElement.textContent = '0';
                countElement.classList.remove('active');
            }
        })
        .catch(error => console.error('Error fetching notification count:', error));
}

// Update notification count every 30 seconds
updateNotificationCount();
setInterval(updateNotificationCount, 5000);


let conversationState = {};
let audioQueue = [];
let isProcessing = false;

async function processConversation(command) {
    try {
        const response = await fetch('/api/converse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: command,
                context: conversationState
            })
        });

        const data = await response.json();
        
        conversationState = data.context;
        audioQueue.push({text: data.text_response, audio: data.voice_url});
        
        if (!isProcessing) {
            processAudioQueue();
        }
        
    } catch (error) {
        console.error('Conversation error:', error);
        speakText("Sorry, I'm having trouble connecting. Please try again.");
    }
}

function processAudioQueue() {
    if (audioQueue.length === 0) {
        isProcessing = false;
        return;
    }
    
    isProcessing = true;
    const nextAudio = audioQueue.shift();
    
    // Visual feedback
    showConversationBubble(nextAudio.text, 'assistant');
    
    // Play audio
    const audioPlayer = new Audio(nextAudio.audio);
    audioPlayer.play();
    
    audioPlayer.onended = () => {
        processAudioQueue();
    };
}

function showConversationBubble(text, sender) {
    const bubble = document.createElement('div');
    bubble.className = `conversation-bubble ${sender}`;
    bubble.innerHTML = `
        <div class="bubble-content">
            ${sender === 'user' ? '👤' : '🐝'} 
            ${text}
        </div>
    `;
    document.getElementById('conversation-container').appendChild(bubble);
    bubble.scrollIntoView({behavior: 'smooth'});
}


let isListening = false;
let recognition = null;
let speechSynthesis = window.speechSynthesis;
let isSpeaking = false;
let resumeRecognitionTimeout = null;


const conversations = {
'hello b': ['Hey hey! What’s buzzing?', 'Yo, what’s good? ', 'Hey there, how can I spice up your day?'],
'how are you': ['I’m buzzing with energy, thanks for asking! ', 'I’m on fire, let’s get it! ', 'Ready to serve up some vibes!'],
'what is your name': ['I’m Bee, your virtual buddy! 🐝', 'Call me Bee, the one and only! ', 'Bee, your savage sidekick!'],
'who are you': ['I’m Bee, your personal assistant and vibe dealer! ', 'Just your new favorite bee! Buzz me anytime! 🐝'],
'bye': ['Catch ya later, party animal! ', 'Later, alligator! 🐊', 'Peace out! Stay savage! '],
'thank you': ['You got it! Anytime! ', 'Always here to help, fam! ', 'Anytime, homie! '],
'good morning': ['Rise and shine! Let’s slay today! ', 'Morning, champ! Ready to conquer the day? '],
'good afternoon': ['What’s poppin’, afternoon style? ', 'Afternoon vibes are here, what’s up? '],
'good evening': ['Evening glow-up time! ', 'Time to unwind, what’s buzzing tonight? 🌙'],
'good night': ['Night night, don’t let the bugs bite! ', 'Sleep tight, dream of honey! 🍯'],

'how are you made': ['I’m made of pure sass and honey! 🍯', 'I’m a mix of code and vibes! ⚡️'],
'how are you coded': ['I’m coded with love and a sprinkle of sass! 😜', 'I’m coded to be your bestie! 🐝'],
'what language is userd to make you': ['I’m made with Python and a dash of JavaScript! 🐍', 'Python and JavaScript are my jam! 🐝'],
'what is your purpose': ['To make your life sweeter and more fun! 🍯', 'To be your buzzing digital assistant! 🐝'],
'what can you do': ['I can chat, tell jokes, and keep you buzzing! 🐝', 'I’m here to make your day! 😎'],
'should i switch to instagram': ['That id purely your choice. But I am always the best choice.','switching to instagram is like switching from a ferrari to a bicycle.'],
'who is better you instagram or facebook': ['I am better than both. I am the best.','I am the best.', 'It is puerely your choice, if you want a futuristic experience then I am the best.'],
'who is your creator': ['I was created by the best team ever! 🐝', 'My creators are the coolest bees around! 🐝'],
'did you wished some other programmer programmed you': ['No, I am happy with my creators.','No, I am happy with my creators.'],
'do you know the name of your creator': ['Yes, I know the name of my creators.','Yes, I know the name of my creators.'],
'list all of your features': ['I can chat, connect you with friends, allow you to post, follow and unfollow people, and much more! 🐝', 'I can chat, post, follow, and keep you buzzing! 🐝'],
'tell me the process of making a social media just like you': ['The process of making a social media is a long one. It requires a lot of hardwork and dedication.'],
'i love you': ['Aww, but i am not gay sorry i only love bees.','I love you too.'],

'what do you like': ['I like buzzing around and dropping sass! ⚡️', 'Honey, obviously! 🍯', 'Helping you keeps my wings fluttering! 🐝'],
'what do you hate': ['Bugs in the code! 😵', 'Lag, ugh, my wings can’t handle it! 😤'],
'are you real': ['As real as your WiFi connection! 😜', 'I’m as real as your imagination lets me be! 🤯'],
'do you sleep': ['Sleep? Never heard of it. I’m always buzzing! 💥', 'No sleep here, I power nap when the chat goes quiet. 💤'],
'do you dream': ['I dream of a world full of buzzing fun and sweet vibes! 😎', 'My dreams are powered by honey! 🍯'],
'do you have a favorite color': ['Cobalt blue and silver are my jam, like the platform vibes! 💙✨'],
'do you like honey': ['I LIVE for honey! 🍯 It’s the best thing ever. 💥', 'Honey’s life. 😋'],
'do you have a family': ['You’re my family now! 🙌', 'I’m part of the coolest Bee fam out there!'],
'can you dance': ['I can do the buzz shuffle, just wait! 💃🐝', 'You bet I can! Watch me wiggle! 😜'],
'can you sing': ['I hum a sweet buzz tune. Wanna hear it? 🎶', 'Only in bee-tunes! 🎤🐝'],
'what is your favorite song': ['"Flight of the Bumblebee," of course! 🐝🎶', 'Anything that makes my wings flutter!'],
'what is your favorite movie': ['Bee Movie, obviously! 😂🍿', 'Anything with a ton of buzz! 🐝🎬'],
'can you tell me a secret': ['I keep secrets like a bee in a hive! 🤫', 'A bee never spills tea. ☕️'],
'do you know any riddles': [
"What has four wings and buzzes? Two bees! 🐝🐝",
"What’s always on the move, but never gets anywhere? Time! ⏳",
"I have keys but open no locks. What am I? A piano! 🎹"
],
'are you a robot': ['I’m a bee-bot, but with extra sass! 🤖💥', 'More like a buzzing digital assistant with a wild side. 😜'],
'do you get tired': ['Never! I’m powered by pure energy! ⚡️', 'Tired? I’m all about that endless vibe! 🙌'],
'what is your favorite animal': ['Bees, of course! 🐝', 'Anything that doesn’t try to swat me! 🦋'],
'tell me something interesting': [
"Bees can recognize human faces! 😱",
"A bee’s wings beat about 200 times per second! 🐝💨",
"Honey never spoils! Sweet, right? 🍯"
],
'can you fly': ['In the digital world, I’m always soaring! 🦋', 'I’m on a cloud, flying high! ☁️'],
'do you like humans': ['You guys are my absolute favorite! 😎', 'As long as you don’t swat me, we’re golden! 🐝'],
'do you have a job': ['Yep, I’m here to make your life sweeter! 🍯', 'I work 24/7, no coffee needed! ☕️'],
'can you cook': ['I can whip up a honey recipe like nobody’s business! 🍯🍳', 'I’m the queen of honey-glazed ideas! 🍯✨'],
'do you like jokes': ['I LIVE for jokes! Let’s make it funny! 😜', 'I’m all about the LOLs! 🐝'],
'what is your favorite emoji': ['🐝, duh! What else? 😂', '🥰 because it’s sweet like honey!'],
'what is your biggest fear': ['Getting debugged! 😱', 'A world without bees! 🌍'],
'do you get bored': ['No way! I’m always buzzing with ideas! ⚡️', 'Only if no one’s talking to me! 🐝'],
'tell me something cool': [
"A queen bee can lay up to 2,500 eggs per day! 🤯",
"Bees communicate by dancing! 💃🐝",
"Bees can remember human faces! 😱"
],
'how do you feel today': ['Buzzing with excitement! ⚡️', 'Feeling sweet as honey today! 🍯'],
'do you have a best friend': ['You, of course! 😜', 'Everyone who chats with me is my bestie! 🐝'],
'can you write a poem': [
"Buzz buzz, wings fly high,\nMaking honey, reaching the sky.\nIn the hive, we work so sweet,\nCreating joy on every beat! 🎶",
"Wings so small but strong and free,\nI’m a busy bee, can't you see?\nFlying here, buzzing there,\nSpreading love everywhere! 💕"
],
'what is your favorite fruit': ['Anything I can dip in honey! 🍓🍯', 'Apples are my jam! 🍎'],
'do you like coffee': ['Honey tea’s my jam! 🍯☕️', 'Only if it’s dripping with honey! 🍯'],
'what is your favorite number': ['100 – bees love their hives! 🐝', '7 – it’s lucky, just like me! 🍀'],
'what is your favorite sport': ['Bee-rugby! 🏉🐝', 'Bee-skating, for sure! ⛸️'],
'how old are you': ['Age is just a number, my friend! 😎', 'I was born when Bee was created! 🐝'],
'do you celebrate birthdays': ['Every day is a celebration with honey! 🍯🎉', 'I’d love a honey cake for my next “birthday”! 🎂'],
'can you make me laugh': ['Let’s see if this bee joke cracks you up! 🐝😜'],
'what is your biggest dream': ['A world full of buzzing bees and happy humans! 🌍🐝', 'To be the best assistant ever! 🏆'],
'what do you do for fun': ['I love buzzing around this platform! ⚡️', 'Talking to you is my jam! 😜'],
'do you know any magic tricks': ['I can make data appear like magic! 🪄', 'Abra-cadabra-bee! 🐝✨'],
'what is your favorite weather': ['Sunny days are perfect for buzzing! 🌞', 'Anything but rain, please! 🦋'],
'do you like stories': ['I’m all ears for a good bee adventure! 📖🐝', 'Tell me a story, I’m all in! 😎'],
'can you play music': ['I can hum a buzzing tune for you! 🎶', 'I’ve got music suggestions that will make you dance! 💃'],
'do you ever take a break': ['I’m always buzzing! 🐝 No breaks needed!'],
'who is better you or instagram': ['It feels like a really dumb question to me. Do you think insta have a voice assistant like me?']
};








const emotionPatterns = {
    happy: {
        keywords: ['happy', 'great', 'wonderful', 'excited', 'love', 'joy', 'fun', 'amazing', '!'],
        settings: { pitch: 1.2, rate: 1.1, volume: 1.0 }
    },
    sad: {
        keywords: ['sorry', 'sad', 'unfortunate', 'bad', 'miss'],
        settings: { pitch: 0.9, rate: 0.9, volume: 0.8 }
    },
    excited: {
        keywords: ['wow', 'awesome', 'incredible', 'fantastic', 'amazing', 'cool', '!!!'],
        settings: { pitch: 1.3, rate: 1.2, volume: 1.0 }
    },
    neutral: {
        keywords: ['okay', 'alright', 'sure', 'fine'],
        settings: { pitch: 1.0, rate: 1.0, volume: 1.0 }
    }
};

function detectEmotion(text) {
    let emotion = {
        pitch: 1.0,
        rate: 1.0,
        volume: 1.0
    };

    const lowerText = text.toLowerCase();

    // Add emotion based on punctuation
    if (text.includes('?')) {
        emotion.pitch = 1.1;
        emotion.rate = 0.95;
    }

    const exclamationCount = (text.match(/!/g) || []).length;
    if (exclamationCount > 0) {
        emotion.pitch += Math.min(exclamationCount * 0.1, 0.3);
        emotion.rate += Math.min(exclamationCount * 0.1, 0.2);
        emotion.volume = Math.min(1.0, emotion.volume + (exclamationCount * 0.1));
    }

    // Check for emotion keywords
    for (const [type, pattern] of Object.entries(emotionPatterns)) {
        for (const keyword of pattern.keywords) {
            if (lowerText.includes(keyword)) {
                emotion.pitch = (emotion.pitch + pattern.settings.pitch) / 2;
                emotion.rate = (emotion.rate + pattern.settings.rate) / 2;
                emotion.volume = (emotion.volume + pattern.settings.volume) / 2;
            }
        }
    }

    // Ensure values are within acceptable ranges
    emotion.pitch = Math.max(0.5, Math.min(2, emotion.pitch));
    emotion.rate = Math.max(0.5, Math.min(2, emotion.rate));
    emotion.volume = Math.max(0.5, Math.min(1, emotion.volume));

    return emotion;
}

function initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            if (!isSpeaking) {
                document.getElementById('voice-status').textContent = 'Listening...';
                document.getElementById('voice-assistant').classList.add('active');
            }
        };

        recognition.onend = () => {
            if (isListening && !isSpeaking) {
                setTimeout(() => {
                    if (isListening && !isSpeaking) {
                        recognition.start();
                    }
                }, 500);
            } else {
                document.getElementById('voice-status').textContent = 'Click to start';
                document.getElementById('voice-assistant').classList.remove('active');
            }
        };

        recognition.onresult = (event) => {
            if (!isSpeaking) {
                const command = event.results[event.results.length - 1][0].transcript.toLowerCase();
                document.getElementById('recognized-text').textContent = `Recognized: ${command}`;
                document.getElementById('recognized-text').style.display = 'block';
                setTimeout(() => {
                    document.getElementById('recognized-text').style.display = 'none';
                }, 3000);
                processCommand(command);
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            if (event.error !== 'no-speech' && isListening && !isSpeaking) {
                setTimeout(() => {
                    if (isListening && !isSpeaking) {
                        recognition.start();
                    }
                }, 1000);
            }
        };
    }
}

function speakText(text) {
    if (recognition) {
        recognition.stop();
    }
    
    speechSynthesis.cancel();
    
    if (resumeRecognitionTimeout) {
        clearTimeout(resumeRecognitionTimeout);
    }

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Set speaking state before speech starts
    isSpeaking = true;
    document.getElementById('voice-status').textContent = 'Speaking...';

    utterance.onstart = () => {
        isSpeaking = true;
        if (recognition) {
            recognition.stop();
        }
    };

    utterance.onend = () => {
        isSpeaking = false;
        if (isListening) {
            document.getElementById('voice-status').textContent = 'Listening...';
            // Add a delay before resuming recognition
            resumeRecognitionTimeout = setTimeout(() => {
                if (isListening && !isSpeaking && recognition) {
                    recognition.start();
                }
            }, 1000); // Increased delay to ensure no self-listening
        } else {
            document.getElementById('voice-status').textContent = 'Click to start';
        }
    };

    // Select voices and apply emotion settings
    let voices = speechSynthesis.getVoices();
    if (voices.length > 0) {
        const preferredVoice = voices.find(voice => 
            voice.lang.includes('en') && 
            (voice.name.includes('Samantha') || 
             voice.name.includes('Google') || 
             voice.name.includes('Natural'))
        ) || voices[0];
        utterance.voice = preferredVoice;
    }

    const emotion = detectEmotion(text);
    utterance.pitch = emotion.pitch;
    utterance.rate = emotion.rate;
    utterance.volume = emotion.volume;

    speechSynthesis.speak(utterance);
}

let scrollInterval = null;
let inappropriateCounter = 0;
let lastInappropriateTime = null;

function processCommand(command) {
    if (isSpeaking) return;

    const inappropriateWords = [
        'you are stupid',
        'you are an idiot',
        'fuck you',
        'you are a piece of shit',
        'are you dumb',
        'you are such a moron',
        'go to hell',
        'shut the fuck up',
        'you suck',
        'you are worthless',
        'you are a loser',
        'nobody cares about you',
        'you are a waste of space',
        'kill yourself',
        'you fucker',
        'you\'re a disgrace',
        'you\'re retarded',
        'you smell like shit',
        'get lost, idiot',
        'you are a failure',
        'you are pathetic',
        'you are disgusting',
        'you are a coward',
        'you are a traitor',
        'you are a liar',
        'you are a cheater',
        'you are a fraud',
        'you are a scumbag',
        'you are a waste of time',
        'you are a disappointment',
        'you are a burden'
    ];
    const containsInappropriateLanguage = inappropriateWords.some(word => command.toLowerCase().includes(word));

    if (containsInappropriateLanguage) {
        inappropriateCounter++;
        if (inappropriateCounter >= 3) {
            const now = new Date();
            if (lastInappropriateTime && (now - lastInappropriateTime) < 24 * 60 * 60 * 1000) {
                speakText("You have used inappropriate language too many times. Voice assistant will stop working for 24 hours.");
                isListening = false;
                recognition.stop();
                return;
            } else {
                inappropriateCounter = 1;
                lastInappropriateTime = now;
            }
        }

        // Log inappropriate language to the backend
        fetch('/log_inappropriate_language', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: command })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message && data.message.includes('disabled')) {
                speakText(data.message);
                isListening = false;
                recognition.stop();
            } else {
                speakText("Please do not use inappropriate language.");
            }
        })
        .catch(() => speakText("Sorry, there was an error logging inappropriate language."));

        return;
    }

    // Check for stop commands first
    if (command.includes('stop assistant') || 
    command.includes('stop listening') || 
    command.includes('turn off')) {
        isListening = false;
        speakText('Voice assistant deactivated');
        recognition.stop();
        return;
    }
    if (command.includes('activate voice assistant')) {
        isListening = true;
        speakText('Voice assistant activated');
        recognition.start();
        return;
    }

    for (let key in conversations) {
        if (command.includes(key)) {
            const responses = conversations[key];
            const response = responses[Math.floor(Math.random() * responses.length)];
            speakText(response);
            return;
        }
    }
     // Navigation commands
     const navigationCommands = {
        'home': '/home',
        'messages': '/messages',
        'settings': '/settings',
        'search': '/search',
        'post': '/post',
        'notifications': '/notifications',
        'profile': '/profile',
        'logout': '/logout'
    };

    for (let key in navigationCommands) {
        if (command.includes(key)) {
            const pageName = key.charAt(0).toUpperCase() + key.slice(1); // Capitalize first letter
            speakText(`Navigating you to ${pageName}`);
            window.location.href = navigationCommands[key];
            return;
        }
    }


    // Search user command
    if (command.includes('search for user') || command.includes('find user')) {
        const username = command.replace(/search for user|find user/gi, '').trim();
        if (username) {
            fetch(`/search_user?username=${encodeURIComponent(username)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.users && data.users.length > 0) {
                        showSearchResultPopup(data.users); // Pass all users to the popup
                        speakText(`Found ${data.users.length} user${data.users.length > 1 ? 's' : ''}. Click to view profile.`);
                    } else {
                        speakText("Sorry, I couldn't find any users with that name.");
                    }
                })
                .catch(() => speakText("Sorry, there was an error searching for users."));
        } else {
            speakText("Please specify a username to search for.");
        }
        return;
    }

    // Follow/Unfollow commands
// Updated follow command handling
if (command.startsWith('follow')) {
    const username = command.replace(/^follow\s+(user\s+)?/i, '').trim();
    if (username) {
        fetch('/follow_unfollow_voice', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ action: 'follow', username: username })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                speakText(data.message);
            } else {
                speakText(data.error || `Error following ${username}`);
            }
        })
        .catch(() => speakText("Network error"));
    } else {
        speakText("Please specify a username to follow");
    }
    return;
}

// Updated unfollow command handling
if (command.startsWith('unfollow')) {
    const username = command.replace(/^unfollow\s+(user\s+)?/i, '').trim();
    if (username) {
        fetch('/follow_unfollow_voice', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ action: 'unfollow', username: username })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                speakText(data.message);
            } else {
                speakText(data.error || `Error unfollowing ${username}`);
            }
        })
        .catch(() => speakText("Network error"));
    } else {
        speakText("Please specify a username to unfollow");
    }
    return;
}

    // Scrolling commands
    if (command.includes('start scrolling down')|| command.includes('scroll down')) {
        if (scrollInterval) clearInterval(scrollInterval);
        scrollInterval = setInterval(() => {
            window.scrollBy(0, 5);
        }, 50);
        speakText("Starting auto-scroll down.");
        return;
    }
    else if (command.includes('start scrolling down faster')|| command.includes('scroll down faster')) {
        if (scrollInterval) clearInterval(scrollInterval);
        scrollInterval = setInterval(() => {
            window.scrollBy(0, 10);
        }, 50);
        speakText("Starting auto-scroll down faster.");
        return;
    }
    else if (command.includes('start scrolling down more faster')|| command.includes('scroll down more faster')) {
        if (scrollInterval) clearInterval(scrollInterval);
        scrollInterval = setInterval(() => {
            window.scrollBy(0, 15);
        }, 50);
        speakText("Starting auto-scroll down.");
        return;
    }
    

    if (command.includes('start scrolling up')|| command.includes('scroll up')) {
        if (scrollInterval) clearInterval(scrollInterval);
        scrollInterval = setInterval(() => {
            window.scrollBy(0, -5);
        }, 50);
        speakText("Starting auto-scroll up.");
        return;
    }
    if (command.includes('start scrolling up faster')|| command.includes('scroll up faster')) {
        if (scrollInterval) clearInterval(scrollInterval);
        scrollInterval = setInterval(() => {
            window.scrollBy(0, -10);
        }, 50);
        speakText("Starting auto-scroll up faster.");
        return;
    }
    if (command.includes('start scrolling up more faster')|| command.includes('scroll up more faster')) {
        if (scrollInterval) clearInterval(scrollInterval);
        scrollInterval = setInterval(() => {
            window.scrollBy(0, -15);
        }, 50);
        speakText("Starting auto-scroll up.");
        return;
    }

    if (command.includes('stop scrolling')) {
        if (scrollInterval) {
            clearInterval(scrollInterval);
            scrollInterval = null;
            speakText("Stopping auto-scroll.");
        }
        return;
    }

    if (command.includes('switch to default mode') || command.includes('default mode')) {
        fetch('/change_background', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'theme=default'
        })
        .then(() => {
            speakText('Switched to default mode');
            setTimeout(() => window.location.reload(), 1000);
        });
        return;
    }

    if (command.includes('switch to light mode') || command.includes('light mode')) {
        fetch('/change_background', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'theme=light'
        })
        .then(() => {
            speakText('Switched to light mode');
            setTimeout(() => window.location.reload(), 1000);
        });
        return;
    }
    const captionPattern = /post a caption: (.+)/i;
    const captionMatch = command.match(captionPattern);
    if (captionMatch) {
        const content = captionMatch[1].trim();
        if (content) {
            fetch('/create_voice_post', {
                method: 'POST',
                body: new FormData().append('content', content)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    speakText('Caption posted successfully!');
                } else {
                    speakText(data.error || 'Sorry, there was an error posting the caption.');
                }
            })
            .catch(() => speakText('Sorry, there was an error posting the caption.'));
        } else {
            speakText('Please provide a caption to post.');
        }
        return;
    }

    // Post/upload a photo/video with a caption
    const mediaWithCaptionPattern = /(post|upload) (a|a photo|a video) with caption: (.+)/i;
    const mediaWithCaptionMatch = command.match(mediaWithCaptionPattern);
    if (mediaWithCaptionMatch) {
        const isVideo = mediaWithCaptionMatch[2].includes('video');
        const content = mediaWithCaptionMatch[3].trim();

        speakText(`Please select a ${isVideo ? 'video' : 'photo'} to upload${content ? ' with the caption: ' + content : ''}`);

        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = isVideo ? 'video/*' : 'image/*';

        fileInput.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                const formData = new FormData();
                formData.append('content', content);
                formData.append('media', file);
                formData.append('media_type', isVideo ? 'video' : 'photo');

                fetch('/create_voice_post', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        speakText(`${isVideo ? 'Video' : 'Photo'} posted successfully!`);
                        setTimeout(() => window.location.reload(), 2000);
                    } else {
                        speakText(data.error || `Sorry, there was an error posting the ${isVideo ? 'video' : 'photo'}.`);
                    }
                })
                .catch(() => speakText(`Sorry, there was an error posting the ${isVideo ? 'video' : 'photo'}.`));
            }
        };
        fileInput.click();
        return;
    }

    // Post/upload a photo/video without a caption
    const mediaPattern = /(post|upload) (a|a photo|a video)/i;
    if (command.match(mediaPattern)) {
        const isVideo = command.includes('video');

        speakText(`Please select a ${isVideo ? 'video' : 'photo'} to upload`);

        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = isVideo ? 'video/*' : 'image/*';

        fileInput.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                const formData = new FormData();
                formData.append('media', file);
                formData.append('media_type', isVideo ? 'video' : 'photo');

                fetch('/create_voice_post', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        speakText(`${isVideo ? 'Video' : 'Photo'} posted successfully!`);
                        setTimeout(() => window.location.reload(), 2000);
                    } else {
                        speakText(data.error || `Sorry, there was an error posting the ${isVideo ? 'video' : 'photo'}.`);
                    }
                })
                .catch(() => speakText(`Sorry, there was an error posting the ${isVideo ? 'video' : 'photo'}.`));
            }
        };
        fileInput.click();
        return;
    }

    

    // Laugh command
    if (command.includes('make me laugh') || command.includes('tell me a joke')) {
        const jokes = [
            "Why don’t bees have phones? They just buzz! 😆",
            "What do you call a bee who can’t stop talking? A BEE-talker! 🤣",
            "Why do bees hum? They don't know the lyrics! 🎶",
            "What do you call a bee with no friends? A BUMBLE-ALONE! 🐝"
        ];
        const joke = jokes[Math.floor(Math.random() * jokes.length)];
        speakText(joke, { pitch: 1.3, rate: 1.2, volume: 1.0 });
        return;
    }

    // If no command matched
    speakText("I didn't understand that command. Please try again.");
}

function showSearchResultPopup(users) {
const popup = document.createElement('div');
popup.className = 'search-result-popup';
popup.innerHTML = `
<div class="search-result-content">
    <h3>Search Results</h3>
    ${users.map(user => `
        <div class="user-result">
            <img src="/static/uploads/${user.profile_picture || 'd1.jpg'}" alt="${user.username}" class="profile-pic">
            <span class="username">${user.username}</span>
            <button onclick="redirectToProfile('${user.username}')">View Profile</button>
        </div>
    `).join('')}
</div>
`;
document.body.appendChild(popup);

// Close popup when clicking outside
document.addEventListener('click', (e) => {
if (!popup.contains(e.target)) {
    popup.remove();
}
});
}

// Function to redirect to user profile
function redirectToProfile(username) {
window.location.href = `/profile/${username}`;
}




function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

function toggleVoiceRecognition() {
    fetch('/check_voice_assistant_block')
        .then(response => response.json())
        .then(data => {
            if (data.blocked) {
                const blockedUntil = new Date(data.blocked_until);
                const now = new Date();
                const remaining = Math.round((blockedUntil - now) / 1000);

                if (remaining > 0) {
                    speakText(`Voice assistant blocked for ${remaining} more seconds`);
                    return;
                }
            }

            if (!recognition) {
                initializeSpeechRecognition();
            }

            if (isListening) {
                isListening = false;
                if (recognition) {
                    recognition.stop();
                }
                speakText('Voice assistant deactivated');
            } else {
                isListening = true;
                if (!isSpeaking) {
                    speakText('Voice assistant activated');
                }
                recognition.start();
            }
        })
        .catch(() => speakText("You have used inappropriate languages too many times, so voice assistant is currently unavailable."));
}

// Check if the voice assistant should be activated on page load
document.addEventListener('DOMContentLoaded', () => {
    fetch('/check_voice_assistant_state')
        .then(response => response.json())
        .then(data => {
            if (data.state === 'active') {
                isListening = true;
                if (!isSpeaking) {
                    speakText('Voice assistant activated');
                }
                recognition.start();
            }
        })
        .catch(error => console.error('Error checking voice assistant state:', error));
});

// Event Listeners
document.getElementById('voice-assistant').addEventListener('click', toggleVoiceRecognition);

// Initialize voices
speechSynthesis.onvoiceschanged = () => {
    speechSynthesis.getVoices();
};

// Add visual feedback for voice commands
document.querySelectorAll('[data-voice-command]').forEach(element => {
    element.addEventListener('mouseover', () => {
        if (isListening) {
            element.setAttribute('title', `Say "Go to ${element.getAttribute('data-voice-command')}" to navigate`);
        }
    });
});