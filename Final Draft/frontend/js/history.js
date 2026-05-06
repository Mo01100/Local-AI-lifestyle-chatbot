/**
 * Conversation History
 *
 * This module manages the History page, which lets users:
 *   - Browse all past conversations with message counts and timestamps
 *   - Open a past conversation in the chat window
 *   - Delete individual conversations
 *   - Filter/search conversations by title using a live search input
 *
 * Note: functions like addMessage() and currentConversationId are defined in chat.js
 * and are available globally because both files are loaded in the same HTML page.
 */

/**
 * Fetch all conversations from the backend and render them in the history list.
 * Called by app.js when the user navigates to the History page.
 * Also called after deleting a conversation to refresh the displayed list.
 */
async function loadConversations() {
    try {
        const response = await fetch(`${API_BASE}/chat/conversations`);
        const conversations = await response.json();

        displayConversations(conversations);  // Render the fetched list
    } catch (error) {
        console.error('Error loading conversations:', error);
        // Show an error message inside the list container rather than failing silently
        document.getElementById('conversationsList').innerHTML =
            '<p>Error loading conversations</p>';
    }
}

/**
 * Render the list of conversations in the History page container.
 * Each row shows: title, message count, last-updated time, and action buttons.
 *
 * @param {Array} conversations - Array of conversation objects from the API
 */
function displayConversations(conversations) {
    const container = document.getElementById('conversationsList');

    // Show an empty-state message if no conversations exist yet
    if (conversations.length === 0) {
        container.innerHTML = '<p>No conversations yet. Start chatting!</p>';
        return;
    }

    // Build one card per conversation using template literals
    container.innerHTML = conversations.map(conv => `
        <div class="conversation-item" data-id="${conv.id}">
            <div class="conversation-header">
                <h3>${conv.title}</h3>
                <!-- Delete button: calls deleteConversation() with this conversation's ID -->
                <button class="btn btn-danger btn-sm" onclick="deleteConversation(${conv.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            <div class="conversation-meta">
                <!-- Message count and last-updated timestamp -->
                <span><i class="fas fa-message"></i> ${conv.message_count} messages</span>
                <span><i class="fas fa-clock"></i> ${formatDate(conv.updated_at)}</span>
            </div>
            <!-- Button to open this conversation in the chat window -->
            <button class="btn btn-secondary btn-sm" onclick="viewConversation(${conv.id})">
                View Conversation
            </button>
        </div>
    `).join('');
}

/**
 * Open a specific conversation in the Chat page.
 * Switches the user to the Chat page and loads all messages for the selected conversation.
 *
 * @param {number} id - The conversation ID to view
 */
async function viewConversation(id) {
    try {
        const response = await fetch(`${API_BASE}/chat/conversations/${id}`);
        const messages = await response.json();

        // Navigate the user to the Chat page by simulating a nav-item click
        document.querySelector('[data-page="chat"]').click();

        // Fill the chat window with this conversation's messages
        const messagesContainer = document.getElementById('messages');
        messagesContainer.innerHTML = '';  // Clear any existing messages

        // Render each message using chat.js's addMessage() function
        messages.forEach(msg => {
            addMessage(msg.content, msg.role);
        });

        // Set the active conversation ID so new replies continue this conversation
        currentConversationId = id;

    } catch (error) {
        console.error('Error viewing conversation:', error);
    }
}

/**
 * Delete a conversation permanently from the backend.
 * Prompts for confirmation before deleting, then refreshes the list.
 *
 * @param {number} id - The conversation ID to delete
 */
async function deleteConversation(id) {
    // Confirm before performing an irreversible action
    if (!confirm('Are you sure you want to delete this conversation?')) return;

    try {
        await fetch(`${API_BASE}/chat/conversations/${id}`, {
            method: 'DELETE'
        });

        // Refresh the conversation list to remove the deleted item
        loadConversations();
        showNotification('Conversation deleted', 'success');
    } catch (error) {
        console.error('Error deleting conversation:', error);
        showNotification('Error deleting conversation', 'error');
    }
}

// ─── Live Search / Filter ─────────────────────────────────────────────────────
// Client-side filtering: hides conversation cards whose titles don't match the search term.
// No API call needed — we filter the already-loaded DOM elements.
document.getElementById('historySearch')?.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();  // Normalise search to lowercase
    const conversations = document.querySelectorAll('.conversation-item');

    conversations.forEach(conv => {
        const title = conv.querySelector('h3').textContent.toLowerCase();
        // Show the card if the title contains the search term; hide it otherwise
        conv.style.display = title.includes(searchTerm) ? 'block' : 'none';
    });
});
