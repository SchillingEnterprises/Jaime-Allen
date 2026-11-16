"""HTTP views for the public therapy website and its AI-support endpoint."""

import json
import logging
import uuid
from typing import Any, ClassVar

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie

from main.models import ClientInteraction, Service
from therapy_app.ai_agents import content_optimizer, therapy_ai

logger = logging.getLogger(__name__)

# Keep requests bounded to protect the application and downstream AI provider.
MAX_CHAT_MESSAGE_LENGTH = 2_000
MAX_SESSION_ID_LENGTH = 100
FALLBACK_AI_RESPONSE = (
    "Thank you for sharing. I appreciate you reaching out. "
    "Please consider discussing this further with your qualified therapist."
)


@ensure_csrf_cookie
def home(request):
    """Render the home page and make a CSRF cookie available to the chat widget."""
    services = Service.objects.filter(is_active=True)
    optimized_context = {
        f"{service.service_type}_optimized": content_optimizer.optimize_content(
            service.service_type
        )
        for service in services
    }
    context = {
        "services": services,
        "ai_enabled": therapy_ai.ai_enabled,
        **optimized_context,
    }
    return render(request, "index.html", context)


@ensure_csrf_cookie
def about(request):
    """Render the about page and issue a CSRF cookie for same-origin forms."""
    return render(request, "about.html", {"ai_enabled": therapy_ai.ai_enabled})


@ensure_csrf_cookie
def service_detail(request, service_slug):
    """Render the detail page for a service identified by its unique slug."""
    service = get_object_or_404(Service, slug=service_slug)
    optimized_content = content_optimizer.optimize_content(service.service_type)
    template_by_service_type = {
        "conflict_resolution": "services/conflict_resolution.html",
        "renewing_connections": "services/renewing_connections.html",
        "relationship_stages": "services/relationship_stages.html",
        "serenity": "services/serenity.html",
        "effective_communication": "services/effective_communication.html",
    }
    template_name = template_by_service_type.get(
        service.service_type, "services/conflict_resolution.html"
    )
    context = {
        "service": service,
        "optimized_content": optimized_content,
        "ai_suggestions": optimized_content.get("ai_suggestions", []),
        "ai_enabled": therapy_ai.ai_enabled,
    }
    return render(request, template_name, context)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class AIChatView(View):
    """Validate chat requests, call the AI service, and persist successful exchanges."""

    http_method_names: ClassVar[list[str]] = ["get", "post", "head", "options"]

    def get(self, request):
        """Explain the supported method without accepting a state-changing GET."""
        response = JsonResponse(
            {"error": "Use POST with a JSON request body for AI chat."},
            status=405,
        )
        response["Allow"] = "POST"
        return response

    def post(self, request):
        """Validate and process a bounded JSON chat request."""
        if request.content_type != "application/json":
            return JsonResponse(
                {"error": "Content-Type must be application/json.", "success": False},
                status=415,
            )

        try:
            payload: Any = json.loads(request.body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse(
                {"error": "Request body must contain valid JSON.", "success": False},
                status=400,
            )

        if not isinstance(payload, dict):
            return JsonResponse(
                {"error": "JSON request body must be an object.", "success": False},
                status=400,
            )

        if payload.get("consent") is not True:
            return JsonResponse(
                {
                    "error": "Explicit consent is required before sending a message to the configured AI provider.",
                    "success": False,
                },
                status=400,
            )

        raw_message = payload.get("message")
        if not isinstance(raw_message, str) or not raw_message.strip():
            return JsonResponse(
                {"error": "A non-empty message is required.", "success": False},
                status=400,
            )

        user_message = raw_message.strip()
        if len(user_message) > MAX_CHAT_MESSAGE_LENGTH:
            return JsonResponse(
                {
                    "error": f"Message must be {MAX_CHAT_MESSAGE_LENGTH} characters or fewer.",
                    "success": False,
                },
                status=413,
            )

        raw_session_id = payload.get("session_id")
        if raw_session_id is None:
            session_id = str(uuid.uuid4())
        elif (
            not isinstance(raw_session_id, str)
            or not raw_session_id.strip()
            or len(raw_session_id) > MAX_SESSION_ID_LENGTH
        ):
            return JsonResponse(
                {"error": "session_id must be a non-empty string of at most 100 characters.",
                 "success": False},
                status=400,
            )
        else:
            session_id = raw_session_id.strip()

        try:
            sentiment = therapy_ai.analyze_sentiment(user_message)
            ai_response = therapy_ai.generate_therapy_response(user_message)
            if settings.STORE_CHAT_INTERACTIONS:
                ClientInteraction.objects.create(
                    session_id=session_id,
                    message=user_message,
                    sentiment=sentiment,
                    ai_response=ai_response,
                )
        except Exception:
            # Do not log request bodies or provider response data: messages may
            # contain personal information. The client receives a safe fallback.
            logger.exception("AI chat processing failed.")
            return JsonResponse(
                {"response": FALLBACK_AI_RESPONSE, "success": False},
                status=503,
            )

        return JsonResponse(
            {
                "response": ai_response,
                "sentiment": sentiment,
                "session_id": session_id,
                "success": True,
            }
        )


@ensure_csrf_cookie
def contact(request):
    """Render contact details and issue a CSRF cookie for same-origin interactions."""
    return render(request, "contact.html", {"ai_enabled": therapy_ai.ai_enabled})
