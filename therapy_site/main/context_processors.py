from therapy_app.ai_agents import therapy_ai

def ai_settings(request):
    return {
        'ai_enabled': therapy_ai.ai_enabled,
    }
