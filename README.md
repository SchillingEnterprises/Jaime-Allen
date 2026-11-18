# Jaime Allen — Relationship Support Website and Django Prototype

This repository contains related but separate website and application work for the Jaime Allen project.

## Project layout

- `index.html` is the primary static landing page published with GitHub Pages.
- `foyer_index.html` is a retained legacy entry page that links into archived material under `website/`.
- `website/` contains legacy static pages and shared styles.
- `therapy_site/` contains a separate Django application prototype, including its own dependencies, migrations, static assets, tests, and development database. It is not part of the GitHub Pages site.

The root `_config.yml` excludes the Django application and development metadata from the Jekyll Pages build. Keep this boundary intact: GitHub Pages is static hosting, not a Django runtime. Validate static-site changes and Django changes independently.

## AI-support prototype and privacy

The optional AI widget is a communication-support aid, not therapy, diagnosis, treatment, crisis counseling, emergency response, or a substitute for a qualified clinician.

- The backend defaults to the local Ollama provider when configured.
- OpenAI is an optional provider and is used only when explicitly selected with an API key.
- The interface must disclose which provider processes a message and obtain affirmative consent before transmitting personal content.
- Chat messages are not written to the application database unless `STORE_CHAT_INTERACTIONS=true` is deliberately configured.
- Disabling database persistence does not prevent the selected provider from processing the message to generate a response.
- Prompts and provider payloads must not be written to application logs.

Do not enable public use until a qualified professional and responsible operator have reviewed the content, consent language, privacy notice, provider data handling, retention/deletion policy, and escalation boundaries.

## Data and public-repository warning

**This is a public GitHub repository. A SQLite database file is tracked under `therapy_site/`, and its contents and historical versions may be accessible to anyone who can view the repository.** The database has not been opened or reviewed as part of this maintenance work. Do not place real client, patient, appointment, or other sensitive records in this repository.

Before using the Django prototype with real people or sensitive information, move data to an appropriately secured private database. If sensitive information is or has been stored in the tracked database, removing the current file alone is not sufficient: earlier commits may still contain copies. Review the data and history privately, preserve any required records securely, and plan a reviewed history-removal and exposure-response process. Rotate any credentials found in exposed history.

## Requirements and local development

The Django prototype has its own dependency manifest at `therapy_site/requirements.txt` and its own `manage.py`. Use Python 3.12–3.14 and work from the `therapy_site/` directory in an isolated virtual environment.

```bash
cd therapy_site
python -m venv .venv
# Activate the environment, then:
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set local development values. Never commit real secrets.

```bash
python manage.py migrate
python manage.py runserver
```

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

GitHub Actions is intended to run the Django checks on Python 3.12, 3.13, and 3.14. The static-site validation workflow is separate. A passing Pages build does not validate Django or make the backend production-ready.

## Deployment boundaries

- GitHub Pages publishes the static root website and the linked `website/` archive only.
- The Django prototype requires separate application hosting, a production database, managed secrets, authentication and authorization review, secure transport, backups, monitoring, and privacy review.
- The current Django settings retain SQLite for local development. A production deployment needs an appropriately secured managed database and deployment-specific settings.
- The legacy `DEPLOY.txt` note must be checked against the current hosting configuration; it is not proof of a live deployment.

Preserve the static site and Django prototype together unless their ownership, deployment, or release lifecycles become genuinely independent. Do not treat this repository, its Pages site, or its current database as an approved clinical record system.
