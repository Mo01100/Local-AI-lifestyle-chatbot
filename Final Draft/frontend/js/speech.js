/**
 * Speech Recognition Module
 * Uses browser's built-in Web Speech API (no backend needed!)
 * Simple, reliable, and works offline in Chrome/Edge
 */

class SpeechRecognition {
    constructor() {
        this.recognition = null;
        this.isRecording = false;
        this.micBtn = document.getElementById('micBtn');
        this.chatInput = document.getElementById('chatInput');
        this.speechLang = document.getElementById('speechLang');
        this._accumulatedText = ''; // stores confirmed words across segments

        this.init();
    }

    init() {
        // Check if browser supports Web Speech API
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            console.warn('Web Speech API not supported');
            this.micBtn.disabled = true;
            this.micBtn.title = 'Speech recognition not supported in this browser';
            return;
        }

        // Initialize speech recognition
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;       // keep listening until user clicks stop
        this.recognition.interimResults = true;   // show live partial results in the textarea
        this.recognition.maxAlternatives = 1;

        // Set initial language from selector
        this.recognition.lang = this.speechLang.value;

        // Update language when selector changes
        this.speechLang.addEventListener('change', () => {
            this.recognition.lang = this.speechLang.value;
        });

        // Handle results
        this.recognition.onresult = (event) => {
            let interim = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    // Confirmed segment — append to accumulated text
                    this._accumulatedText += (this._accumulatedText ? ' ' : '') + transcript.trim();
                } else {
                    // Still being spoken — show as preview
                    interim = transcript;
                }
            }
            // Show confirmed + live interim text in the textarea
            this.chatInput.value = this._accumulatedText + (interim ? ' ' + interim : '');
            this.chatInput.style.height = 'auto';
            this.chatInput.style.height = this.chatInput.scrollHeight + 'px';
        };

        // Handle errors
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.hideProcessing();

            switch (event.error) {
                case 'no-speech':
                    this.showError('No speech detected. Please try again.');
                    break;
                case 'audio-capture':
                    this.showError('No microphone found. Please check your device.');
                    break;
                case 'not-allowed':
                    this.showError('Microphone access denied. Please allow microphone access.');
                    break;
                case 'network':
                    this.showError('Network error. Speech recognition requires internet connection.');
                    break;
                default:
                    this.showError('Speech recognition error: ' + event.error);
            }
        };

        // Handle end of recognition
        this.recognition.onend = () => {
            // In continuous mode, onend fires if the browser interrupts the session.
            // Restart automatically only if the user hasn't manually stopped.
            if (this.isRecording) {
                try { this.recognition.start(); } catch (_) { }
            } else {
                this.hideProcessing();
            }
        };

        // Handle start
        this.recognition.onstart = () => {
            this.isRecording = true;
            this.updateUI(true);
        };

        // Add click listener
        this.micBtn.addEventListener('click', () => this.toggleRecording());
    }

    toggleRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    }

    startRecording() {
        try {
            this._accumulatedText = '';         // clear accumulator for fresh recording
            this.chatInput.value = '';          // clear any previous text
            this.chatInput.style.height = 'auto';
            // Update language before starting
            this.recognition.lang = this.speechLang.value;
            this.recognition.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
            this.showError('Could not start speech recognition. Please try again.');
        }
    }

    stopRecording() {
        this.isRecording = false;   // set first so onend doesn't restart
        try {
            this.recognition.stop();
        } catch (error) {
            console.error('Error stopping recognition:', error);
        }
    }

    updateUI(recording) {
        const icon = this.micBtn.querySelector('i');

        if (recording) {
            this.micBtn.classList.add('recording');
            icon.classList.remove('fa-microphone');
            icon.classList.add('fa-stop');
            this.micBtn.title = 'Stop recording';
        } else {
            this.micBtn.classList.remove('recording');
            icon.classList.remove('fa-stop');
            icon.classList.add('fa-microphone');
            this.micBtn.title = 'Voice input (Browser)';
        }
    }

    showProcessing() {
        const icon = this.micBtn.querySelector('i');
        this.micBtn.classList.add('processing');
        icon.classList.remove('fa-microphone', 'fa-stop');
        icon.classList.add('fa-spinner', 'fa-spin');
        this.micBtn.disabled = true;
        this.micBtn.title = 'Processing...';
    }

    hideProcessing() {
        const icon = this.micBtn.querySelector('i');
        this.micBtn.classList.remove('processing', 'recording');
        icon.classList.remove('fa-spinner', 'fa-spin', 'fa-stop');
        icon.classList.add('fa-microphone');
        this.micBtn.disabled = false;
        this.micBtn.title = 'Voice input (Browser)';
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'speech-error';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            position: fixed;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            background: #f44336;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 10000;
            animation: slideUp 0.3s ease;
            max-width: 80%;
            text-align: center;
        `;

        document.body.appendChild(errorDiv);

        setTimeout(() => {
            errorDiv.style.animation = 'slideDown 0.3s ease';
            setTimeout(() => errorDiv.remove(), 300);
        }, 4000);
    }
}

// Initialize speech recognition when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.speechRecognition = new SpeechRecognition();
});
