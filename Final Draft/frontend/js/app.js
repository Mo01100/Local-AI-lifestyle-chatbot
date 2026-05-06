/**
 * Main Application JavaScript
 * Entry point for the AI Lifestyle Chatbot frontend.
 *
 * Responsibilities:
 *   - Initialising the sidebar navigation (clicking nav items switches pages)
 *   - Loading user settings from the backend on page load and applying them to the DOM
 *   - Providing global utility functions (notifications, date formatting) used by all other JS modules
 *
 * This file is loaded first in index.html so its functions are available to all other scripts.
 */

// Base URL for all API calls — all fetch() requests in all JS files use this constant
const API_BASE = 'http://localhost:8000/api';

// ─── Boot Sequence ────────────────────────────────────────────────────────────
// Wait for the DOM to be fully parsed before attaching event listeners
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();  // Set up sidebar nav click handling
    loadSettings();    // Fetch and apply persisted user settings from the backend
});

/**
 * Initialise the sidebar navigation.
 *
 * Clicking a nav item:
 *   1. Marks that nav item as 'active' (highlights it)
 *   2. Shows the corresponding page panel (hides all others)
 *   3. Triggers any data loading needed for that page (e.g., fetching reminders)
 *
 * Also wires up the mobile sidebar toggle button.
 */
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');  // All clickable nav links
    const pages = document.querySelectorAll('.page');          // All page panels (only one shown at a time)

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const pageName = item.dataset.page;  // 'chat', 'history', 'planning', etc.

            // Update active nav item — remove 'active' from all, add to clicked one
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Update active page — hide all pages, show the selected one
            pages.forEach(page => page.classList.remove('active'));
            document.getElementById(`${pageName}Page`).classList.add('active');

            // Trigger any page-specific data loading (e.g., fetch reminders list)
            loadPageData(pageName);
        });
    });

    // Mobile: toggle sidebar visibility with the hamburger button
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');

    sidebarToggle?.addEventListener('click', () => {
        sidebar.classList.toggle('active');  // 'active' class slides the sidebar into view
    });
}

/**
 * Called when the user clicks a nav item.
 * Triggers the appropriate data fetch for each page type.
 * Chat and About don't need extra fetching; other pages load their data here.
 *
 * @param {string} pageName - The page identifier (matches data-page attribute)
 */
function loadPageData(pageName) {
    switch (pageName) {
        case 'chat':
            // Chat is always loaded
            break;
        case 'history':
            loadConversations();   // Defined in history.js — fetches all past conversations
            break;
        case 'planning':
            loadTodayPlan();       // Defined in planning.js — fetches today's daily plan
            break;
        case 'reminders':
            loadReminders();       // Defined in reminders.js — fetches all reminders
            break;
        case 'settings':
            // Settings loaded on init
            break;
        case 'about':
            // Static page
            break;
    }
}

/**
 * Fetch user settings from the backend and apply them to the page.
 * Called once when the app first loads so the UI reflects saved preferences.
 * Each setting is applied by calling the corresponding apply* function below.
 */
async function loadSettings() {
    try {
        const response = await fetch(`${API_BASE}/settings`);
        const settings = await response.json();

        // Apply each setting to the DOM
        applyTheme(settings.theme);
        applyContrast(settings.contrast_mode);
        applyBrightness(settings.brightness);
        applyFontSize(settings.font_size);

    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// ─── Settings Application Functions ─────────────────────────────────────────
// These functions update data attributes / inline styles on <body>.
// CSS rules in main.css then respond to these attributes to visually change the UI.

/** Set the active theme by writing it as a data attribute on <body>.
 *  CSS selectors like body[data-theme="dark"] then activate the dark-mode palette.
 */
function applyTheme(theme) {
    document.body.dataset.theme = theme;
}

/** Set the contrast level (accessibility feature).
 *  Values: 'normal', 'high', 'low'
 */
function applyContrast(mode) {
    document.body.dataset.contrast = mode;
}

/** Apply brightness as a CSS filter directly on <body>.
 *  value is an integer percentage (e.g., 80 means 80% brightness).
 */
function applyBrightness(value) {
    document.body.style.filter = `brightness(${value}%)`;
}

/** Set the font-size level (accessibility feature).
 *  CSS rules change the root font size based on data-font-size: 'small', 'medium', 'large'
 */
function applyFontSize(size) {
    document.body.dataset.fontSize = size;
}

// ─── Global Utility Functions ─────────────────────────────────────────────────
// These are used by multiple other JS modules (chat.js, reminders.js, history.js, etc.)

/**
 * Show a simple notification to the user.
 * Currently uses a browser alert; can be swapped for a toast library.
 *
 * @param {string} message - The notification message to display
 * @param {string} type    - 'info', 'success', or 'error' (currently unused but reserved)
 */
function showNotification(message, type = 'info') {
    // Simple notification (can be enhanced with a library)
    alert(message);
}

/**
 * Format an ISO 8601 datetime string into a human-readable local date AND time.
 * Example: "2024-03-15T10:30:00" → "3/15/2024, 10:30:00 AM"
 *
 * @param {string} dateString - ISO 8601 datetime string from the API
 * @returns {string} Localised date+time string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

/**
 * Format an ISO 8601 datetime string into a local date only (no time).
 * Example: "2024-03-15T10:30:00" → "3/15/2024"
 *
 * @param {string} dateString - ISO 8601 datetime string from the API
 * @returns {string} Localised date string
 */
function formatDateOnly(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}
