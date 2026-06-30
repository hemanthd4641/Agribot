/**
 * Raitha mitra - Frontend Logic
 * Refactored for modularity, modern UI features, and performance.
 */

document.addEventListener('DOMContentLoaded', () => {
    
    // --- State & Config ---
    const state = {
        isProcessing: false,
        isRecording: false,
        selectedFile: null,
        mediaRecorder: null,
        audioChunks: [],
        settings: {
            theme: localStorage.getItem('agri-theme') || 'dark',
            fontSize: localStorage.getItem('agri-font-size') || 'normal',
            speechSpeed: parseFloat(localStorage.getItem('agri-speech-speed')) || 1.0,
            language: localStorage.getItem('agri-language') || 'en-IN'
        }
    };

    // --- DOM Elements ---
    const DOM = {
        // Layout
        html: document.documentElement,
        body: document.body,
        sidebar: document.getElementById('sidebar'),
        mobileMenuBtn: document.getElementById('mobileMenuBtn'),
        closeSidebarBtn: document.getElementById('closeSidebarBtn'),
        
        // Chat Area
        chatArea: document.getElementById('chatArea'),
        chatMessages: document.getElementById('chatMessages'),
        welcomeScreen: document.getElementById('welcomeScreen'),
        scrollToBottomBtn: document.getElementById('scrollToBottomBtn'),
        
        // Input Area
        messageInput: document.getElementById('messageInput'),
        sendBtn: document.getElementById('sendBtn'),
        voiceBtn: document.getElementById('voiceBtn'),
        attachBtn: document.getElementById('attachBtn'),
        fileInput: document.getElementById('fileInput'),
        dropZone: document.getElementById('dropZone'),
        imagePreviewArea: document.getElementById('imagePreviewArea'),
        imagePreviewElement: document.getElementById('imagePreviewElement'),
        removeImageBtn: document.getElementById('removeImageBtn'),
        
        // Actions
        newChatBtn: document.getElementById('newChatBtn'),
        clearChatBtn: document.getElementById('clearChatBtn'),
        downloadChatBtn: document.getElementById('downloadChatBtn'),
        themeToggleBtn: document.getElementById('themeToggleBtn'),
        
        // Settings Modal
        settingsModal: document.getElementById('settingsModal'),
        openSettingsBtn: document.getElementById('openSettingsBtn'),
        closeSettingsBtn: document.getElementById('closeSettingsBtn'),
        themeOptions: document.querySelectorAll('.theme-option'),
        fontSizeSelect: document.getElementById('fontSizeSelect'),
        speechSpeedRange: document.getElementById('speechSpeedRange'),
        speedLabel: document.getElementById('speedLabel'),
        languageSelect: document.getElementById('languageSelect'),
        
        // Misc
        audioPlayer: document.getElementById('audioPlayer'),
        toastContainer: document.getElementById('toastContainer'),
        featureCards: document.querySelectorAll('.feature-card')
    };

    // --- Initialization ---
    init();

    function init() {
        applySettings();
        setupEventListeners();
        setupMarked();
        checkScroll();
        DOM.messageInput.focus();
    }

    // --- Markdown Configuration ---
    function setupMarked() {
        if (typeof marked !== 'undefined' && typeof hljs !== 'undefined') {
            marked.setOptions({
                highlight: function (code, lang) {
                    const language = hljs.getLanguage(lang) ? lang : 'plaintext';
                    return hljs.highlight(code, { language }).value;
                },
                langPrefix: 'hljs language-',
                breaks: true,
                gfm: true
            });
        }
    }

    // --- Event Listeners ---
    function setupEventListeners() {
        // Auto-resize textarea
        DOM.messageInput.addEventListener('input', handleTextareaInput);
        
        // Send message (Enter to send, Shift+Enter for new line)
        DOM.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        DOM.sendBtn.addEventListener('click', sendMessage);
        
        // Feature Cards Click
        DOM.featureCards.forEach(card => {
            card.addEventListener('click', () => {
                const prompt = card.getAttribute('data-prompt');
                DOM.messageInput.value = prompt;
                handleTextareaInput();
                sendMessage();
            });
        });

        // Sidebar Toggle (Mobile)
        DOM.mobileMenuBtn.addEventListener('click', () => DOM.sidebar.classList.add('open'));
        DOM.closeSidebarBtn.addEventListener('click', () => DOM.sidebar.classList.remove('open'));
        
        // File Upload (Drag & Drop + Click)
        DOM.attachBtn.addEventListener('click', () => DOM.fileInput.click());
        DOM.fileInput.addEventListener('change', handleFileSelect);
        DOM.removeImageBtn.addEventListener('click', clearImagePreview);
        
        DOM.dropZone.addEventListener('dragover', (e) => { e.preventDefault(); DOM.dropZone.classList.add('drag-over'); });
        DOM.dropZone.addEventListener('dragleave', () => DOM.dropZone.classList.remove('drag-over'));
        DOM.dropZone.addEventListener('drop', handleFileDrop);

        // Voice
        DOM.voiceBtn.addEventListener('click', toggleRecording);
        
        // Actions
        DOM.newChatBtn.addEventListener('click', clearConversation);
        DOM.clearChatBtn.addEventListener('click', clearConversation);
        DOM.downloadChatBtn.addEventListener('click', downloadChatPDF);
        DOM.themeToggleBtn.addEventListener('click', toggleThemeAction);
        
        // Scroll Management
        DOM.chatArea.addEventListener('scroll', checkScroll);
        DOM.scrollToBottomBtn.addEventListener('click', scrollToBottom);

        // Settings Modal
        DOM.openSettingsBtn.addEventListener('click', () => DOM.settingsModal.classList.add('active'));
        DOM.closeSettingsBtn.addEventListener('click', () => DOM.settingsModal.classList.remove('active'));
        DOM.settingsModal.addEventListener('click', (e) => {
            if (e.target === DOM.settingsModal) DOM.settingsModal.classList.remove('active');
        });
        
        // Settings Changes
        DOM.themeOptions.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const theme = e.currentTarget.getAttribute('data-theme');
                updateSetting('theme', theme);
            });
        });
        
        DOM.fontSizeSelect.addEventListener('change', (e) => updateSetting('fontSize', e.target.value));
        DOM.speechSpeedRange.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value).toFixed(1);
            DOM.speedLabel.textContent = `${val}x`;
            updateSetting('speechSpeed', val);
        });
        DOM.languageSelect.addEventListener('change', (e) => updateSetting('language', e.target.value));
    }

    // --- Settings Management ---
    function updateSetting(key, value) {
        state.settings[key] = value;
        localStorage.setItem(`agri-${key}`, value);
        applySettings();
    }

    function applySettings() {
        // Theme
        DOM.html.setAttribute('data-theme', state.settings.theme);
        DOM.themeOptions.forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-theme') === state.settings.theme);
        });
        
        // Font Size
        DOM.body.setAttribute('data-font-size', state.settings.fontSize);
        DOM.fontSizeSelect.value = state.settings.fontSize;
        
        // Speech
        DOM.speechSpeedRange.value = state.settings.speechSpeed;
        DOM.speedLabel.textContent = `${parseFloat(state.settings.speechSpeed).toFixed(1)}x`;
        if (DOM.audioPlayer) DOM.audioPlayer.playbackRate = state.settings.speechSpeed;
        
        DOM.languageSelect.value = state.settings.language;
    }

    function toggleThemeAction() {
        const newTheme = state.settings.theme === 'dark' ? 'light' : 'dark';
        updateSetting('theme', newTheme);
    }

    // --- Input Handling ---
    function handleTextareaInput() {
        const input = DOM.messageInput;
        input.style.height = 'auto';
        input.style.height = (input.scrollHeight) + 'px';
        
        const hasValue = input.value.trim().length > 0;
        DOM.sendBtn.disabled = !hasValue && !state.selectedFile;
    }

    // --- File Handling ---
    function handleFileSelect(e) {
        const file = e.target.files[0];
        processFile(file);
    }

    function handleFileDrop(e) {
        e.preventDefault();
        DOM.dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) {
            processFile(e.dataTransfer.files[0]);
        }
    }

    function processFile(file) {
        if (!file) return;
        if (!file.type.startsWith('image/')) {
            showToast('Only image files are supported.', 'error');
            return;
        }
        if (file.size > 4 * 1024 * 1024) {
            showToast('Image is too large. Max 4MB allowed.', 'error');
            return;
        }
        
        state.selectedFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            DOM.imagePreviewElement.src = e.target.result;
            DOM.imagePreviewArea.classList.add('active');
            handleTextareaInput(); // Enable send button
        };
        reader.readAsDataURL(file);
    }

    function clearImagePreview() {
        state.selectedFile = null;
        DOM.fileInput.value = '';
        DOM.imagePreviewElement.src = '';
        DOM.imagePreviewArea.classList.remove('active');
        handleTextareaInput();
    }

    // --- Scroll Management ---
    function checkScroll() {
        const { scrollTop, scrollHeight, clientHeight } = DOM.chatArea;
        // Show button if not at the bottom
        if (scrollHeight - scrollTop - clientHeight > 100) {
            DOM.scrollToBottomBtn.classList.add('visible');
        } else {
            DOM.scrollToBottomBtn.classList.remove('visible');
        }
    }

    function scrollToBottom(smooth = true) {
        DOM.chatArea.scrollTo({
            top: DOM.chatArea.scrollHeight,
            behavior: smooth ? 'smooth' : 'auto'
        });
    }

    // --- Chat Logic ---
    async function sendMessage() {
        const text = DOM.messageInput.value.trim();
        const hasImage = state.selectedFile !== null;

        if ((!text && !hasImage) || state.isProcessing) return;

        let queryText = text;
        if (!queryText && hasImage) {
            queryText = 'Please analyze this image from an agricultural perspective.';
        }

        // Setup UI for processing
        state.isProcessing = true;
        DOM.messageInput.value = '';
        handleTextareaInput(); // reset height & disable send button
        DOM.sendBtn.disabled = true;
        DOM.voiceBtn.disabled = true;
        DOM.attachBtn.disabled = true;
        
        // Hide welcome screen if present
        if (DOM.welcomeScreen) {
            DOM.welcomeScreen.style.display = 'none';
        }

        // Add user message to UI
        const imageSrc = hasImage ? DOM.imagePreviewElement.src : null;
        appendMessage(queryText, 'user', null, imageSrc);
        
        // Save file reference and clear preview
        const fileToSend = state.selectedFile;
        clearImagePreview();
        
        // Show typing indicator
        showTypingIndicator();

        try {
            const formData = new FormData();
            if (hasImage) {
                formData.append('image', fileToSend, fileToSend.name || 'image.jpg');
            }
            formData.append('text', queryText);

            const response = await fetch('/chat', {
                method: 'POST',
                body: formData // Fetch sets Content-Type automatically for FormData
            });

            if (!response.ok) {
                const errData = await response.json().catch(()=>({}));
                throw new Error(errData.error || `Server error: ${response.status}`);
            }

            const data = await response.json();
            
            removeTypingIndicator();
            if (data.text) {
                appendMessage(data.text, 'bot', data.cache);
                if (data.voice) playVoice(data.voice);
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            removeTypingIndicator();
            appendMessage(`Sorry, an error occurred: ${error.message}. Please try again.`, 'bot');
            showToast('Message failed to send', 'error');
        } finally {
            state.isProcessing = false;
            DOM.voiceBtn.disabled = false;
            DOM.attachBtn.disabled = false;
            DOM.messageInput.focus();
        }
    }

    // --- Voice Recording ---
    function toggleRecording() {
        if (state.isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    }

    async function startRecording() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showToast('Voice recording is not supported in your browser.', 'error');
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            state.audioChunks = [];
            
            // Try to use a compressed format
            let options = {};
            if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
                options = { mimeType: 'audio/webm;codecs=opus' };
            }
            
            state.mediaRecorder = new MediaRecorder(stream, options);
            
            state.mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) state.audioChunks.push(e.data);
            };
            
            state.mediaRecorder.onstop = () => {
                const blob = new Blob(state.audioChunks, { type: 'audio/webm' });
                stream.getTracks().forEach(t => t.stop());
                sendAudio(blob);
            };
            
            state.mediaRecorder.start(250); // collect chunks every 250ms
            state.isRecording = true;
            DOM.voiceBtn.classList.add('recording');
            showToast('Listening...', 'info');
            
        } catch (error) {
            console.error('Mic error:', error);
            showToast('Microphone access denied or error occurred.', 'error');
        }
    }

    function stopRecording() {
        if (state.mediaRecorder && state.mediaRecorder.state !== 'inactive') {
            state.mediaRecorder.stop();
        }
        state.isRecording = false;
        DOM.voiceBtn.classList.remove('recording');
    }

    async function sendAudio(blob) {
        if (state.isProcessing) return;
        
        state.isProcessing = true;
        DOM.sendBtn.disabled = true;
        DOM.voiceBtn.disabled = true;
        
        if (DOM.welcomeScreen) DOM.welcomeScreen.style.display = 'none';
        showTypingIndicator(); // Show indicator while transcribing and processing

        try {
            const fd = new FormData();
            fd.append('audio', blob, 'recording.webm');
            
            const response = await fetch('/chat', {
                method: 'POST',
                body: fd
            });

            if (!response.ok) throw new Error('Failed to process audio');
            const data = await response.json();
            
            removeTypingIndicator();
            
            if (data.transcription) {
                appendMessage(data.transcription, 'user');
            }
            if (data.text) {
                appendMessage(data.text, 'bot', data.cache);
                if (data.voice) playVoice(data.voice);
            }
            
        } catch (error) {
            console.error('Audio error:', error);
            removeTypingIndicator();
            appendMessage('Sorry, could not process your voice request.', 'bot');
            showToast('Audio processing failed', 'error');
        } finally {
            state.isProcessing = false;
            DOM.voiceBtn.disabled = false;
            DOM.attachBtn.disabled = false;
            DOM.messageInput.focus();
        }
    }

    function playVoice(src) {
        if (!src) return;
        DOM.audioPlayer.src = src;
        DOM.audioPlayer.playbackRate = state.settings.speechSpeed;
        DOM.audioPlayer.play().catch(e => console.warn('Audio auto-play prevented', e));
    }

    // --- UI Helpers ---
    function appendMessage(text, type, cache = null, imageUrl = null) {
        const isUser = type === 'user';
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${type}`;
        
        // Avatar icon
        const iconClass = isUser ? 'ph-user' : 'ph-plant';
        const avatarColorClass = isUser ? '' : 'brand-bg';
        
        // Image tag if present
        const imgTag = imageUrl ? `<img class="message-image" src="${imageUrl}" alt="Uploaded image">` : '';
        
        // Content Formatting (Markdown for bot)
        let formattedText = escapeHtml(text).replace(/\n/g, '<br>');
        if (!isUser && typeof marked !== 'undefined') {
            formattedText = marked.parse(text);
        }

        // Cache Tag
        let cacheTag = '';
        if (cache && cache.cached_tokens > 0) {
            cacheTag = `<div class="cache-badge" title="Prompt Tokens: ${cache.prompt_tokens}, Cached: ${cache.cached_tokens}"><i class="ph-fill ph-lightning"></i> ${cache.hit_rate}% Cached</div>`;
        }
        
        // Current Time
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        msgDiv.innerHTML = `
            <div class="message-avatar">
                <i class="ph-fill ${iconClass}"></i>
            </div>
            <div class="message-content">
                ${imgTag}
                <div class="message-bubble ${!isUser ? 'markdown-body' : ''}">
                    ${formattedText}
                </div>
                <div class="message-meta">
                    <span>${timeStr}</span>
                    ${cacheTag}
                    ${!isUser ? `
                    <div class="msg-actions">
                        <button class="msg-action-btn copy-btn" title="Copy response" data-text="${escapeHtml(text)}">
                            <i class="ph ph-copy"></i>
                        </button>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;

        DOM.chatMessages.appendChild(msgDiv);
        
        // Bind copy event
        if (!isUser) {
            const copyBtn = msgDiv.querySelector('.copy-btn');
            if (copyBtn) {
                copyBtn.addEventListener('click', (e) => {
                    const txt = e.currentTarget.getAttribute('data-text');
                    navigator.clipboard.writeText(txt).then(() => {
                        showToast('Copied to clipboard', 'success');
                        const icon = copyBtn.querySelector('i');
                        icon.className = 'ph ph-check text-success';
                        setTimeout(() => { icon.className = 'ph ph-copy'; }, 2000);
                    });
                });
            }
        }
        
        scrollToBottom();
    }

    function showTypingIndicator() {
        const div = document.createElement('div');
        div.className = 'typing-indicator active';
        div.id = 'typingIndicator';
        div.innerHTML = `
            <div class="message-avatar"><i class="ph-fill ph-plant"></i></div>
            <div class="dot-flashing"></div>
        `;
        DOM.chatMessages.appendChild(div);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const ind = document.getElementById('typingIndicator');
        if (ind) ind.remove();
    }

    function escapeHtml(unsafe) {
        return (unsafe || '').toString()
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }

    // --- Actions ---
    async function clearConversation() {
        const msgCount = DOM.chatMessages.querySelectorAll('.message').length;
        if (msgCount === 0) return;
        
        if (!confirm('Are you sure you want to clear the conversation history?')) return;
        
        try {
            await fetch('/chat/clear', { method: 'POST' });
            // Clean DOM
            const msgs = DOM.chatMessages.querySelectorAll('.message, .typing-indicator');
            msgs.forEach(m => m.remove());
            if (DOM.welcomeScreen) DOM.welcomeScreen.style.display = 'flex';
            if (window.innerWidth <= 768) DOM.sidebar.classList.remove('open');
            showToast('Conversation cleared', 'success');
        } catch (e) {
            console.error('Failed to clear:', e);
            showToast('Failed to clear conversation', 'error');
        }
    }

    function downloadChatPDF() {
        if (typeof html2pdf === 'undefined') {
            showToast('PDF export library is loading or unavailable.', 'error');
            return;
        }
        
        if (DOM.chatMessages.querySelectorAll('.message').length === 0) {
            showToast('No conversation to export.', 'info');
            return;
        }

        showToast('Preparing PDF...', 'info');
        
        // Create a clone of messages to avoid messing up the UI scrolling during render
        const elementToPrint = document.createElement('div');
        elementToPrint.style.padding = '20px';
        elementToPrint.style.backgroundColor = '#ffffff'; // Force light bg for PDF
        elementToPrint.style.color = '#000000';
        elementToPrint.innerHTML = `
            <h2 style="text-align:center; margin-bottom: 20px; font-family: sans-serif;">Raitha mitra - Chat Log</h2>
        `;
        
        // Clone messages and adapt styles for printing
        const clone = DOM.chatMessages.cloneNode(true);
        const welcome = clone.querySelector('.welcome-screen');
        if (welcome) welcome.remove();
        
        elementToPrint.appendChild(clone);

        const opt = {
            margin:       10,
            filename:     `Raitha mitra_Chat_${new Date().toISOString().slice(0,10)}.pdf`,
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2, useCORS: true },
            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };

        html2pdf().set(opt).from(elementToPrint).save().then(() => {
            showToast('Chat downloaded successfully', 'success');
        }).catch(err => {
            console.error('PDF error:', err);
            showToast('Failed to generate PDF', 'error');
        });
    }

    // --- Toast Notifications ---
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let icon = 'ph-info';
        if (type === 'success') icon = 'ph-check-circle';
        if (type === 'error') icon = 'ph-warning-circle';
        
        toast.innerHTML = `
            <i class="ph-fill ${icon} toast-icon"></i>
            <span>${escapeHtml(message)}</span>
        `;
        
        DOM.toastContainer.appendChild(toast);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

});