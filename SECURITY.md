# Security Policy

## Scope and deployment status

This public repository contains a static relationship-support website and a separate Django application prototype under `therapy_site/`. GitHub Pages is configured to exclude the Django application from the published static site. This does **not** make files in the Git repository or its history private.

## Sensitive data and repository exposure

A SQLite database file is tracked under `therapy_site/`. Its records have not been inspected during this maintenance work. Treat the file as potentially sensitive until the project owner has reviewed it in a suitably private environment. Do not add real client, patient, appointment, or other sensitive information to this repository.

If sensitive information is or has been stored there, removing the current database file is not sufficient: earlier commits may still contain copies. Review the data and history privately, preserve any required records securely, and plan an appropriately reviewed history-removal and exposure-response process. Rotate any credentials included in exposed history.

## AI provider and message handling

The application may process personal relationship or wellbeing messages. Database transcript persistence is disabled by default and is enabled only when `STORE_CHAT_INTERACTIONS=true` is explicitly configured. This does not prevent the selected AI provider from processing a message to generate a response.

Before enabling the widget for public use:

- Disclose which AI provider processes each message.
- Obtain affirmative consent before transmitting personal content.
- Define access, retention, deletion, backup, and incident-response practices.
- Do not log message bodies, provider payloads, or personal content.
- Keep real messages out of fixtures, issues, logs, screenshots, and CI artifacts.
- Review the provider's data-processing terms and the application's privacy notice.

The local Ollama option and optional OpenAI integration have different deployment and data-flow characteristics; the active provider must be disclosed accurately.

## Clinical and emergency boundaries

The AI widget is not a clinician, diagnostic system, treatment provider, crisis service, or emergency-response channel. Qualified professionals must review prompts, public-facing content, crisis language, and escalation instructions before production use.

## Production requirements

The Django prototype is not production-approved. Before handling real user information, establish an approved hosting environment, private managed database, secure secret management, authentication and authorization, HTTPS, encrypted backups, audit and retention controls, monitoring, and appropriate review of external AI or messaging providers.

Do not disable existing access controls or production checks to make a deployment pass.

## Supported framework

Use supported Django security releases and keep dependency updates covered by automated checks. The project CI is designed to validate maintained Python modules across Python 3.12–3.14.

## Reporting

Report suspected vulnerabilities privately through GitHub private vulnerability reporting when available or contact the maintainers privately. Do not include personal or sensitive records in public issues or pull requests.
