# Security Policy

## Supported Versions

The latest minor release on `main` is supported. Older releases receive fixes only for actively exploited vulnerabilities.

## Reporting a Vulnerability

**Do not open a public issue for security reports.**

Please use GitHub's private vulnerability reporting:

1. Go to <https://github.com/ytthuan/agents-system-setup/security/advisories/new>
2. Provide: a description, reproduction steps, affected version(s), and impact assessment.

We aim to acknowledge within 72 hours and ship a fix or mitigation within 14 days for High/Critical severity.

## Scope

In scope:
- The skill content under `plugins/agents-system-setup/skills/agents-system-setup/`
- The installer scripts under `scripts/` and `plugins/agents-system-setup/skills/agents-system-setup/scripts/`
- The plugin manifests (Copilot, Claude, Codex, marketplace)

Out of scope (report directly to the upstream project):
- Vulnerabilities in GitHub Copilot CLI, Claude Code, OpenCode, or OpenAI Codex (CLI or App) themselves
- Vulnerabilities in third-party MCP servers recommended by the skill — those are surfaced for opt-in install but maintained externally

## Disclosure

We follow coordinated disclosure. Once a fix is released, we publish a GitHub Security Advisory crediting the reporter (unless anonymity is requested).
