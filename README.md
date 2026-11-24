# Jaime Allen — Professional Profile, Static Site, and Django Prototype

This repository contains a public static website, retained historical relationship-resource pages, and a separate Django application prototype. These are distinct deployment surfaces and must remain clearly separated.

## Current professional profile

The current public practice listing identifies Jaime Allen as a **Licensed Marriage & Family Therapist (California LMFT #164998)** with **Insightful Matters Family Counseling Professionals**. The practice profile lists virtual telehealth as her service location.

The official profile currently lists:
- Master’s degree in Marriage and Family Therapy from Pacific Oaks College.
- English as the language spoken.
- Age ranges: adolescence (12–20), young adult (21–35), adulthood (35–50), and midlife (50–80).
- A professional approach that includes psychodynamic therapy and EMDR training.
- Experience and areas described by the practice profile including trauma support, cancer-related support, couples counseling, LGBTQ+ affirming care, and creative approaches such as art therapy, horticultural therapy, and dream journaling.

**Source of truth:** [Jaime Allen — Insightful Matters](https://www.insightfulmatters.com/jaime-allen). The practice’s page controls current services, scope, availability, contact methods, and booking options. This repository is a secondary presentation and must be reconciled whenever the official profile changes. The former AMFT designation, former registration number, and old supervisor listing have been retired from the current profile pages; do not reintroduce them.

## Project layout

- `index.html` is the primary static landing page published with GitHub Pages.
- `foyer_index.html` is a retained historical relationship-resource archive and links into older material under `website/`.
- `website/` contains legacy static pages and styles. The old biography page has been replaced with a current-profile summary; other historical topic pages are explicitly presented as an archive, not as a live service catalogue.
- `therapy_site/` contains a separate Django application prototype, including dependencies, migrations, static assets, and tests. Its SQLite development database is created locally by migrations and is deliberately not tracked in the repository.

The root `_config.yml` excludes the Django application and development metadata from the Jekyll Pages build. Keep this boundary intact: GitHub Pages is static hosting, not a Django runtime. Validate static-site changes and Django changes independently.

## Static site, privacy, and clinical boundaries

The interactive Seascape/relationship reflection content is an educational experience only. It is not therapy, diagnosis, treatment, crisis counseling, emergency response, or a clinical record. Do not invite users to submit health details through this static site. The static page is not a client portal and is not an approved channel for protected health information. Direct users to the official practice website for approved communication, portal, and appointment options.

Do not describe the GitHub Pages site, prototype, or AI widget as HIPAA-compliant or otherwise certified. Do not embed payment links or make clinical-payment claims unless the practice explicitly authorizes a reviewed implementation.

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

**The current default-branch tree no longer contains the SQLite database.** A previous version of the development database was committed while this repository was public. Removing it from the current tree does not remove historical copies from Git history, forks, caches, or existing clones. Treat the historical database as potentially sensitive until a responsible data owner has reviewed it privately. The repository should remain private until that review and a coordinated historical-exposure response are complete.

The prototype now creates a local development database from migrations. Run `python manage.py migrate` and `python manage.py init_services` from `therapy_site/`; create any local administrator with `python manage.py createsuperuser`. The removed development database is not restored automatically. Never commit a replacement SQLite file, real client/patient/appointment records, or production credentials. Use a secured private managed database for any approved deployment.

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
- `DEPLOY.txt` documents the boundaries and validation steps; it is not proof of a live deployment.

Preserve the static site and Django prototype together unless their ownership, deployment, or release lifecycles become genuinely independent. Do not treat this repository, its Pages site, or its current database as an approved clinical record system.

## Security

See [SECURITY.md](SECURITY.md) for this repository's security, privacy, and responsible-use guidance.
