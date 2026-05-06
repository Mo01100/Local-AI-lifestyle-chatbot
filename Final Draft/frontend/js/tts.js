/**
 * Text-to-Speech Module (Piper TTS)
 * Automatically uses the voice matching the selected speech language.
 * Calls the backend /api/tts/synthesize endpoint and plays the returned WAV.
 */

const TTS_API = `${typeof API_BASE !== 'undefined' ? API_BASE : '/api'}/tts`;

// Maps browser speech language codes (en-US, ar-SA, …) → short lang codes (en, ar, …)
const SPEECH_LANG_TO_CODE = {
    'en-US': 'en',
    'ar-SA': 'ar',
    'es-ES': 'es',
    'fr-FR': 'fr',
    'de-DE': 'de',
    'zh-CN': 'zh',
    'hi-IN': 'hi',
};

// Human-readable labels shown in the TTS language badge
const LANG_LABELS = {
    en: '🇺🇸 EN',
    ar: '🇸🇦 AR',
    es: '🇪🇸 ES',
    fr: '🇫🇷 FR',
    de: '🇩🇪 DE',
    zh: '🇨🇳 ZH',
    hi: '🇮🇳 HI',
};

class TTSManager {
    constructor() {
        this.isAvailable = false;
        this.currentAudio = null;
        this.activeSpeakBtn = null;
        this.languageVoices = {};   // lang code → voice model name from backend
        this.currentLanguage = 'en'; // tracks the selected language reactively
        this.ttsEnabled = this._loadEnabledState(); // persisted on/off toggle

        this._initLanguageFromSelector();
        this._checkAvailability();
        this._watchSpeechLangSelector();
        this._setupToggleButton();
    }

    _loadEnabledState() {
        // Default: enabled. User can toggle off, saved in localStorage.
        const saved = localStorage.getItem('ttsEnabled');
        return saved === null ? true : saved === 'true';
    }

    _saveEnabledState() {
        localStorage.setItem('ttsEnabled', String(this.ttsEnabled));
    }

    _setupToggleButton() {
        const btn = document.getElementById('ttsToggleBtn');
        if (!btn) return;
        btn.addEventListener('click', () => this.toggleTTS());
    }

    /** Toggle TTS on/off globally */
    toggleTTS() {
        this.ttsEnabled = !this.ttsEnabled;
        this._saveEnabledState();
        this._updateToggleBtn();
        this._applyEnabledStateToSpeakBtns();
        if (!this.ttsEnabled && this.currentAudio) {
            this._stopCurrentAudio();
        }
    }

    _updateToggleBtn() {
        const btn = document.getElementById('ttsToggleBtn');
        if (!btn) return;
        const icon = btn.querySelector('i');
        if (this.ttsEnabled) {
            btn.classList.remove('tts-off');
            btn.title = 'Disable text-to-speech';
            icon.classList.remove('fa-volume-mute');
            icon.classList.add('fa-volume-up');
        } else {
            btn.classList.add('tts-off');
            btn.title = 'Enable text-to-speech';
            icon.classList.remove('fa-volume-up');
            icon.classList.add('fa-volume-mute');
        }
    }

    /** Show or hide all existing speak buttons based on enabled state */
    _applyEnabledStateToSpeakBtns() {
        document.querySelectorAll('.tts-speak-btn').forEach(btn => {
            btn.style.display = this.ttsEnabled ? '' : 'none';
        });
    }

    async _checkAvailability() {
        try {
            const res = await fetch(`${TTS_API}/health`);
            if (!res.ok) return;
            const data = await res.json();
            this.isAvailable = data.status === 'available';
            this.languageVoices = data.language_voices || {};
            if (this.isAvailable) {
                this._updateLangBadge();
                this._updateToggleBtn();
                this._applyEnabledStateToSpeakBtns();
                document.getElementById('ttsLangBadge')?.classList.remove('hidden');
                document.getElementById('ttsToggleBtn')?.classList.remove('hidden');
            }
        } catch (e) {
            console.warn('TTS health check failed:', e);
        }
    }

    /** Read the initial language from the selector immediately on load */
    _initLanguageFromSelector() {
        const speechLang = document.getElementById('speechLang');
        if (speechLang) {
            this.currentLanguage = SPEECH_LANG_TO_CODE[speechLang.value] || 'en';
        }
    }

    /** Keep this.currentLanguage in sync whenever the selector changes */
    _watchSpeechLangSelector() {
        const speechLang = document.getElementById('speechLang');
        if (!speechLang) return;
        speechLang.addEventListener('change', () => {
            this.currentLanguage = SPEECH_LANG_TO_CODE[speechLang.value] || 'en';
            this._updateLangBadge();
        });
    }

    _updateLangBadge() {
        const badge = document.getElementById('ttsLangBadge');
        if (!badge) return;
        const lang = this.currentLanguage;
        badge.textContent = `🔊 ${LANG_LABELS[lang] || lang.toUpperCase()}`;
        badge.title = `TTS voice: ${lang} (${this.languageVoices[lang] || 'default'})`;
    }

    /** @deprecated use this.currentLanguage directly */
    _getSelectedLangCode() {
        return this.currentLanguage;
    }

    /**
     * Speak text using Piper TTS in the currently selected language.
     * @param {string} text  - Text to speak
     * @param {HTMLElement} btn - The speak button element (for UI state)
     */
    async speak(text, btn) {
        if (!this.isAvailable || !this.ttsEnabled) {
            console.warn('TTS not available or disabled');
            return;
        }

        // If already speaking, stop
        if (this.currentAudio) {
            this._stopCurrentAudio();
            if (this.activeSpeakBtn === btn) return; // toggle off
        }

        this._setButtonState(btn, 'loading');
        this.activeSpeakBtn = btn;

        try {
            const language = this.currentLanguage;  // always uses the currently selected language
            const res = await fetch(`${TTS_API}/synthesize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, language }),
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                console.error('TTS synthesis failed:', err);
                this._setButtonState(btn, 'idle');
                this.activeSpeakBtn = null;
                return;
            }

            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const audio = new Audio(url);
            this.currentAudio = audio;

            this._setButtonState(btn, 'speaking');

            audio.onended = () => {
                URL.revokeObjectURL(url);
                this.currentAudio = null;
                this.activeSpeakBtn = null;
                this._setButtonState(btn, 'idle');
            };

            audio.onerror = (e) => {
                console.error('Audio playback error:', e);
                URL.revokeObjectURL(url);
                this.currentAudio = null;
                this.activeSpeakBtn = null;
                this._setButtonState(btn, 'idle');
            };

            await audio.play();

        } catch (e) {
            console.error('TTS error:', e);
            this.currentAudio = null;
            this.activeSpeakBtn = null;
            this._setButtonState(btn, 'idle');
        }
    }

    _stopCurrentAudio() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
            this.currentAudio = null;
        }
        if (this.activeSpeakBtn) {
            this._setButtonState(this.activeSpeakBtn, 'idle');
            this.activeSpeakBtn = null;
        }
    }

    _setButtonState(btn, state) {
        if (!btn) return;
        const icon = btn.querySelector('i');
        if (!icon) return;

        btn.classList.remove('loading', 'speaking');
        icon.classList.remove('fa-volume-up', 'fa-spinner', 'fa-spin', 'fa-stop');

        switch (state) {
            case 'loading':
                btn.classList.add('loading');
                icon.classList.add('fa-spinner', 'fa-spin');
                btn.title = 'Generating speech…';
                btn.disabled = true;
                break;
            case 'speaking':
                btn.classList.add('speaking');
                icon.classList.add('fa-stop');
                btn.title = 'Stop speaking';
                btn.disabled = false;
                break;
            default: // 'idle'
                icon.classList.add('fa-volume-up');
                btn.title = 'Read aloud';
                btn.disabled = false;
        }
    }
}

// Global singleton — initialised when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.ttsManager = new TTSManager();
});
