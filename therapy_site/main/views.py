from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import uuid
from main.models import Service, ClientInteraction
from therapy_app.ai_agents import therapy_ai, content_optimizer


def home(request):
    try:
        services = Service.objects.filter(is_active=True)

        # AI-optimized content
        ai_context = {}
        for service in services:
            optimized = content_optimizer.optimize_content(service.service_type)
            ai_context[f'{service.service_type}_optimized'] = optimized

        context = {
            'services': services,
            'ai_enabled': therapy_ai.ai_enabled,
            **ai_context
        }
        return render(request, 'index.html', context)
    except Exception as e:
        # Fallback if services don't exist yet
        context = {
            'services': [],
            'ai_enabled': therapy_ai.ai_enabled,
        }
        return render(request, 'index.html', context)


def about(request):
    context = {
        'ai_enabled': therapy_ai.ai_enabled,
    }
    return render(request, 'about.html', context)


def service_detail(request, service_slug):
    try:
        service = get_object_or_404(Service, slug=service_slug)
        optimized_content = content_optimizer.optimize_content(service.service_type)

        # Fix the template mapping - match service_type to actual template names
        template_map = {
            'conflict_resolution': 'services/conflict_resolution.html',
            'renewing_connections': 'services/renewing_connections.html',
            'relationship_stages': 'services/relationship_stages.html',
            'serenity': 'services/serenity.html',
            'effective_communication': 'services/effective_communication.html',
        }

        template_name = template_map.get(service.service_type, 'services/conflict_resolution.html')

        context = {
            'service': service,
            'optimized_content': optimized_content,
            'ai_suggestions': optimized_content.get('ai_suggestions', []),
            'ai_enabled': therapy_ai.ai_enabled,
        }
        return render(request, template_name, context)
    except Exception as e:
        print(f"Service detail error: {e}")  # Debug output
        return home(request)


@method_decorator(csrf_exempt, name='dispatch')
class AIChatView(View):
    def get(self, request):
        """Handle GET requests - return a simple message"""
        return JsonResponse({'error': 'Please use POST requests for AI chat'}, status=400)

    def post(self, request):
        """Handle POST requests - existing AI chat logic"""
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            session_id = data.get('session_id', str(uuid.uuid4()))

            # Analyze sentiment
            sentiment = therapy_ai.analyze_sentiment(user_message)

            # Generate AI response
            ai_response = therapy_ai.generate_therapy_response(user_message)

            # Store interaction
            ClientInteraction.objects.create(
                session_id=session_id,
                message=user_message,
                sentiment=sentiment,
                ai_response=ai_response
            )

            return JsonResponse({
                'response': ai_response,
                'sentiment': sentiment,
                'session_id': session_id,
                'success': True
            })

        except Exception as e:
            return JsonResponse({
                'response': 'I appreciate you reaching out. Let\'s discuss this further in our session.',
                'success': False
            })


def contact(request):
    context = {
        'ai_enabled': therapy_ai.ai_enabled,
    }
    return render(request, 'contact.html', context)
