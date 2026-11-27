# Security Policy

## Scope and deployment status

This public repository contains a static relationship-support website and a separate Django application prototype under `therapy_site/`. GitHub Pages is configured to exclude the Django application from the published static site. This does **not** make files in the Git repository or its history private.

## Sensitive data and repository exposure

The tracked SQLite development database has been removed from the current default-branch tree. A prior version was committed while this repository was public, so its historical contents may remain accessible through earlier commits, forks, caches, and existing clones. Treat it as potentially sensitive until the responsible data owner has reviewed it privately. Keep the repository private until the review and coordinated historical-exposure response are complete.

The local Django database is now created from migrations; the historical database is not restored automatically. Do not re-add or replace a tracked SQLite file. Do not add real client, patient, appointment, or other sensitive information to this repository. If a replacement data source is approved for production, it must be a secured private managed database with documented access, retention, backup, and deletion controls.

Removing the current file is not a history rewrite. Any historical database, credentials, or sensitive records need a separate, approved exposure-response and coordinated clone/fork/cache remediation plan.

## AI provider and message handling

The application may process personal relationship or wellbeing messages. Database transcript persistence is disabled by default and is enabled only when `STORE_CHAT_INTERACTIONS=true` is explicitly configured. This does not prevent the selected AI provider from processing a message to generate a response.

Before enabling the widget for public use:

- Disclose which AI provider processes each message.
- Obtain affirmative consent before transmitting personal content.
- Define access, retention, deletion, backup, and incident-response practices.
- Keep the anonymous chat endpoint's per-process limit of five POST attempts per minute as defense in depth; configure a shared cache for multi-worker enforcement and an edge/WAF rate limit before public production use.
- Do not log message bodies, provider payloads, personal content, or exception text and tracebacks originating in AI/analyzer calls. Operational error logs may include only the exception class name.
- Keep real messages out of fixtures, issues, logs, screenshots, and CI artifacts.
- Review the provider's data-processing terms and the application's privacy notice.

The local Ollama option and optional OpenAI integration have different deployment and data-flow characteristics; the active provider must be disclosed accurately.

## Clinical and emergency boundaries

The AI widget is not a clinician, diagnostic system, treatment provider, crisis service, or emergency-response channel. Qualified professionals must review prompts, public-facing content, crisis language, and escalation instructions before production use.

## Production requirements

The Django prototype is not production-approved. Before handling real user information, establish an approved hosting environment, private managed database, secure secret management, authentication and authorization, HTTPS, encrypted backups, a shared cache and edge/WAF rate limiting for the anonymous AI endpoint, audit and retention controls, monitoring, and appropriate review of external AI or messaging providers.

Non-debug settings now fail at startup unless `DB_NAME`, `DB_USER`, `DB_PASSWORD`, and `DB_HOST` configure PostgreSQL. TLS is mandatory: `DB_SSLMODE` accepts only `require`, `verify-ca`, or `verify-full`, and defaults to certificate- and hostname-verifying `verify-full`. Store connection secrets in the host's secret manager. Local SQLite remains for `DEBUG=true` development and CI only.

Do not disable existing access controls or production checks to make a deployment pass.

## Supported framework

Use supported Django security releases and keep dependency updates covered by automated checks. The project CI is designed to validate maintained Python modules across Python 3.12–3.14.

## Reporting

Report suspected vulnerabilities privately through GitHub private vulnerability reporting when available or contact the maintainers privately. Do not include personal or sensitive records in public issues or pull requests.
