/**
 * Chat Functionality
 *
 * This module manages the entire Chat page UI:
 *   - Tracking the active conversation (ID + title)
 *   - Sending user messages to the backend and displaying AI responses
 *   - Loading and displaying past conversations in the sidebar
 *   - Adding TTS "read aloud" buttons to assistant messages
 *   - Rendering Markdown-style formatting (bold, bullet lists, numbered lists)
 *   - Showing/hiding a typing indicator while waiting for the AI response
 */

// ─── Conversation State ────────────────────────────────────────────────────────
// These module-level variables track which conversation is currently open in the chat window.
// null means no conversation is selected (i.e., we'll start a new one on the next message).
let currentConversationId = null;
let currentConversationTitle = "New Conversation";

// ─── Boot Sequence ────────────────────────────────────────────────────────────
// Set up all event listeners once the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initChat();                    // Wire up buttons, keyboard shortcuts, and resize behaviour
    loadConversationsSidebar();    // Populate the left-side conversation list from the backend
});

/**
 * Initialise all interactive elements in the chat page.
 * Wires up:
 *   - Send button click → sendMessage()
 *   - Enter key in textarea → sendMessage() (Shift+Enter inserts a newline instead)
 *   - "New Chat" buttons → startNewChat()
 *   - Sidebar toggle button → show/hide the conversation sidebar
 *   - Textarea auto-resize as the user types
 */
function initChat() {
    const sendBtn = document.getElementById('sendBtn');
    const chatInput = document.getElementById('chatInput');
    const newChatBtn = document.getElementById('newChatBtn');
    const newChatBtnSidebar = document.getElementById('newChatBtnSidebar');
    const toggleSidebarBtn = document.getElementById('toggleConversationSidebar');

    // Primary send action via button click
    sendBtn.addEventListener('click', sendMessage);

    // Keyboard shortcut: Enter sends the message; Shift+Enter adds a newline
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();  // Prevent default newline insertion
            sendMessage();
        }
    });

    // Both "New Chat" buttons (toolbar + sidebar) start a fresh conversation
    newChatBtn.addEventListener('click', startNewChat);
    newChatBtnSidebar?.addEventListener('click', startNewChat);

    // Toggle the conversation history sidebar on/off
    toggleSidebarBtn?.addEventListener('click', () => {
        document.getElementById('conversationSidebar').classList.toggle('active');
    });

    // Auto-resize textarea: resets height then expands to fit content
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = chatInput.scrollHeight + 'px';
    });
}

/**
 * Reset the chat window for a brand new conversation.
 * Called when the user clicks either "New Chat" button.
 * Clears the message thread, resets the conversation state, 
 * and de-selects any highlighted sidebar item.
 */
function startNewChat() {
    currentConversationId = null;               // No active conversation — next message creates one
    currentConversationTitle = "New Conversation";
    document.getElementById('messages').innerHTML = '';        // Clear the message thread
    document.getElementById('chatInput').value = '';           // Clear the input box
    document.getElementById('currentConversationTitle').textContent = currentConversationTitle;

    // Remove active highlight from all sidebar conversation items
    document.querySelectorAll('.conversation-list-item').forEach(item => {
        item.classList.remove('active');
    });
    showNotification('Started new conversation', 'success');
}

/**
 * Fetch all conversations from the backend and render them in the sidebar.
 * Called on page load and after sending/deleting a conversation.
 */
async function loadConversationsSidebar() {
    try {
        const response = await fetch(`${API_BASE}/chat/conversations`);
        const conversations = await response.json();

        displayConversationsSidebar(conversations);  // Render the list
    } catch (error) {
        console.error('Error loading conversations:', error);
    }
}

/**
 * Render the conversation list in the sidebar.
 * Each item shows the conversation title, last-updated date, and a delete button.
 * The currently active conversation is highlighted with the 'active' class.
 *
 * @param {Array} conversations - Array of conversation objects from the API
 */
function displayConversationsSidebar(conversations) {
    const container = document.getElementById('conversationListSidebar');

    // Show a placeholder message if no conversations exist yet
    if (conversations.length === 0) {
        container.innerHTML = '<p style="padding: 1rem; text-align: center; color: var(--text-tertiary);">No conversations yet</p>';
        return;
    }

    // Build an HTML list item for each conversation
    container.innerHTML = conversations.map(conv => `
        <div class="conversation-list-item ${conv.id === currentConversationId ? 'active' : ''}" 
             data-id="${conv.id}" 
             onclick="loadConversationInChat(${conv.id}, '${conv.title.replace(/'/g, "\\'")}')">
            <h4>${conv.title}</h4>
            <div class="meta">
                <span>${formatDateOnly(conv.updated_at)}</span>
                <button class="delete-btn" onclick="event.stopPropagation(); deleteConversationFromSidebar(${conv.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

/**
 * Load a specific conversation's messages into the chat window.
 * Called when the user clicks a conversation in the sidebar.
 *
 * @param {number} id    - The conversation ID to load
 * @param {string} title - The conversation title to display in the header
 */
async function loadConversationInChat(id, title) {
    try {
        const response = await fetch(`${API_BASE}/chat/conversations/${id}`);
        const messages = await response.json();

        // Clear current messages in the chat window
        const messagesContainer = document.getElementById('messages');
        messagesContainer.innerHTML = '';

        // Render each message in order (user and assistant alternating)
        messages.forEach(msg => {
            addMessage(msg.content, msg.role);
        });

        // Update the active conversation state
        currentConversationId = id;
        currentConversationTitle = title;
        document.getElementById('currentConversationTitle').textContent = title;

        // Highlight the selected conversation in the sidebar, deselect others
        document.querySelectorAll('.conversation-list-item').forEach(item => {
            item.classList.remove('active');
            if (parseInt(item.dataset.id) === id) {
                item.classList.add('active');
            }
        });

    } catch (error) {
        console.error('Error loading conversation:', error);
    }
}

/**
 * Delete a conversation from the backend and refresh the sidebar.
 * If the deleted conversation was the active one, starts a new chat.
 * Prompts the user for confirmation before deleting.
 *
 * @param {number} id - The conversation ID to delete
 */
async function deleteConversationFromSidebar(id) {
    if (!confirm('Delete this conversation?')) return;

    try {
        await fetch(`${API_BASE}/chat/conversations/${id}`, {
            method: 'DELETE'
        });

        // If deleted conversation was active, start new chat
        if (id === currentConversationId) {
            startNewChat();
        }

        // Reload sidebar to reflect the deletion
        loadConversationsSidebar();

    } catch (error) {
        console.error('Error deleting conversation:', error);
    }
}

/**
 * Send the user's current input to the backend chat API.
 *
 * Flow:
 *   1. Read and validate the message
 *   2. Display the user's message immediately ('optimistic UI')
 *   3. Show a typing indicator while waiting
 *   4. POST to /api/chat/ with the message, conversation ID, and domain filter
 *   5. Hide the typing indicator and display the assistant's response
 *   6. Refresh the sidebar (in case a new conversation was created or updated)
 */
async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();

    // Do nothing if the input is empty
    if (!message) return;

    // Immediately show the user's message in the chat window
    addMessage(message, 'user');
    chatInput.value = '';
    chatInput.style.height = 'auto';  // Shrink the textarea back to default height

    // Show typing indicator (animated dots) while waiting for the response
    showTypingIndicator();

    try {
        // Read the selected domain filter ('all', 'nutrition', 'exercise', etc.)
        const domain = document.getElementById('domainSelector').value;

        const response = await fetch(`${API_BASE}/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                conversation_id: currentConversationId,    // null = create new conversation
                domain: domain === 'all' ? null : domain   // null = search all domains
            })
        });

        const data = await response.json();

        // Track whether this was a brand-new conversation (to trigger title update)
        const isNewConversation = !currentConversationId;
        currentConversationId = data.conversation_id;  // Store the (possibly new) conversation ID

        // Remove the typing indicator now that we have a response
        hideTypingIndicator();

        // Display the assistant's response
        addMessage(data.message, 'assistant');

        // Reload sidebar to show new/updated conversation
        if (isNewConversation) {
            // For new conversations: reload sidebar then fetch the auto-generated title
            await loadConversationsSidebar();
            const convResponse = await fetch(`${API_BASE}/chat/conversations`);
            const conversations = await convResponse.json();
            const currentConv = conversations.find(c => c.id === currentConversationId);
            if (currentConv) {
                currentConversationTitle = currentConv.title;
                document.getElementById('currentConversationTitle').textContent = currentConv.title;
            }
        } else {
            // For existing conversations: just reload so 'updated_at' order is refreshed
            loadConversationsSidebar();
        }

    } catch (error) {
        hideTypingIndicator();
        // Show a user-friendly error if the server can't be reached
        addMessage('Error: Could not connect to server. Please ensure the backend is running.', 'assistant');
        console.error('Error sending message:', error);
    }
}

/**
 * Create and append a message bubble to the chat window.
 * Assistant messages also get a "read aloud" TTS button (if TTS is available).
 * Scrolls the chat to the bottom after adding each message.
 *
 * @param {string} content - The message text (may contain markdown-style formatting)
 * @param {string} role    - 'user' or 'assistant'
 */
function addMessage(content, role) {
    const messagesContainer = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;  // CSS handles left/right bubble styling

    // Format the message content (handles bold, bullet lists, numbered lists)
    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'message-content';
    contentWrapper.innerHTML = formatMessage(content);
    messageDiv.appendChild(contentWrapper);

    // Add TTS speak button for assistant messages
    if (role === 'assistant') {
        const speakBtn = document.createElement('button');
        speakBtn.className = 'btn-speak';
        speakBtn.title = 'Read aloud';
        speakBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
        // When clicked, call the global TTS manager's speak() method
        speakBtn.addEventListener('click', () => {
            if (window.ttsManager && window.ttsManager.isAvailable) {
                window.ttsManager.speak(content, speakBtn);
            }
        });

        // Hide if TTS not yet confirmed available; ttsManager will show it later
        speakBtn.classList.add('tts-speak-btn');
        messageDiv.appendChild(speakBtn);
    }

    messagesContainer.appendChild(messageDiv);
    // Scroll to the bottom so the newest message is always visible
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Convert plain text (with simple Markdown-style syntax) into HTML.
 * Handles:
 *   - HTML escaping (prevents XSS attacks)
 *   - **bold** and __bold__ → <strong>
 *   - Lines starting with * or - → <ul><li>
 *   - Lines starting with 1. 2. etc. → <ol><li>
 *   - Otherwise: wraps in <p>, empty lines become <br>
 *
 * @param {string} text - Raw message text from the API
 * @returns {string} HTML string safe to set as innerHTML
 */
function formatMessage(text) {
    // Escape HTML to prevent XSS
    let formatted = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Convert markdown-style formatting
    // Bold text: **text** or __text__
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/__(.+?)__/g, '<strong>$1</strong>');

    // Convert bullet points: lines starting with * or -
    const lines = formatted.split('\n');
    let inList = false;         // Tracks whether we're inside an open <ul> or <ol>
    let result = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();

        // Check if line is a bullet point
        if (trimmed.match(/^[\*\-]\s+/)) {
            if (!inList) {
                result.push('<ul>');  // Open a new unordered list
                inList = true;
            }
            const content = trimmed.replace(/^[\*\-]\s+/, '');  // Strip the bullet marker
            result.push(`<li>${content}</li>`);
        } else if (trimmed.match(/^\d+\.\s+/)) {
            // Numbered list item (e.g., "1. something")
            if (!inList) {
                result.push('<ol>');  // Open a new ordered list
                inList = true;
            }
            const content = trimmed.replace(/^\d+\.\s+/, '');  // Strip the number prefix
            result.push(`<li>${content}</li>`);
        } else {
            // End the list if we're no longer on a list item
            if (inList) {
                result.push('</ul>');
                inList = false;
            }
            if (trimmed) {
                result.push(`<p>${line}</p>`);  // Non-empty line → paragraph
            } else {
                result.push('<br>');             // Empty line → line break
            }
        }
    }

    // Close any list that was still open at the end of the text
    if (inList) {
        result.push('</ul>');
    }

    return result.join('');
}

/**
 * Show the animated typing indicator (usually animated dots).
 * Used while waiting for the backend to generate an AI response.
 */
function showTypingIndicator() {
    document.getElementById('typingIndicator').style.display = 'flex';
}

/**
 * Hide the typing indicator.
 * Called once the AI response has been received and displayed.
 */
function hideTypingIndicator() {
    document.getElementById('typingIndicator').style.display = 'none';
}
