/**
 * Settings Management
 *
 * This module manages the Settings page, which lets users configure:
 *   - Contrast Mode: normal, high, or low (accessibility)
 *   - Brightness: 0–200% (CSS filter applied to the page)
 *   - Font Size: small, medium, or large (CSS data attribute)
 *   - Theme: light or dark (CSS data attribute)
 *   - Language: preferred chat language code ('en', 'ar', 'es', etc.)
 *   - Notifications: whether browser notifications are enabled
 *   - Notification Sound: whether notification sounds play
 *
 * Each setting change is:
 *   1. Applied immediately to the DOM for instant visual feedback
 *   2. Persisted to the backend (and SQLite DB) via a PUT request
 *
 * On page load, current settings are fetched and all controls are pre-populated
 * so the page reflects what the user previously saved.
 */

// ─── Boot Sequence ────────────────────────────────────────────────────────────
// Wire up event listeners once the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initSettings();
});

/**
 * Initialise the Settings page.
 * Attaches change/input listeners to every control so that any change is:
 *   1. Applied to the page immediately (for instant visual feedback)
 *   2. Saved to the backend (persisted to the database)
 * Then loads the current saved settings to pre-populate all controls.
 */
function initSettings() {
    // ── Contrast Mode ────────────────────────────────────────────────────────
    // When the user chooses a contrast level, apply it visually and save it
    document.getElementById('contrastMode').addEventListener('change', async (e) => {
        applyContrast(e.target.value);                          // Instant visual feedback (defined in app.js)
        await updateSettings({ contrast_mode: e.target.value }); // Persist to backend
    });

    // ── Brightness ────────────────────────────────────────────────────────────
    const brightnessSlider = document.getElementById('brightness');
    const brightnessValue = document.getElementById('brightnessValue');

    // 'input' fires continuously while dragging the slider for real-time preview
    brightnessSlider.addEventListener('input', (e) => {
        const value = e.target.value;
        brightnessValue.textContent = value + '%';  // Update the displayed percentage label
        applyBrightness(value);                      // Instant visual feedback (defined in app.js)
    });

    // 'change' fires only when the slider is released — save the final value
    brightnessSlider.addEventListener('change', async (e) => {
        await updateSettings({ brightness: parseInt(e.target.value) });  // Save as integer
    });

    // ── Font Size ────────────────────────────────────────────────────────────
    document.getElementById('fontSize').addEventListener('change', async (e) => {
        applyFontSize(e.target.value);                         // Instant visual feedback
        await updateSettings({ font_size: e.target.value });   // Persist
    });

    // ── Theme ─────────────────────────────────────────────────────────────────
    document.getElementById('theme').addEventListener('change', async (e) => {
        applyTheme(e.target.value);                            // Instant visual feedback
        await updateSettings({ theme: e.target.value });       // Persist
    });

    // ── Language ─────────────────────────────────────────────────────────────
    // Language preference affects the chat service (translation); no instant DOM change needed
    document.getElementById('language').addEventListener('change', async (e) => {
        await updateSettings({ language: e.target.value });
        showNotification('Language preference saved', 'success');
    });

    // ── Notifications ─────────────────────────────────────────────────────────
    document.getElementById('notificationsEnabled').addEventListener('change', async (e) => {
        await updateSettings({ notifications_enabled: e.target.checked });
    });

    document.getElementById('notificationSound').addEventListener('change', async (e) => {
        await updateSettings({ notification_sound: e.target.checked });
    });

    // Load current settings from the backend and pre-populate all controls
    loadCurrentSettings();
}

/**
 * Fetch current settings from the backend and populate all Settings page controls.
 * Called once when the Settings page initialises.
 * Ensures controls reflect what was last saved, not browser defaults.
 */
async function loadCurrentSettings() {
    try {
        const response = await fetch(`${API_BASE}/settings`);
        const settings = await response.json();

        // Pre-populate each control with the saved value (fall back to defaults if missing)
        document.getElementById('contrastMode').value = settings.contrast_mode || 'normal';
        const brightness = settings.brightness || 100;
        document.getElementById('brightness').value = brightness;
        document.getElementById('brightnessValue').textContent = brightness + '%';  // Update the label too
        document.getElementById('fontSize').value = settings.font_size || 'medium';
        document.getElementById('theme').value = settings.theme || 'light';
        document.getElementById('language').value = settings.language || 'en';
        // Checkboxes: default to checked (true) unless explicitly saved as false
        document.getElementById('notificationsEnabled').checked = settings.notifications_enabled !== false;
        document.getElementById('notificationSound').checked = settings.notification_sound !== false;

    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

/**
 * Send a partial settings update to the backend via PUT /api/settings.
 * Only the fields included in the 'updates' object are changed; all others remain as-is.
 * The backend merges the provided fields with the existing stored settings.
 *
 * @param {Object} updates - Partial settings object (e.g., { theme: 'dark' })
 */
async function updateSettings(updates) {
    try {
        const response = await fetch(`${API_BASE}/settings`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updates)  // Only the changed field(s) are sent
        });

        if (!response.ok) {
            showNotification('Error saving settings', 'error');
        }
    } catch (error) {
        console.error('Error updating settings:', error);
        showNotification('Error saving settings', 'error');
    }
}
