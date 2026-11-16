# Security Policy

## Reporting a vulnerability

Do not publish suspected vulnerabilities, private client information, credentials, or sensitive request data in public issues. Use GitHub private vulnerability reporting when enabled or contact the maintainers privately.

## Sensitive messages and AI providers

This application may process personal relationship or wellbeing messages. The default database behavior does not persist chat transcripts; storage is enabled only when `STORE_CHAT_INTERACTIONS=true` is explicitly configured. This does not prevent the selected AI provider from processing the message to generate a response.

Before enabling the widget for the public:
- Disclose which AI provider processes each message.
- Obtain informed consent before transmission of personal content.
- Define access, retention, deletion, backup, and incident-response practices.
- Do not log message bodies, provider payloads, or personal content.
- Keep real messages out of fixtures, issues, logs, screenshots, and CI artifacts.

## Clinical and emergency boundaries

The AI widget is not a clinician, diagnostic system, treatment provider, crisis service, or emergency-response channel. Have a qualified professional review prompts, content, crisis language, and escalation instructions before production.

## Supported framework

The project should use supported Django security releases. CI pins Django 6.1.3 and checks the maintained Python modules across supported Python versions.
