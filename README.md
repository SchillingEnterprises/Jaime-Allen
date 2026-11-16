# Jaime Allen Relationship Support Website

A Django-powered website prototype for relationship education and communication-support services. The project includes a public service catalogue, service-detail pages, and an optional AI-assisted communication widget.


## Repository map

This repository intentionally preserves two related web surfaces rather than treating every file as part of one Django runtime:

- **Current root experience:** `index.html` is the modern static landing experience. It is plain static web content and does not execute Django.
- **Legacy static content:** `foyer_index.html` is a retained earlier entry page. Its supporting content lives under `website/page sections/`, with shared styles in `website/static/css/styles.css`. Keep these pages available until their links and any replacement content have been reviewed.
- **Relationship-support application:** `therapy_site/` is the separately runnable Django application, with its own settings, requirements, database, templates, tests, and AI-support integration. Its backend requires a Python/Django host; GitHub Pages cannot run Django.

The static and Django surfaces can remain in this repository because they share the Jaime Allen project identity and historical content, but they must keep separate build, test, and deployment boundaries. Do not assume a static page deployment also deploys the Django backend.

### Preserved and generated content

The repository currently contains a tracked SQLite database at `therapy_site/db.sqlite3`, generated Django static output under `therapy_site/staticfiles/`, and Python bytecode/cache files. This maintenance pass does not remove, rewrite, or publish database contents. Treat the database as protected historical/application data. Before cleaning generated files from version control, inspect their provenance and any deployment dependency, then make a separate reviewed change that does not alter database rows.

The file `DEPLOY.txt` contains a legacy deployment note. Verify its destination and platform against the current hosting configuration before relying on it; it is not, by itself, proof of a live deployment.

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
