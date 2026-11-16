"""Unit and integration tests for service models and public HTTP endpoints."""

import json
from unittest.mock import Mock, patch

import requests
from django.db import IntegrityError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from main.models import ClientInteraction, Service
from therapy_app.ai_agents import ContentOptimizer, TherapyAI


class ServiceModelTests(TestCase):
    """Verify the service catalogue's ordering, representation, and constraints."""

    def test_services_are_ordered_by_configured_position(self):
        """The default ordering should put the lowest position first."""
        later_service = Service.objects.create(
            title="Later service",
            slug="later-service",
            description="A later service.",
            service_type="serenity",
            order=20,
        )
        first_service = Service.objects.create(
            title="First service",
            slug="first-service",
            description="The first service.",
            service_type="conflict_resolution",
            order=1,
        )

        self.assertEqual(list(Service.objects.all()), [first_service, later_service])

    def test_string_representation_is_the_service_title(self):
        service = Service.objects.create(
            title="Clear Communication",
            slug="clear-communication",
            description="Build healthier communication habits.",
            service_type="effective_communication",
        )

        self.assertEqual(str(service), "Clear Communication")

    def test_service_slug_must_be_unique(self):
        Service.objects.create(
            title="Original",
            slug="same-slug",
            description="Original service.",
            service_type="serenity",
        )

        with self.assertRaises(IntegrityError):
            Service.objects.create(
                title="Duplicate",
                slug="same-slug",
                description="Duplicate service.",
                service_type="serenity",
            )


class ClientInteractionModelTests(TestCase):
    """Verify persistence and readable representation of chat interactions."""

    def test_string_representation_identifies_session(self):
        interaction = ClientInteraction.objects.create(
            session_id="session-test-01",
            message="A test message.",
            ai_response="A supportive response.",
        )

        self.assertEqual(str(interaction), "Session session-test-01")


class AIChatViewTests(TestCase):
    """Exercise validation, CSRF protection, persistence, and endpoint failures."""

    def setUp(self):
        self.endpoint = reverse("ai_chat")

    def post_json(self, payload):
        """Submit a JSON object using Django's test HTTP client."""
        payload = {"consent": True, **payload}
        return self.client.post(
            self.endpoint,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_get_is_rejected_and_advertises_post(self):
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response["Allow"], "POST")

    def test_non_json_content_type_is_rejected(self):
        response = self.client.post(
            self.endpoint,
            data="message=hello",
            content_type="text/plain",
        )

        self.assertEqual(response.status_code, 415)
        self.assertFalse(response.json()["success"])

    def test_malformed_json_is_rejected(self):
        response = self.client.post(
            self.endpoint, data="{not-json", content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

    def test_json_array_is_rejected(self):
        response = self.post_json(["not", "an", "object"])

        self.assertEqual(response.status_code, 400)

    @patch("main.views.therapy_ai.generate_therapy_response")
    def test_missing_consent_is_rejected_before_provider_processing(self, mock_generate_response):
        response = self.client.post(
            self.endpoint,
            data=json.dumps({"message": "A message without consent."}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        mock_generate_response.assert_not_called()
        self.assertEqual(ClientInteraction.objects.count(), 0)

    def test_blank_message_is_rejected(self):
        response = self.post_json({"message": "  "})

        self.assertEqual(response.status_code, 400)

    def test_oversized_message_is_rejected(self):
        response = self.post_json({"message": "x" * 2_001})

        self.assertEqual(response.status_code, 413)

    def test_invalid_session_identifier_is_rejected(self):
        response = self.post_json({"message": "Hello", "session_id": "x" * 101})

        self.assertEqual(response.status_code, 400)

    @patch("main.views.therapy_ai.generate_therapy_response")
    @patch("main.views.therapy_ai.analyze_sentiment")
    def test_valid_message_is_processed_without_persisting_by_default(
        self, mock_analyze_sentiment, mock_generate_response
    ):
        mock_analyze_sentiment.return_value = {"label": "NEUTRAL", "score": 0.5}
        mock_generate_response.return_value = "Thank you for sharing."
        response = self.post_json(
            {"message": "  Hello there.  ", "session_id": "session-unit-test"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["session_id"], "session-unit-test")
        self.assertEqual(response.json()["response"], "Thank you for sharing.")
        self.assertFalse(ClientInteraction.objects.filter(session_id="session-unit-test").exists())

    @override_settings(STORE_CHAT_INTERACTIONS=True)
    @patch("main.views.therapy_ai.generate_therapy_response")
    @patch("main.views.therapy_ai.analyze_sentiment")
    def test_valid_message_is_persisted_only_when_explicitly_enabled(
        self, mock_analyze_sentiment, mock_generate_response
    ):
        mock_analyze_sentiment.return_value = {"label": "NEUTRAL", "score": 0.5}
        mock_generate_response.return_value = "Thank you for sharing."

        response = self.post_json(
            {"message": "A message for the opted-in test.", "session_id": "session-retained"}
        )

        self.assertEqual(response.status_code, 200)
        interaction = ClientInteraction.objects.get(session_id="session-retained")
        self.assertEqual(interaction.message, "A message for the opted-in test.")

    @patch("main.views.therapy_ai.generate_therapy_response")
    def test_processing_failure_returns_safe_service_unavailable_response(
        self, mock_generate_response
    ):
        mock_generate_response.side_effect = RuntimeError("simulated provider outage")
        response = self.post_json({"message": "Hello"})

        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json()["success"])
        self.assertEqual(ClientInteraction.objects.count(), 0)

    def test_post_requires_a_csrf_token(self):
        """The API must retain the CSRF middleware's default protection."""
        csrf_enforcing_client = Client(enforce_csrf_checks=True)
        response = csrf_enforcing_client.post(
            self.endpoint,
            data=json.dumps({"message": "Hello"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)


class AIServiceTests(TestCase):
    """Test the AI adapter without a live provider or downloaded ML models."""

    def test_disabled_ai_returns_a_nonempty_supportive_fallback(self):
        with override_settings(OPENAI_API_KEY=None):
            ai_service = TherapyAI(client=None)

        self.assertFalse(ai_service.ai_enabled)
        self.assertIn("listen", ai_service.generate_therapy_response("Hello"))

    @override_settings(AI_PROVIDER="ollama", OLLAMA_BASE_URL="http://localhost:11434", OLLAMA_MODEL="qwen2.5:3b")
    @patch("therapy_app.ai_agents.requests.post")
    def test_ollama_provider_returns_local_model_response(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"message": {"content": "A local response."}}
        mock_post.return_value = mock_response
        ai_service = TherapyAI(client=None)

        response = ai_service.generate_therapy_response("Help me phrase a concern.")

        self.assertEqual(response, "A local response.")
        mock_post.assert_called_once()
        self.assertIn("/api/chat", mock_post.call_args.args[0])
        self.assertEqual(mock_post.call_args.kwargs["json"]["model"], "qwen2.5:3b")

    @override_settings(AI_PROVIDER="ollama", OLLAMA_BASE_URL="http://localhost:11434")
    @patch("therapy_app.ai_agents.requests.post")
    def test_ollama_provider_falls_back_when_local_server_is_unavailable(self, mock_post):
        mock_post.side_effect = requests.ConnectionError("offline")
        ai_service = TherapyAI(client=None)

        response = ai_service.generate_therapy_response("Help me communicate.")

        self.assertIn("courage", response.lower())

    def test_configured_client_response_is_returned(self):
        provider_client = Mock()
        provider_client.chat.completions.create.return_value.choices = [
            Mock(message=Mock(content="A tested response."))
        ]
        ai_service = TherapyAI(client=provider_client)

        result = ai_service.generate_therapy_response("A sample question.")

        self.assertEqual(result, "A tested response.")
        provider_client.chat.completions.create.assert_called_once()

    def test_sentiment_falls_back_when_no_model_is_configured(self):
        ai_service = TherapyAI(client=None, sentiment_analyzer=None)

        self.assertEqual(
            ai_service.analyze_sentiment("A sample message."),
            {"label": "NEUTRAL", "score": 0.5},
        )

    def test_content_optimizer_returns_known_guidance(self):
        guidance = ContentOptimizer.optimize_content("serenity")

        self.assertEqual(guidance["title"], "Finding Relationship Serenity")
        self.assertTrue(guidance["ai_suggestions"])

    def test_content_optimizer_handles_unknown_service_types(self):
        self.assertEqual(ContentOptimizer.optimize_content("unknown-service"), {})


class PublicPageTests(TestCase):
    """Verify the primary public pages render without hidden prerequisites."""

    @override_settings(AI_PROVIDER="ollama", OLLAMA_BASE_URL="http://127.0.0.1:11434")
    def test_chat_discloses_ollama_provider_and_requires_explicit_consent(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Provider:")
        self.assertContains(response, "Ollama")
        self.assertContains(response, 'id="ai-consent"')
        self.assertContains(response, "consent to this processing")
        self.assertContains(response, "Do not include names, contact details")

    @override_settings(AI_PROVIDER="openai", OPENAI_API_KEY="test-only-key")
    def test_chat_discloses_openai_when_that_provider_is_configured(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "OpenAI")
        self.assertContains(response, "OpenAI&#x27;s API")

    def test_homepage_renders_with_empty_service_catalogue(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, "New resources are taking shape.")
        self.assertContains(response, "Skip to content")

    def test_about_and_contact_pages_render(self):
        for page_name in ("about", "contact"):
            with self.subTest(page=page_name):
                response = self.client.get(reverse(page_name))
                self.assertEqual(response.status_code, 200)

    def test_service_detail_renders_the_matching_service_template(self):
        service = Service.objects.create(
            title="Clear Communication",
            slug="clear-communication",
            description="Practice healthier communication habits.",
            service_type="effective_communication",
            is_active=True,
        )

        response = self.client.get(reverse("service_detail", args=[service.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "services/effective_communication.html"
        )
        self.assertContains(response, "Practice Communication Skills")

    def test_missing_service_returns_not_found(self):
        response = self.client.get(
            reverse("service_detail", args=["this-service-does-not-exist"])
        )

        self.assertEqual(response.status_code, 404)
