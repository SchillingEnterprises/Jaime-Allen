"""Unit and integration tests for service models and public HTTP endpoints."""

import json
from io import StringIO
from unittest.mock import Mock, patch

import requests
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.db import IntegrityError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from main.models import ClientInteraction, Service
from therapy_app.ai_agents import ContentOptimizer, TherapyAI
from therapy_app.settings import _environment_flag


class EnvironmentFlagTests(TestCase):
    """Security settings must fail closed on malformed boolean values."""

    def test_true_and_false_spellings_are_parsed_explicitly(self):
        for value in ("1", "true", "yes", "on", " TRUE "):
            with self.subTest(value=value), patch("therapy_app.settings.os.getenv", return_value=value):
                self.assertIs(_environment_flag("FLAG"), True)

        for value in ("0", "false", "no", "off", " FALSE "):
            with self.subTest(value=value), patch("therapy_app.settings.os.getenv", return_value=value):
                self.assertIs(_environment_flag("FLAG", default=True), False)

    def test_missing_value_uses_explicit_default(self):
        with patch("therapy_app.settings.os.getenv", return_value=None):
            self.assertIs(_environment_flag("FLAG"), False)
            self.assertIs(_environment_flag("FLAG", default=True), True)

    def test_malformed_value_raises_configuration_error(self):
        for value in ("tru", "disabled", "", "2"):
            with (
                self.subTest(value=value),
                patch("therapy_app.settings.os.getenv", return_value=value),
                self.assertRaises(ImproperlyConfigured),
            ):
                _environment_flag("FLAG")


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


class ServiceInitializationCommandTests(TestCase):
    """Default service setup must be repeatable without replacing edited content."""

    def test_command_preserves_existing_services_and_is_idempotent(self):
        existing_service = Service.objects.create(
            title="Custom communication resource",
            slug="effective-communication",
            description="Custom description maintained by an editor.",
            service_type="effective_communication",
            icon="custom-icon",
            is_active=False,
            order=99,
        )

        call_command("init_services", stdout=StringIO())
        existing_service.refresh_from_db()
        self.assertEqual(existing_service.title, "Custom communication resource")
        self.assertEqual(
            existing_service.description,
            "Custom description maintained by an editor.",
        )
        self.assertEqual(existing_service.icon, "custom-icon")
        self.assertFalse(existing_service.is_active)
        self.assertEqual(existing_service.order, 99)
        self.assertEqual(Service.objects.count(), 5)

        call_command("init_services", stdout=StringIO())
        self.assertEqual(Service.objects.count(), 5)


class ClientInteractionModelTests(TestCase):
    """Verify persistence and readable representation of chat interactions."""

    def test_string_representation_identifies_session(self):
        interaction = ClientInteraction.objects.create(
            session_id="session-test-01",
            message="A test message.",
            ai_response="A supportive response.",
        )

        self.assertEqual(str(interaction), "Session session-test-01")


    def test_about_and_contact_show_current_verified_professional_details(self):
        for page_name in ("about", "contact"):
            with self.subTest(page=page_name):
                response = self.client.get(reverse(page_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "LMFT #164998")
                self.assertContains(response, "Insightful Matters Family Counseling Professionals")
                self.assertContains(response, "https://www.insightfulmatters.com/jaime-allen")
                self.assertNotContains(response, "AMFT #163181")

    def test_site_discloses_prototype_and_no_health_information_boundary(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Prototype only.")
        self.assertContains(response, "or a client portal")
        self.assertContains(response, "Do not submit health information")


class AIChatViewTests(TestCase):
    """Exercise validation, CSRF protection, persistence, and endpoint failures."""

    def setUp(self):
        self.endpoint = reverse("ai_chat")

    def post_json(self, payload):
        """Submit a JSON object using Django's test HTTP client."""
        if isinstance(payload, dict):
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

    def test_oversized_request_body_is_rejected_before_json_parsing(self):
        response = self.client.post(
            self.endpoint,
            data=json.dumps({"message": "Hello", "padding": "x" * 16_384}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 413)
        self.assertFalse(response.json()["success"])

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

    @patch("main.views.therapy_ai.generate_therapy_response")
    @patch("main.views.therapy_ai.analyze_sentiment")
    def test_processing_failure_does_not_log_message_or_exception_text(
        self, mock_analyze_sentiment, mock_generate_response
    ):
        sensitive_marker = "private-message-must-not-appear-in-logs"
        mock_analyze_sentiment.return_value = {"label": "NEUTRAL", "score": 0.5}
        mock_generate_response.side_effect = RuntimeError(sensitive_marker)

        with self.assertLogs("main.views", level="ERROR") as captured:
            response = self.post_json({"message": sensitive_marker})

        self.assertEqual(response.status_code, 503)
        self.assertNotIn(sensitive_marker, "\\n".join(captured.output))
        self.assertIn("RuntimeError", "\\n".join(captured.output))

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

    @override_settings(AI_PROVIDER="openai", OPENAI_API_KEY="test-only-key")
    @patch("therapy_app.ai_agents.OpenAI")
    def test_openai_sdk_client_has_a_bounded_timeout_and_no_automatic_retries(
        self, mock_openai
    ):
        """Keep public AI requests bounded and avoid retrying sensitive prompts."""
        mock_openai.return_value = Mock()
        ai_service = TherapyAI(client=None)

        self.assertTrue(ai_service.ai_enabled)
        self.assertIsNotNone(ai_service.client)
        mock_openai.assert_called_once_with(
            api_key="test-only-key",
            timeout=45.0,
            max_retries=0,
        )

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

    @override_settings(AI_PROVIDER="ollama", OLLAMA_BASE_URL="http://localhost:11434")
    @patch("therapy_app.ai_agents.requests.post")
    def test_provider_failure_does_not_log_prompt_or_exception_text(self, mock_post):
        sensitive_marker = "private-provider-prompt-must-not-appear-in-logs"
        mock_post.side_effect = requests.ConnectionError(sensitive_marker)
        ai_service = TherapyAI(client=None)

        with self.assertLogs("therapy_app.ai_agents", level="ERROR") as captured:
            response = ai_service.generate_therapy_response(sensitive_marker)

        self.assertIn("courage", response.lower())
        log_output = "\\n".join(captured.output)
        self.assertNotIn(sensitive_marker, log_output)
        self.assertIn("ConnectionError", log_output)

    def test_sentiment_failure_does_not_log_message_or_exception_text(self):
        sensitive_marker = "private-sentiment-text-must-not-appear-in-logs"
        analyzer = Mock(side_effect=RuntimeError(sensitive_marker))
        ai_service = TherapyAI(client=None, sentiment_analyzer=analyzer)

        with self.assertLogs("therapy_app.ai_agents", level="ERROR") as captured:
            result = ai_service.analyze_sentiment(sensitive_marker)

        self.assertEqual(result, {"label": "NEUTRAL", "score": 0.5})
        log_output = "\\n".join(captured.output)
        self.assertNotIn(sensitive_marker, log_output)
        self.assertIn("RuntimeError", log_output)

    def test_content_optimizer_returns_known_guidance(self):
        guidance = ContentOptimizer.optimize_content("serenity")

        self.assertEqual(guidance["title"], "Finding Relationship Serenity")
        self.assertTrue(guidance["ai_suggestions"])

    def test_content_optimizer_handles_unknown_service_types(self):
        self.assertEqual(ContentOptimizer.optimize_content("unknown-service"), {})


class PublicPageTests(TestCase):
    """Verify the primary public pages render without hidden prerequisites."""

    def test_admin_branding_uses_existing_assets_and_accurate_scope(self):
        admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jaime Allen Therapy Administration")
        self.assertContains(response, "Educational prototype administration")
        self.assertNotContains(response, "AI-Enhanced Therapy Platform")
        self.assertNotContains(response, "therapy-logo.png")

    def test_external_framework_assets_use_subresource_integrity(self):
        response = self.client.get(reverse("home"))

        for integrity in (
            "sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH",
            "sha384-nRgPTkuX86pH8yjPJUAFuASXQSSl2/bBUiNV47vSYpKFxHJhbcrGnmlYpYJMeD7a",
            "sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz",
        ):
            with self.subTest(integrity=integrity):
                self.assertContains(response, f'integrity="{integrity}"')
        self.assertContains(response, 'crossorigin="anonymous"')

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

    def test_inactive_service_detail_is_not_public(self):
        service = Service.objects.create(
            title="Unpublished resource",
            slug="unpublished-resource",
            description="This resource is not published.",
            service_type="effective_communication",
            is_active=False,
        )

        response = self.client.get(reverse("service_detail", args=[service.slug]))

        self.assertEqual(response.status_code, 404)

    @override_settings(AI_PROVIDER="ollama", OLLAMA_BASE_URL="http://127.0.0.1:11434")
    def test_communication_coach_discloses_provider_and_requires_consent(self):
        service = Service.objects.create(
            title="Clear Communication",
            slug="clear-communication",
            description="Practice healthier communication habits.",
            service_type="effective_communication",
            is_active=True,
        )

        response = self.client.get(reverse("service_detail", args=[service.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Provider:")
        self.assertContains(response, "the Ollama service configured by this site")
        self.assertContains(response, 'id="communication-coach-consent"')
        self.assertContains(response, "consent to this processing")
        self.assertContains(response, "provider's data handling may differ")
        self.assertNotContains(response, "Progress Tracking")
