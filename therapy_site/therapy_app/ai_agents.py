"""Optional AI integrations and deterministic service-content guidance.

The AI provider is initialized only when an API key is configured. Importing
this module does not download models or make network requests.
"""

import logging
from typing import Any

import requests
from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)

NEUTRAL_SENTIMENT: dict[str, float | str] = {"label": "NEUTRAL", "score": 0.5}
AI_FALLBACK_RESPONSE = (
    "Thank you for sharing. It takes courage to discuss these feelings. "
    "Would you like to explore this further with your therapist?"
)

CONTENT_GUIDANCE: dict[str, dict[str, Any]] = {
    "conflict_resolution": {
        "title": "Conflict Resolution with Empathy",
        "keywords": ["communication", "understanding", "compromise", "boundaries"],
        "ai_suggestions": [
            "Practice active listening without interrupting",
            'Use "I feel" statements instead of "You always" statements',
        ],
    },
    "renewing_connections": {
        "title": "Renewing Emotional Connections",
        "keywords": ["reconnection", "intimacy", "communication", "trust"],
        "ai_suggestions": [
            "Schedule weekly quality time without distractions",
            "Express appreciation for small daily actions",
        ],
    },
    "relationship_stages": {
        "title": "Navigating Relationship Stages",
        "keywords": ["growth", "intimacy", "trust", "communication"],
        "ai_suggestions": [
            "Celebrate relationship milestones together",
            "Maintain individual identities within the relationship",
        ],
    },
    "serenity": {
        "title": "Finding Relationship Serenity",
        "keywords": ["peace", "acceptance", "mindfulness", "balance"],
        "ai_suggestions": [
            "Practice mindfulness meditation together",
            "Focus on what you can control in the relationship",
        ],
    },
    "effective_communication": {
        "title": "Mastering Effective Communication",
        "keywords": [
            "active listening",
            "nonviolent communication",
            "emotional intelligence",
            "relationship skills",
        ],
        "ai_suggestions": [
            "Practice the three-second pause before responding",
            'Use "I feel" statements instead of "You always" statements',
        ],
    },
}


class TherapyAI:
    """Provide optional, non-clinical supportive responses using an AI provider."""

    def __init__(self, client: Any = None, sentiment_analyzer: Any = None) -> None:
        """Accept injectable clients so behavior can be unit-tested without a network."""
        self.client = client
        self.sentiment_analyzer = sentiment_analyzer

        if (
            self.client is None
            and settings.AI_PROVIDER == "openai"
            and settings.OPENAI_API_KEY
        ):
            try:
                self.client = OpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    timeout=45.0,
                    max_retries=0,
                )
            except Exception:
                logger.exception("Could not initialize the configured AI provider.")

    @property
    def ai_enabled(self) -> bool:
        """Return whether an injected or environment-configured provider is available."""
        if self.client is not None:
            return True
        if settings.AI_PROVIDER == "ollama":
            return bool(settings.OLLAMA_BASE_URL)
        return bool(settings.OPENAI_API_KEY)

    def analyze_sentiment(self, message: str) -> dict[str, Any]:
        """Return optional sentiment metadata; fall back safely when unavailable."""
        if self.sentiment_analyzer is None:
            return NEUTRAL_SENTIMENT.copy()

        try:
            analysis = self.sentiment_analyzer(message[:512])
            return analysis[0] if analysis else NEUTRAL_SENTIMENT.copy()
        except Exception:
            logger.exception("Sentiment analysis failed.")
            return NEUTRAL_SENTIMENT.copy()

    def generate_therapy_response(
        self, user_message: str, context: str | None = None
    ) -> str:
        """Generate a brief supportive response without presenting it as clinical care."""
        if not self.ai_enabled:
            return "I'm here to listen. Could you tell me more about how you're feeling?"

        system_instructions = (
            "You are a supportive relationship-communication assistant, not a "
            "licensed clinician. Respond with empathy, avoid diagnosis or treatment "
            "claims, do not provide crisis counseling, and encourage professional "
            "support when appropriate. Keep the response under 150 words."
        )
        user_prompt = (
            f"Client message: {user_message}\n"
            f"Context: {context or 'General relationship communication'}\n"
            "Offer a compassionate, practical, non-judgmental response."
        )

        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": user_prompt},
        ]

        try:
            if settings.AI_PROVIDER == "ollama" and self.client is None:
                provider_response = requests.post(
                    f"{settings.OLLAMA_BASE_URL}/api/chat",
                    json={
                        "model": settings.OLLAMA_MODEL,
                        "messages": messages,
                        "stream": False,
                        "options": {"temperature": 0.5},
                    },
                    timeout=(3, 45),
                )
                provider_response.raise_for_status()
                response_text = provider_response.json().get("message", {}).get("content")
            else:
                completion = self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages,
                    max_completion_tokens=180,
                )
                response_text = completion.choices[0].message.content

            if isinstance(response_text, str) and response_text.strip():
                return response_text.strip()
        except (requests.RequestException, ValueError):
            # Do not write user prompts or provider payloads to application logs.
            logger.exception("Local AI provider request failed.")
        except Exception:
            logger.exception("AI response generation failed.")

        return AI_FALLBACK_RESPONSE


class ContentOptimizer:
    """Return curated, deterministic content suggestions for service pages."""

    @staticmethod
    def optimize_content(content_type: str) -> dict[str, Any]:
        """Return a copy of known guidance, or an empty mapping for unknown types."""
        guidance = CONTENT_GUIDANCE.get(content_type)
        if guidance is None:
            return {}
        return {
            key: value.copy() if isinstance(value, list) else value
            for key, value in guidance.items()
        }


# Keep module-level services lightweight; they do not make requests at import time.
therapy_ai = TherapyAI()
content_optimizer = ContentOptimizer()
