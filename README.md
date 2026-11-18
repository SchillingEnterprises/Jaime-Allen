# Jaime Allen — Relationship Therapy Website and Django Prototype

This repository contains related but separate website and application work for the Jaime Allen project.

## Project layout

- `index.html` is the primary static landing page published with GitHub Pages.
- `foyer_index.html` is a legacy entry page that links into the archived material under `website/`.
- `website/` contains the legacy static pages and stylesheet used by that entry page.
- `therapy_site/` contains a separate Django application prototype, including its own dependencies, migrations, static assets, and development database. It is not part of the GitHub Pages site.

The root `_config.yml` excludes the Django application and development metadata from the Jekyll Pages build. Keep that boundary intact: GitHub Pages is static hosting, not a Django runtime.

## Development

The Django prototype has its own dependency manifest at `therapy_site/requirements.txt` and its own `manage.py`. Work on it from the `therapy_site/` directory, using an isolated virtual environment and configuration appropriate for local development. Do not assume that a successful Pages build validates the Django application or makes it production-ready.

## Data and privacy warning

**This is a public GitHub repository. A SQLite database file is currently tracked under `therapy_site/`, so its contents and historical versions may be accessible to anyone who can view the repository.** Do not place real client, patient, appointment, or other sensitive records in this repository. The database has not been opened or reviewed as part of this maintenance work.

Before using the Django prototype with real people or sensitive information, move data to an appropriately secured private database and arrange a reviewed removal of any sensitive data from Git history if needed. Deleting the current file alone does not erase earlier committed copies.

## Deployment boundaries

- GitHub Pages publishes the static root website and the linked `website/` archive only.
- The Django prototype requires separate application hosting, a production database, managed secrets, authentication and authorization review, secure transport, backups, logging, and privacy review.
- Do not treat the repository, its Pages site, or its current database as an approved clinical record system.

## Maintenance

Preserve the original static pages and Django project together in this repository unless their ownership, deployment, or release lifecycles become genuinely independent. When making changes, validate the static Pages build separately from Django tests and deployment checks.
