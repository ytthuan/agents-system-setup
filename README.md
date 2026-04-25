# agents-system-setup

[![CI](https://github.com/ytthuan/agents-system-setup/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ytthuan/agents-system-setup/actions/workflows/ci.yml)
[![Release](https://github.com/ytthuan/agents-system-setup/actions/workflows/release.yml/badge.svg)](https://github.com/ytthuan/agents-system-setup/actions/workflows/release.yml)
[![Latest release](https://img.shields.io/github/v/release/ytthuan/agents-system-setup?sort=semver&display_name=tag)](https://github.com/ytthuan/agents-system-setup/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Cross-OS](https://img.shields.io/badge/cross--os-linux%20%7C%20macos%20%7C%20windows-blue)](.github/workflows/ci.yml)
[![Runtimes](https://img.shields.io/badge/runtimes-Copilot%20CLI%20%7C%20Claude%20Code%20%7C%20Codex%20%7C%20OpenCode-purple)](#install--per-runtime)

A multi-runtime plugin that **bootstraps**, **updates**, **improves**, or **replicates** a complete multi-agent system across **GitHub Copilot CLI**, **Claude Code**, **OpenCode**, and **OpenAI Codex CLI** — from a single skill, with a Canonical IR for bidirectional replication, parallel-aware orchestration, mandatory security/audit/architecture governance, and compact-by-default context output baked in.

## What it generates

- `AGENTS.md` at repo root with a **Read First** section, **Context Loading Policy**, **Directory Architecture**, **Agent Roster (with parallel-safety waves)**, **Capability Matrix**, **Security & Audit Matrix**, **Threat Model**, **Architecture / Design Pattern Decisions**, **ADR Index**, and **Quality Gates**.
- **Orchestrator + N subagents** (3–50, sized to scope) emitted in the right format for every selected runtime, with a **fan-out clause** so parallel-safe subagents always run in one wave.
- **`AGENT-TEAMS.md`** for Claude Code projects when the roster benefits from peer-to-peer teammates (3+ independent concerns).
- Project-scoped **skills** under each runtime's conventional path.
- **Curated plugin / MCP recommendations** from vendor-official catalogs, every recommendation tagged `[Tier · Vendor]` and **opt-in per item**.
- **Mandatory MCP approval gate** — no MCP config is ever written without explicit user approval.
- **Source-backed governance baseline** — OWASP GenAI, NIST SSDF, MCP Security Best Practices, GitHub Code Security, SLSA, OPA, Azure Well-Architected, C4, and TOGAF (enterprise only).
- **Context-optimized output profiles** — `Balanced` by default, with `Compact` and `Full` options for generated files and summaries.
- Cross-OS scripts (`.sh` + `.ps1`), `.gitattributes` for line-ending safety.

## Modes

| Mode | When to use |
|---|---|
| `init` | Brand-new repo, no agent artifacts |
| `update` | Existing artifacts, regenerate managed blocks non-destructively |
| `improve` | Audit existing system → propose checklist of targeted fixes → opt-in apply |
| `replicate` | Port agents/skills/MCP from one runtime to another (Copilot ↔ Claude ↔ OpenCode ↔ Codex) via Canonical IR |

## Install — per runtime

Each runtime has a different install mechanism. The repo ships the right manifest for each.

### GitHub Copilot CLI

```
copilot
> /plugin install ytthuan/agents-system-setup
> /agents-system-setup
```

Reads the root `plugin.json` and exposes the bundled skill as `/agents-system-setup`.

### Claude Code

```
claude
> /plugin install ytthuan/agents-system-setup
> /agents-system-setup:agents-system-setup
```

Reads `.claude-plugin/plugin.json`. Skills are namespaced as `/<plugin>:<skill>`. Source: <https://docs.anthropic.com/en/docs/claude-code/plugins>.

### OpenAI Codex CLI

```bash
codex plugin marketplace add ytthuan/agents-system-setup
codex
> /plugins        # browse and install agents-system-setup
> @agents-system-setup
```

Reads `.codex-plugin/plugin.json` and the marketplace descriptor at `.agents/plugins/marketplace.json`. Source: <https://developers.openai.com/codex/plugins/build>.

### OpenCode

OpenCode plugins are JS/TS hooks — not skill bundles — so install by clone-and-copy:

```bash
git clone https://github.com/ytthuan/agents-system-setup.git
cd agents-system-setup
./scripts/install-opencode.sh project   # or "global"
```

Windows / cross-platform PowerShell:

```powershell
git clone https://github.com/ytthuan/agents-system-setup.git
cd agents-system-setup
pwsh ./scripts/install-opencode.ps1 -Scope project
```

This places the skill at `.opencode/skills/agents-system-setup/` (or `~/.config/opencode/skills/` for global).

## Usage

Once installed, invoke the skill — no arguments needed; it auto-detects mode:

```
/agents-system-setup
```

Or be explicit:

```
/agents-system-setup init
/agents-system-setup update
/agents-system-setup improve
/agents-system-setup replicate
```

## Parallel subagents & Claude Code agent teams

The generated orchestrator always fans out **parallel-safe subagents** in one wave (multiple `Task` calls in a single response), then awaits before the next wave. Parallel-safety is computed automatically from the Directory Architecture — see [parallelism reference](./plugins/agents-system-setup/skills/agents-system-setup/references/parallelism.md).

For Claude Code, when 3+ subagents are independent and would benefit from peer-to-peer challenge, the generator additionally emits `AGENT-TEAMS.md` with the opt-in env var (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`), settings snippet, suggested teammate roster, and a token-cost warning. Source: <https://docs.anthropic.com/en/docs/claude-code/agent-teams>.

## Context optimization

Generated output is **compact by default**. The skill asks for an output profile (`Balanced`, `Compact`, or `Full`) and records where long detail lives. `AGENTS.md` stays the routing and policy index; exhaustive marketplace research, long threat rationale, full ADR text, and platform schema detail are linked as references instead of repeated in every agent file.

## Why a plugin (not a bare skill)?

- A **skill** is the *unit of capability*.
- A **plugin** is the *distribution unit*.
- Wrapping the skill in plugin manifests for each runtime makes it one-line installable on Copilot CLI / Claude Code / Codex, and clone-and-copy installable on OpenCode.

## Repo layout

```
agents-system-setup/
├── plugin.json                  # Copilot CLI manifest
├── .claude-plugin/plugin.json   # Claude Code manifest
├── .codex-plugin/plugin.json    # Codex CLI manifest
├── .agents/plugins/marketplace.json   # Codex marketplace descriptor
├── scripts/
│   ├── install-opencode.sh      # OpenCode installer (POSIX)
│   └── install-opencode.ps1     # OpenCode installer (PowerShell)
├── plugins/
│   └── agents-system-setup/
│       ├── .claude-plugin/plugin.json
│       ├── .codex-plugin/plugin.json
│       └── skills/
│           └── agents-system-setup/
│               ├── SKILL.md
│               ├── references/      # platforms, marketplaces, replication, governance, …
│               ├── assets/          # AGENTS.md + agent/skill templates
│               └── scripts/         # git-init.sh + .ps1, link-project-memory.sh + .ps1
├── README.md
├── DESIGN.md                    # rationale per phase / hard rule
├── CHANGELOG.md
├── LICENSE                      # MIT
├── .gitignore
└── .gitattributes
```

## Compatibility

| Runtime | Plugin install | Skill format compatible | Parallel subagents | Agent teams |
|---|---|---|---|---|
| GitHub Copilot CLI | ✅ `/plugin install` | ✅ | ✅ | n/a |
| Claude Code | ✅ `/plugin install` | ✅ | ✅ | ✅ (opt-in env var) |
| OpenAI Codex CLI | ✅ `marketplace add` + `/plugins` | ✅ | ✅ | n/a |
| OpenCode | ⚠️ clone + script copy | ✅ | ✅ | n/a |

Cross-OS: Linux, macOS, Windows (native PowerShell + Git Bash + WSL).

## Design rationale

The procedure is intentional, not arbitrary. See [DESIGN.md](./DESIGN.md) for the reasoning behind every phase (why interview-first, why MCP gate, why Canonical IR, why per-item opt-in, why parallel-by-default).

## Contributing

PRs welcome. The skill is documented heavily in `plugins/agents-system-setup/skills/agents-system-setup/references/`. New marketplace sources go in `references/marketplaces.md` with a `[Tier · Vendor]` tag.

## License

MIT — see [LICENSE](./LICENSE).
