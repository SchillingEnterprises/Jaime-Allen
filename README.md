# Jaime Allen Relationship Support Website

A Django-powered website prototype for relationship education and communication-support services. The project includes a public service catalogue, service-detail pages, and an optional AI-assisted communication widget.

## Scope and safety boundaries

- The AI widget is a communication-support aid, not therapy, diagnosis, treatment, emergency response, or a substitute for a qualified clinician.
- The backend uses the local Ollama provider by default when configured. OpenAI is an optional provider and is not called unless explicitly selected with an API key.
- Chat messages are not written to the application database unless `STORE_CHAT_INTERACTIONS=true` is deliberately configured.
- The frontend should disclose which AI provider processes the message and obtain the appropriate consent before a user submits personal content.
- This repository is a software prototype. Clinical, legal, privacy, and content review are required before production use.

## Requirements

- Python 3.12–3.14
- Django 6.1.3
- See `therapy_site/requirements.txt` for the complete pinned dependency set.

## Local development

```bash
cd therapy_site
python -m venv .venv
# Activate the environment, then:
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set a local secret. The project loads the local environment file in development. Never commit real secrets.

```bash
python manage.py migrate
python manage.py runserver
```

Open the local server address printed by Django.

## Quality checks

From `therapy_site/`:

```bash
ruff check main/views.py main/tests.py therapy_app/settings.py therapy_app/ai_agents.py
node --check static/js/ai-chatbot.js
python -m compileall -q main therapy_app
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --verbosity 2
```

GitHub Actions runs these checks on Python 3.12, 3.13, and 3.14.

## Production considerations

The current settings default to SQLite for local development. A production deployment needs a supported managed database, host-specific secrets, HTTPS, backups, monitoring, an appropriate privacy notice and retention policy, and provider-specific data-processing disclosures.

The project is not ready to publish as a live clinical or therapy service until a qualified professional reviews the content and a responsible operator confirms the privacy, security, consent, and escalation workflows.
