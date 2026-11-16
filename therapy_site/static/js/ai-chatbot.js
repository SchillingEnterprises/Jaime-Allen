/**
 * Accessible, same-origin chat widget client.
 *
 * The endpoint is configured by the Django template through window.aiConfig.
 * User-provided text is inserted with textContent, never interpreted as HTML.
 */
class AIChatBot {
    constructor() {
        this.isOpen = false;
        this.isSending = false;
        this.sessionId = this.generateSessionId();

        // Cache the required widget elements once rather than querying on every message.
        this.toggleButton = document.getElementById("ai-chat-toggle");
        this.chatWidget = document.getElementById("ai-chat-widget");
        this.closeButton = document.querySelector(".ai-close-btn");
        this.sendButton = document.getElementById("ai-send-btn");
        this.messageInput = document.getElementById("ai-message-input");
        this.messagesContainer = document.querySelector(".ai-chat-messages");

        if (!this.hasRequiredElements()) {
            console.warn("AI chat widget markup is incomplete; chat initialization skipped.");
            return;
        }

        this.bindEvents();
        this.addMessage(
            "ai",
            "Hello! I'm here to provide supportive listening and guidance. How can I help you today?"
        );
    }

    /**
     * Return a unique client-side conversation identifier.
     * This identifier is for conversation grouping, not authentication.
     */
    generateSessionId() {
        if (window.crypto && typeof window.crypto.randomUUID === "function") {
            return `session_${window.crypto.randomUUID()}`;
        }

        const randomSuffix = Math.random().toString(36).slice(2, 12);
        return `session_${Date.now().toString(36)}_${randomSuffix}`;
    }

    /** Check whether this page actually contains the full chat component. */
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

    /** Register event handlers after the markup has been verified. */
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

    /** Open or close the chat panel and move keyboard focus appropriately. */
    toggleChat() {
        this.isOpen = !this.isOpen;
        this.chatWidget.classList.toggle("open", this.isOpen);
        if (this.isOpen) {
            this.messageInput.focus();
        }
    }

    /** Close the chat panel without discarding the current conversation. */
    closeChat() {
        this.isOpen = false;
        this.chatWidget.classList.remove("open");
        this.toggleButton.focus();
    }

    /**
     * Send one validated message to the same-origin Django endpoint.
     * The CSRF cookie is included because the server deliberately enforces CSRF.
     */
    async sendMessage() {
        if (this.isSending) {
            return;
        }

        const message = this.messageInput.value.trim();
        if (!message) {
            this.messageInput.focus();
            return;
        }

        const chatEndpoint = window.aiConfig && window.aiConfig.chatEndpoint;
        if (!chatEndpoint) {
            this.addMessage("ai", "Chat is temporarily unavailable. Please try again later.");
            return;
        }

        this.isSending = true;
        this.sendButton.disabled = true;
        this.addMessage("user", message);
        this.messageInput.value = "";
        this.showTypingIndicator();

        try {
            const response = await fetch(chatEndpoint, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": this.getCSRFToken()
                },
                body: JSON.stringify({
                    message,
                    session_id: this.sessionId
                })
            });

            const responseData = await response.json();
            if (!response.ok || !responseData.success) {
                throw new Error("The chat endpoint returned an unsuccessful response.");
            }

            this.addMessage("ai", responseData.response);
        } catch (error) {
            // Deliberately avoid logging message text or other user-provided content.
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

    /** Append a text-only message node, preventing user text from becoming HTML. */
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

    /** Add a non-interactive typing indicator while the request is in flight. */
    showTypingIndicator() {
        this.hideTypingIndicator();

        const indicator = document.createElement("div");
        indicator.id = "typing-indicator";
        indicator.className = "message ai-message typing";
        indicator.setAttribute("aria-label", "Assistant is typing");

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

    /** Remove an existing typing indicator, if one is present. */
    hideTypingIndicator() {
        this.messagesContainer
            .querySelector("#typing-indicator")
            ?.remove();
    }

    /** Return the readable CSRF token cookie expected by Django's middleware. */
    getCSRFToken() {
        const tokenPrefix = "csrftoken=";
        const csrfCookie = document.cookie
            .split(";")
            .map((cookie) => cookie.trim())
            .find((cookie) => cookie.startsWith(tokenPrefix));

        if (csrfCookie) {
            return decodeURIComponent(csrfCookie.slice(tokenPrefix.length));
        }

        // Support pages that render Django's standard hidden CSRF form field.
        return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
    }

    /** Format the local time for the message metadata label. */
    getCurrentTime() {
        return new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
        });
    }
}

// Initialize only after the DOM is ready and the server enables the chat feature.
document.addEventListener("DOMContentLoaded", () => {
    if (window.aiConfig && window.aiConfig.enabled) {
        window.aiChatBot = new AIChatBot();
    }
});
