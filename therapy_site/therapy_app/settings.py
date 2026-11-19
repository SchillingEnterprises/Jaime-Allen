"""Runtime settings for the Jaime Allen Therapy Django application.

Secrets and deployment-specific values are read from environment variables.
A local `.env` file is supported for development and must never be committed.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _environment_flag(name: str, default: bool = False) -> bool:
    """Parse explicit booleans and reject misspelled security configuration."""
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ImproperlyConfigured(f"{name} must be a boolean value.")


# DEBUG is intentionally off by default; enable it explicitly for local work.
DEBUG = _environment_flag("DEBUG", default=False)

# Production must supply a strong secret. Local development gets an ephemeral
# key only when DEBUG is explicitly enabled; it changes whenever the process
# restarts, so it must never be used for a persistent deployment.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured(
            "Set SECRET_KEY in the environment before starting with DEBUG=False."
        )
    SECRET_KEY = get_random_secret_key()

# Comma-separated hostnames supplied by the deployment environment.
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "").split(",")
    if host.strip()
]
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

# Reject oversized request bodies before Django buffers/parses them.
DATA_UPLOAD_MAX_MEMORY_SIZE = 16_384

# Application components.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "main",
    "crispy_forms",
    "crispy_bootstrap5",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "therapy_app.urls"
WSGI_APPLICATION = "therapy_app.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "main.context_processors.ai_settings",
            ],
        },
    },
]

# SQLite is retained to preserve the existing local-development data model.
# Configure a managed production database before deploying a multi-worker app.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CRISPY_ALLOWED_TEMPLATE_PACKS = ["bootstrap5"]
CRISPY_TEMPLATE_PACK = "bootstrap5"

# AI provider configuration. Ollama can run local open-weight models without
# a per-request API fee. OpenAI remains an explicit optional provider choice.
AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama").strip().lower()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if AI_PROVIDER not in {"ollama", "openai"}:
    raise ImproperlyConfigured("AI_PROVIDER must be either 'ollama' or 'openai'.")

if AI_PROVIDER == "openai" and not OPENAI_API_KEY:
    raise ImproperlyConfigured("Set OPENAI_API_KEY when AI_PROVIDER=openai.")

AI_ENABLED = (
    bool(OLLAMA_BASE_URL) if AI_PROVIDER == "ollama" else bool(OPENAI_API_KEY)
)

# Conversation messages can contain sensitive personal information. Storage is
# disabled unless the deployment has an explicit retention and access policy.
STORE_CHAT_INTERACTIONS = _environment_flag("STORE_CHAT_INTERACTIONS", default=False)

# Cookie and browser security controls are relaxed only for local development.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = False  # The chat widget reads this token for same-origin POSTs.
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
SECURE_SSL_REDIRECT = _environment_flag("SECURE_SSL_REDIRECT", default=not DEBUG)
SECURE_HSTS_SECONDS = 31_536_000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Admin branding.
ADMIN_SITE_HEADER = "Jaime Allen Therapy Administration"
ADMIN_SITE_TITLE = "Therapy Site Admin"
ADMIN_INDEX_TITLE = "Welcome to Therapy Administration Portal"
