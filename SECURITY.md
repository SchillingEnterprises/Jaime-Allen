# Security Policy

## Reporting a vulnerability

Please do not publish suspected vulnerabilities, private client information, credentials, or sensitive request data in public issues.

Use GitHub private vulnerability reporting for this repository when it is enabled. Otherwise contact the maintainers privately through GitHub. Include affected components, impact, and reproduction steps with secrets and personal information removed.

## Security-sensitive application data

This application may process sensitive personal messages. Production deployments must use HTTPS, strong environment-provided secrets, restricted database access, backups, and a documented retention policy. Do not place real client information in development fixtures, issues, logs, screenshots, or test output.

## Supported versions

The default branch is the primary maintenance line. Dependency and framework upgrades must be validated by the CI checks and reviewed for third-party compatibility before deployment.
