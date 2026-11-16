/**
 * Accessible, same-origin support-chat widget.
 *
 * The feature is enabled only when configured on the server. User input and
 * provider output are rendered as text, never inserted as HTML.
 */
class AIChatBot {
    constructor() {
        this.isOpen = false;
        this.isSending = false;
        this.sessionId = this.generateSessionId();

        // Cache the widget elements once; avoid repeated document-wide lookups.
        this.toggleButton = document.getElementById("ai-chat-toggle");
        this.chatWidget = document.getElementById("ai-chat-widget");
        this.closeButton = document.querySelector(".ai-close-btn");
        this.sendButton = document.getElementById("ai-send-btn");
        this.messageInput = document.getElementById("ai-message-input");
        this.messagesContainer = document.querySelector(".ai-chat-messages");

        if (!this.hasRequiredElements()) {
            console.warn("Support chat markup is incomplete; widget initialization skipped.");
            return;
        }

        this.bindEvents();
        this.addMessage(
            "ai",
            "Hello. I can offer general, supportive communication prompts. What would be helpful to think through today?"
        );
    }

    /** Generate a non-secret conversation grouping identifier. */
    generateSessionId() {
        if (window.crypto && typeof window.crypto.randomUUID === "function") {
            return `session_${window.crypto.randomUUID()}`;
        }
        return `session_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 12)}`;
    }

    /** Confirm the expected markup exists before binding browser events. */
    hasRequiredElements() {
        return Boolean(
            this.toggleButton &&
            this.chatWidget &&
            this.closeButton &&
            this.sendButton &&
            this.messageInput &&
            this.messagesContainer
        );
    }

    /** Bind mouse, touch, and keyboard interactions. */
    bindEvents() {
        this.toggleButton.addEventListener("click", () => this.toggleChat());
        this.closeButton.addEventListener("click", () => this.closeChat());
        this.sendButton.addEventListener("click", () => this.sendMessage());

        this.messageInput.addEventListener("keydown", (event) => {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                this.sendMessage();
            }
        });
    }

    /** Open or close the panel and keep its accessibility state in sync. */
    toggleChat() {
        this.isOpen = !this.isOpen;
        this.chatWidget.hidden = !this.isOpen;
        this.toggleButton.setAttribute("aria-expanded", String(this.isOpen));

        if (this.isOpen) {
            this.messageInput.focus();
        } else {
            this.toggleButton.focus();
        }
    }

    /** Close the panel and return keyboard focus to the launcher button. */
    closeChat() {
        this.isOpen = false;
        this.chatWidget.hidden = true;
        this.toggleButton.setAttribute("aria-expanded", "false");
        this.toggleButton.focus();
    }

    /** Send a bounded message to Django using same-origin credentials and CSRF. */
    async sendMessage() {
        if (this.isSending) {
            return;
        }

        const message = this.messageInput.value.trim();
        if (!message) {
            this.messageInput.focus();
            return;
        }

        if (message.length > 2_000) {
            this.addMessage("ai", "Please keep your message to 2,000 characters or fewer.");
            return;
        }

        const endpoint = window.aiConfig && window.aiConfig.chatEndpoint;
        if (!endpoint) {
            this.addMessage("ai", "Chat is not available right now. Please contact the practice directly.");
            return;
        }

        this.isSending = true;
        this.sendButton.disabled = true;
        this.addMessage("user", message);
        this.messageInput.value = "";
        this.showTypingIndicator();

        try {
            const response = await fetch(endpoint, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": this.getCSRFToken()
                },
                body: JSON.stringify({ message, session_id: this.sessionId })
            });

            const result = await response.json();
            if (!response.ok || !result.success || typeof result.response !== "string") {
                throw new Error("The support chat request was unsuccessful.");
            }

            this.addMessage("ai", result.response);
        } catch (_error) {
            // Deliberately avoid logging the message or other personal information.
            this.addMessage(
                "ai",
                "I couldn't process that message just now. Please try again or contact the practice directly."
            );
        } finally {
            this.hideTypingIndicator();
            this.isSending = false;
            this.sendButton.disabled = false;
            this.messageInput.focus();
        }
    }

    /** Create a text-only message element. */
    addMessage(sender, messageText) {
        const messageElement = document.createElement("div");
        messageElement.className = `message ${sender}-message`;

        const bubbleElement = document.createElement("div");
        bubbleElement.className = "message-bubble";

        const textElement = document.createElement("div");
        textElement.className = "message-text";
        textElement.textContent = messageText;

        const timeElement = document.createElement("div");
        timeElement.className = "message-time";
        timeElement.textContent = this.getCurrentTime();

        bubbleElement.append(textElement, timeElement);
        messageElement.appendChild(bubbleElement);
        this.messagesContainer.appendChild(messageElement);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    /** Show a typing state without injecting an HTML string. */
    showTypingIndicator() {
        this.hideTypingIndicator();

        const indicator = document.createElement("div");
        indicator.id = "typing-indicator";
        indicator.className = "message ai-message typing";
        indicator.setAttribute("aria-label", "Assistant is responding");

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";
        const dots = document.createElement("div");
        dots.className = "typing-dots";

        for (let dotIndex = 0; dotIndex < 3; dotIndex += 1) {
            dots.appendChild(document.createElement("span"));
        }

        bubble.appendChild(dots);
        indicator.appendChild(bubble);
        this.messagesContainer.appendChild(indicator);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    /** Remove the current typing state, if present. */
    hideTypingIndicator() {
        this.messagesContainer.querySelector("#typing-indicator")?.remove();
    }

    /** Read Django's CSRF cookie or the standard hidden input fallback. */
    getCSRFToken() {
        const prefix = "csrftoken=";
        const csrfCookie = document.cookie
            .split(";")
            .map((cookie) => cookie.trim())
            .find((cookie) => cookie.startsWith(prefix));

        if (csrfCookie) {
            return decodeURIComponent(csrfCookie.slice(prefix.length));
        }
        return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
    }

    /** Format a local-time label for a message. */
    getCurrentTime() {
        return new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
        });
    }
}

/** Initialize only when the server-rendered page explicitly enables the feature. */
document.addEventListener("DOMContentLoaded", () => {
    if (window.aiConfig && window.aiConfig.enabled) {
        window.aiChatBot = new AIChatBot();
    }
});
