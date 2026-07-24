class AIChatBot {
    constructor() {
        this.isOpen = false;
        this.sessionId = this.generateSessionId();
        this.init();
    }

    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }

    init() {
        this.toggleBtn = document.getElementById('ai-chat-toggle');
        this.chatWidget = document.getElementById('ai-chat-widget');
        this.closeBtn = document.querySelector('.ai-close-btn');
        this.sendBtn = document.getElementById('ai-send-btn');
        this.messageInput = document.getElementById('ai-message-input');
        this.messagesContainer = document.querySelector('.ai-chat-messages');

        this.bindEvents();

        // Add welcome message
        this.addMessage('ai', 'Hello! I\'m here to provide supportive listening and guidance. How can I help you today?');
    }

    bindEvents() {
        this.toggleBtn.addEventListener('click', () => this.toggleChat());
        this.closeBtn.addEventListener('click', () => this.closeChat());
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        this.chatWidget.classList.toggle('open', this.isOpen);

        if (this.isOpen) {
            this.messageInput.focus();
        }
    }

    closeChat() {
        this.isOpen = false;
        this.chatWidget.classList.remove('open');
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        this.addMessage('user', message);
        this.messageInput.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch(window.aiConfig.chatEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });

            const data = await response.json();
            this.hideTypingIndicator();

            if (data.success) {
                this.addMessage('ai', data.response);
            } else {
                this.addMessage('ai', 'I appreciate you sharing. Let\'s discuss this further in our session.');
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('ai', 'Thank you for your message. I\'m here to listen and support you.');
        }
    }

    addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.innerHTML = `
            <div class="message-bubble">
                <div class="message-text">${this.escapeHtml(text)}</div>
                <div class="message-time">${this.getCurrentTime()}</div>
            </div>
        `;

        this.messagesContainer.appendChild(messageDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'message ai-message typing';
        typingDiv.innerHTML = `
            <div class="message-bubble">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        this.messagesContainer.appendChild(typingDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getCurrentTime() {
        return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (window.aiConfig.enabled) {
        new AIChatBot();
    }
});