from django.conf import settings

from therapy_app.ai_agents import therapy_ai


def ai_settings(request):
    """Expose an accurate provider name without implying the provider is local."""
    provider = settings.AI_PROVIDER
    provider_labels = {
        "ollama": ("Ollama", "the Ollama service configured by this site"),
        "openai": ("OpenAI", "OpenAI's API"),
    }
    provider_label, provider_destination = provider_labels.get(
        provider, ("configured AI provider", "the AI service configured by this site")
    )
    return {
        "ai_enabled": therapy_ai.ai_enabled,
        "ai_provider_label": provider_label,
        "ai_provider_destination": provider_destination,
    }
