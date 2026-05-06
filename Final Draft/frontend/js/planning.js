/**
 * Daily Planning
 *
 * This module manages the Planning page, which allows users to:
 *   - View and edit their daily meal plan (breakfast, lunch, dinner, snacks)
 *   - Log exercise and set wellness goals for a specific date
 *   - Navigate to any date using a date picker to see or update that date's plan
 *   - Save changes, which creates a new plan or overwrites the existing one (backend upsert)
 *
 * On page load, the date picker defaults to today and loads today's plan automatically.
 * Changing the date immediately loads the plan for that date (or clears the form if none exists).
 */

// ─── Boot Sequence ────────────────────────────────────────────────────────────
// Initialise event listeners once the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initPlanning();
});

/**
 * Set up the Planning page event listeners:
 *   - Set today's date as the default in the date picker
 *   - Reload plan data whenever the date picker changes
 *   - Save the plan when the "Save Plan" button is clicked
 */
function initPlanning() {
    const planDate = document.getElementById('planDate');
    const savePlanBtn = document.getElementById('savePlanBtn');

    // Default the date picker to today's date (ISO format YYYY-MM-DD)
    planDate.value = new Date().toISOString().split('T')[0];

    // Load the plan any time the user picks a different date
    planDate.addEventListener('change', loadPlanByDate);

    // Wire the Save button to the save function
    savePlanBtn.addEventListener('click', savePlan);
}

/**
 * Load today's plan and set the date picker to today.
 * Called by app.js when the user navigates to the Planning page.
 */
async function loadTodayPlan() {
    const today = new Date().toISOString().split('T')[0];  // e.g., "2024-03-15"
    document.getElementById('planDate').value = today;
    await loadPlanByDate();  // Fetch and populate the form with today's plan
}

/**
 * Load the plan for the currently selected date from the backend.
 * Populates all form fields if a plan exists, or clears them if not.
 * Called whenever the date picker value changes or on initial load.
 */
async function loadPlanByDate() {
    const date = document.getElementById('planDate').value;  // YYYY-MM-DD string

    try {
        const response = await fetch(`${API_BASE}/planning/${date}`);

        if (response.ok) {
            const plan = await response.json();

            if (plan) {
                // A plan exists for this date — populate each form field
                document.getElementById('breakfast').value = plan.breakfast || '';
                document.getElementById('lunch').value = plan.lunch || '';
                document.getElementById('dinner').value = plan.dinner || '';
                document.getElementById('snacks').value = plan.snacks || '';
                document.getElementById('exercise').value = plan.exercise || '';
                document.getElementById('wellnessGoals').value = plan.wellness_goals || '';
                document.getElementById('notes').value = plan.notes || '';
            } else {
                // Backend returned null — no plan for this date, clear the form
                clearPlanForm();
            }
        } else {
            // Non-200 response (e.g., 404) — clear the form
            clearPlanForm();
        }
    } catch (error) {
        console.error('Error loading plan:', error);
        clearPlanForm();  // Clear on error so the user doesn't see stale data
    }
}

/**
 * Reset all plan form fields to empty strings.
 * Called when switching to a date that has no saved plan.
 */
function clearPlanForm() {
    document.getElementById('breakfast').value = '';
    document.getElementById('lunch').value = '';
    document.getElementById('dinner').value = '';
    document.getElementById('snacks').value = '';
    document.getElementById('exercise').value = '';
    document.getElementById('wellnessGoals').value = '';
    document.getElementById('notes').value = '';
}

/**
 * Save (create or update) the daily plan for the currently selected date.
 * Reads all form fields, builds a plan object, and POSTs it to the backend.
 * The backend handles the upsert: it creates a new record if none exists for this date,
 * or updates the existing record if one does.
 */
async function savePlan() {
    const date = document.getElementById('planDate').value;  // The date to save for

    // Collect all form field values into a plan object
    const planData = {
        date: date,
        breakfast: document.getElementById('breakfast').value,
        lunch: document.getElementById('lunch').value,
        dinner: document.getElementById('dinner').value,
        snacks: document.getElementById('snacks').value,
        exercise: document.getElementById('exercise').value,
        wellness_goals: document.getElementById('wellnessGoals').value,
        notes: document.getElementById('notes').value
    };

    try {
        const response = await fetch(`${API_BASE}/planning/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(planData)
        });

        if (response.ok) {
            showNotification('Plan saved successfully!', 'success');
        } else {
            showNotification('Error saving plan', 'error');
        }
    } catch (error) {
        console.error('Error saving plan:', error);
        showNotification('Error saving plan', 'error');
    }
}
