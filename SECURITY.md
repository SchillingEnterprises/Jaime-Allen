# Security Policy

## Scope and deployment status

This repository contains a static relationship-therapy website and a separate Django application prototype under `therapy_site/`. The repository is public.

GitHub Pages is configured to exclude the Django application from the published static site. This does **not** make files in the Git repository private: anyone who can view this public repository can inspect its tracked files and history.

## Important data exposure warning

A SQLite database file is currently tracked under `therapy_site/`. Its records have not been inspected during this maintenance work. Treat the file as potentially sensitive until the project owner has reviewed it in a suitably private environment. Do not add real client, patient, appointment, or other sensitive information to this repository.

If sensitive information is or has been stored there, removing the current database file is not sufficient: earlier commits may still contain copies. Review the data and history, preserve any required records securely, and plan an appropriately reviewed history-removal and exposure-response process. Any credentials included in the exposed history must be rotated.

## Production requirements

The Django prototype is not a substitute for a production security and privacy review. Before handling real user information, establish an approved hosting environment, private managed database, secure secret management, authentication and authorization, HTTPS, encrypted backups, audit and retention controls, and appropriate review of any external AI or messaging providers.

Do not disable existing access controls or production checks to make a deployment pass.

## Reporting

Report suspected vulnerabilities privately through the repository's GitHub security reporting channel when available. Do not include personal or sensitive records in public issues or pull requests.
