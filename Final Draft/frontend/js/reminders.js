/**
 * Reminders Management
 *
 * This module manages the Reminders page, which allows users to:
 *   - View all reminders (active and completed) sorted by due date
 *   - Add new reminders via a modal form
 *   - Edit existing reminders (pre-fills the modal with current values)
 *   - Mark reminders as completed (PATCH request updates only the completion flag)
 *   - Delete reminders permanently
 *   - Support recurring reminders (daily, weekly, monthly) via a conditional UI
 *
 * The modal form is shared for both Add and Edit actions; editingReminderId tracks context.
 */

// ─── State ────────────────────────────────────────────────────────────────────
// When null, the modal form is in "Add" mode.
// When set to a numeric ID, the form is in "Edit" mode (PUT request will be used).
let editingReminderId = null;

// Track active timeouts for reminders so we can clear them on refresh
let reminderTimeouts = [];

// ─── Boot Sequence ────────────────────────────────────────────────────────────
// Attach event listeners once the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initReminders();
});

/**
 * Wire up all Reminders page event listeners:
 *   - "Add Reminder" button: clears the form and opens the modal
 *   - "Save" and "Cancel" buttons inside the modal
 *   - Modal close (×) button
 *   - "Recurring" checkbox: shows/hides the recurrence pattern dropdown
 */
function initReminders() {
    const addReminderBtn = document.getElementById('addReminderBtn');
    const saveReminderBtn = document.getElementById('saveReminderBtn');
    const cancelReminderBtn = document.getElementById('cancelReminderBtn');
    const closeReminderModal = document.getElementById('closeReminderModal');
    const reminderRecurring = document.getElementById('reminderRecurring');

    // "Add Reminder" button: reset the form ID to null (create mode), then open modal
    addReminderBtn.addEventListener('click', () => {
        editingReminderId = null;   // Ensure we create, not update
        clearReminderForm();
        showReminderModal();
    });

    saveReminderBtn.addEventListener('click', saveReminder);
    cancelReminderBtn.addEventListener('click', hideReminderModal);
    closeReminderModal.addEventListener('click', hideReminderModal);

    // Show the recurrence pattern dropdown when the "Recurring" checkbox is checked
    reminderRecurring.addEventListener('change', (e) => {
        document.getElementById('recurrenceGroup').style.display =
            e.target.checked ? 'block' : 'none';
    });
}

/**
 * Fetch all reminders from the backend and render them in the reminders list.
 * Called by app.js when the user navigates to the Reminders page,
 * and called again after any create/update/delete operation to refresh the view.
 */
async function loadReminders() {
    try {
        const response = await fetch(`${API_BASE}/reminders/`);
        const reminders = await response.json();

        displayReminders(reminders);  // Render the fetched list
        scheduleReminders(reminders); // Schedule active notifications
    } catch (error) {
        console.error('Error loading reminders:', error);
        // Inline error rather than failing silently
        document.getElementById('remindersList').innerHTML =
            '<p>Error loading reminders</p>';
    }
}

/**
 * Render the list of reminders in the Reminders page container.
 * Each card shows: title + category icon, optional description, due date,
 * recurrence info, category badge, and action buttons (complete, edit, delete).
 * Completed reminders receive a 'completed' CSS class for strikethrough styling.
 *
 * @param {Array} reminders - Array of reminder objects from the API
 */
function displayReminders(reminders) {
    const container = document.getElementById('remindersList');

    // Empty-state message if no reminders exist yet
    if (reminders.length === 0) {
        container.innerHTML = '<p>No reminders yet. Add one to get started!</p>';
        return;
    }

    // Build one card per reminder
    container.innerHTML = reminders.map(reminder => `
        <div class="reminder-item ${reminder.is_completed ? 'completed' : ''}">
            <div class="reminder-header">
                <h3>
                    <!-- Category-specific icon (e.g., utensils for meal, dumbbell for exercise) -->
                    <i class="fas fa-${getCategoryIcon(reminder.category)}"></i>
                    ${reminder.title}
                </h3>
                <div class="reminder-actions">
                    <!-- "Complete" button only shown for incomplete reminders -->
                    ${!reminder.is_completed ? `
                        <button class="btn btn-sm btn-success" onclick="completeReminder(${reminder.id})">
                            <i class="fas fa-check"></i>
                        </button>
                    ` : ''}
                    <!-- Edit and delete are always available -->
                    <button class="btn btn-sm btn-secondary" onclick="editReminder(${reminder.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteReminder(${reminder.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <!-- Optional description text -->
            ${reminder.description ? `<p>${reminder.description}</p>` : ''}
            <div class="reminder-meta">
                <span><i class="fas fa-clock"></i> ${formatDate(reminder.due_datetime)}</span>
                <!-- Recurrence badge only shown for recurring reminders -->
                ${reminder.is_recurring ? `<span><i class="fas fa-repeat"></i> ${reminder.recurrence_pattern}</span>` : ''}
                <span class="badge badge-${reminder.category}">${reminder.category}</span>
            </div>
        </div>
    `).join('');
}

/**
 * Map a reminder category string to a Font Awesome icon name.
 * Used to show contextual icons in each reminder card's header.
 *
 * @param {string} category - 'meal', 'exercise', 'medication', or 'custom'
 * @returns {string} Font Awesome icon name (without the 'fa-' prefix)
 */
function getCategoryIcon(category) {
    const icons = {
        meal: 'utensils',
        exercise: 'dumbbell',
        medication: 'pills',
        custom: 'bell'
    };
    return icons[category] || 'bell';  // Default to bell if category is unknown
}

/**
 * Show the reminder modal dialog by adding the 'active' CSS class.
 * The modal must already exist in index.html with id="reminderModal".
 */
function showReminderModal() {
    document.getElementById('reminderModal').classList.add('active');
}

/**
 * Hide the reminder modal by removing the 'active' CSS class.
 */
function hideReminderModal() {
    document.getElementById('reminderModal').classList.remove('active');
}

/**
 * Reset all form fields in the reminder modal to their default empty/unchecked state.
 * Called before opening the modal in "Add" mode to ensure no stale values remain.
 */
function clearReminderForm() {
    document.getElementById('reminderTitle').value = '';
    document.getElementById('reminderDescription').value = '';
    document.getElementById('reminderCategory').value = 'custom';  // Default category
    document.getElementById('reminderDateTime').value = '';
    document.getElementById('reminderRecurring').checked = false;
    document.getElementById('recurrenceGroup').style.display = 'none';  // Hide recurrence dropdown
    document.getElementById('reminderModalTitle').textContent = 'Add Reminder';  // Reset modal title
}

/**
 * Save the reminder from the modal form.
 * Validates required fields, then either creates (POST) or updates (PUT) the reminder.
 * Uses editingReminderId to determine create vs. update mode:
 *   - null → POST to /api/reminders/ (create)
 *   - number → PUT to /api/reminders/{id} (update)
 * After saving, closes the modal and refreshes the reminders list.
 */
async function saveReminder() {
    // Collect form values
    const title = document.getElementById('reminderTitle').value;
    const description = document.getElementById('reminderDescription').value;
    const category = document.getElementById('reminderCategory').value;
    const dueDateTime = document.getElementById('reminderDateTime').value;
    const isRecurring = document.getElementById('reminderRecurring').checked;
    // Only read the recurrence pattern if the recurring checkbox is checked
    const recurrencePattern = isRecurring ? document.getElementById('recurrencePattern').value : null;

    // Validate required fields before making the API call
    if (!title || !dueDateTime) {
        showNotification('Please fill in required fields', 'error');
        return;
    }

    const reminderData = {
        title,
        description,
        category,
        due_datetime: dueDateTime,          // ISO datetime string from the datetime-local input
        is_recurring: isRecurring,
        recurrence_pattern: recurrencePattern
    };

    try {
        // Build URL and method based on whether we're editing or creating
        const url = editingReminderId
            ? `${API_BASE}/reminders/${editingReminderId}`  // Update existing
            : `${API_BASE}/reminders/`;                      // Create new

        const method = editingReminderId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(reminderData)
        });

        if (response.ok) {
            hideReminderModal();           // Close the modal on success
            loadReminders();              // Refresh the displayed list
            showNotification('Reminder saved successfully!', 'success');
        } else {
            showNotification('Error saving reminder', 'error');
        }
    } catch (error) {
        console.error('Error saving reminder:', error);
        showNotification('Error saving reminder', 'error');
    }
}

/**
 * Open the modal in "Edit" mode, pre-populated with the reminder's current values.
 * Fetches all reminders from the backend to find the one matching the given ID,
 * then fills in all form fields before showing the modal.
 *
 * @param {number} id - The ID of the reminder to edit
 */
async function editReminder(id) {
    try {
        // Fetch the full reminders list (no single-reminder endpoint exists) and find by ID
        const response = await fetch(`${API_BASE}/reminders/`);
        const reminders = await response.json();
        const reminder = reminders.find(r => r.id === id);

        if (reminder) {
            editingReminderId = id;  // Switch to update mode

            // Pre-fill all form fields with the reminder's current values
            document.getElementById('reminderTitle').value = reminder.title;
            document.getElementById('reminderDescription').value = reminder.description || '';
            document.getElementById('reminderCategory').value = reminder.category;
            // Slice off the seconds from the ISO datetime to match input[type=datetime-local] format
            document.getElementById('reminderDateTime').value = reminder.due_datetime.slice(0, 16);
            document.getElementById('reminderRecurring').checked = reminder.is_recurring;
            if (reminder.is_recurring) {
                document.getElementById('recurrencePattern').value = reminder.recurrence_pattern;
                document.getElementById('recurrenceGroup').style.display = 'block';
            }
            document.getElementById('reminderModalTitle').textContent = 'Edit Reminder';
            showReminderModal();
        }
    } catch (error) {
        console.error('Error loading reminder:', error);
    }
}

/**
 * Mark a reminder as completed by sending a PATCH request to the backend.
 * Only the is_completed field changes; all other reminder fields remain untouched.
 * Refreshes the list after marking complete.
 *
 * @param {number} id - The ID of the reminder to mark as complete
 */
async function completeReminder(id) {
    try {
        await fetch(`${API_BASE}/reminders/${id}/complete`, {
            method: 'PATCH'  // PATCH = partial update (only is_completed changes)
        });

        loadReminders();  // Refresh the list so the card moves to "completed" state
        showNotification('Reminder completed!', 'success');
    } catch (error) {
        console.error('Error completing reminder:', error);
        showNotification('Error completing reminder', 'error');
    }
}

/**
 * Permanently delete a reminder from the backend.
 * Prompts for confirmation before deleting, then refreshes the list.
 *
 * @param {number} id - The ID of the reminder to delete
 */
async function deleteReminder(id) {
    if (!confirm('Are you sure you want to delete this reminder?')) return;

    try {
        await fetch(`${API_BASE}/reminders/${id}`, {
            method: 'DELETE'
        });

        loadReminders();  // Refresh the list after deletion
        showNotification('Reminder deleted', 'success');
    } catch (error) {
        console.error('Error deleting reminder:', error);
        showNotification('Error deleting reminder', 'error');
    }
}

/**
 * Schedule active reminders to trigger a notification when their time is due.
 * 
 * @param {Array} reminders - Full list of reminders
 */
function scheduleReminders(reminders) {
    // Clear any existing scheduled timeouts
    reminderTimeouts.forEach(clearTimeout);
    reminderTimeouts = [];

    const now = new Date().getTime();

    reminders.forEach(reminder => {
        // Skip completed reminders
        if (reminder.is_completed) return;

        const dueTime = new Date(reminder.due_datetime).getTime();
        const timeUntilDue = dueTime - now;

        // Only schedule if it's in the future and less than 24 hours away
        // (to avoid excessively large timeout values)
        if (timeUntilDue > 0 && timeUntilDue < 24 * 60 * 60 * 1000) {
            const timeoutId = setTimeout(() => {
                triggerReminderNotification(reminder);
            }, timeUntilDue);
            reminderTimeouts.push(timeoutId);
        }
    });
}

/**
 * Trigger the visual and audio notification for a due reminder.
 * Checks the user's settings before notifying.
 * 
 * @param {Object} reminder - The reminder object that is due
 */
function triggerReminderNotification(reminder) {
    // Read current settings state directly from the DOM 
    const notificationsEnabled = document.getElementById('notificationsEnabled')?.checked;
    const soundEnabled = document.getElementById('notificationSound')?.checked;

    if (notificationsEnabled) {
        // Use HTML5 Notification API if permission is granted
        if (Notification.permission === 'granted') {
            new Notification('Reminder: ' + reminder.title, {
                body: reminder.description || 'It is time for your reminder!'
            });
        } else {
            // Fallback to basic notification
            showNotification(`Reminder: ${reminder.title}`, 'info');
        }
        
        if (soundEnabled) {
            playNotificationSound();
        }
    }
}

/**
 * Generate a short, pleasant beep using the Web Audio API.
 * This avoids needing an external mp3 file.
 */
function playNotificationSound() {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(440, audioCtx.currentTime); // A4
        oscillator.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.1); 
        
        gainNode.gain.setValueAtTime(1, audioCtx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);
        
        oscillator.start(audioCtx.currentTime);
        oscillator.stop(audioCtx.currentTime + 0.5);
    } catch (e) {
        console.warn('Audio play failed', e);
    }
}
