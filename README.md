# agents-system-setup

[![CI](https://github.com/ytthuan/agents-system-setup/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ytthuan/agents-system-setup/actions/workflows/ci.yml)
[![Release](https://github.com/ytthuan/agents-system-setup/actions/workflows/release.yml/badge.svg)](https://github.com/ytthuan/agents-system-setup/actions/workflows/release.yml)
[![Latest release](https://img.shields.io/github/v/release/ytthuan/agents-system-setup?sort=semver&display_name=tag)](https://github.com/ytthuan/agents-system-setup/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Cross-OS](https://img.shields.io/badge/cross--os-linux%20%7C%20macos%20%7C%20windows-blue)](.github/workflows/ci.yml)
[![Runtimes](https://img.shields.io/badge/runtimes-Copilot%20CLI%20%7C%20Claude%20Code%20%7C%20Codex%20%7C%20OpenCode%20%7C%20Gemini-purple)](#install--per-runtime)

- A multi-runtime plugin/skill package that **bootstraps**, **updates**, **improves**, **upgrades**, or **replicates** a complete multi-agent system across five supported runtimes: **GitHub Copilot CLI**, **Claude Code**, **OpenCode**, **OpenAI Codex (CLI + App)**, and **Gemini CLI** artifact layouts — from a single skill, with a Canonical IR for bidirectional replication, parallel-aware orchestration, mandatory security/audit/architecture governance, version-stamped artifacts, and compact-by-default context output baked in.

## Relationship to Copilot `/init` and native `AGENTS.md` support

This plugin **complements** Copilot's built-in `/init` and native `AGENTS.md` interop — it does not duplicate them. `/init` analyzes a repo and seeds a single Copilot guidance file, which Copilot (and other agents) then read natively. That single-file, single-runtime bootstrap is the *starting point* this plugin builds on, not what it competes with — an `/init`-seeded `AGENTS.md` is a valid input to `update`/`improve` mode.

`agents-system-setup` adds capabilities no built-in command provides:

- **A governed multi-agent system, not one guidance file.** Generates an Agent Roster, Capability Matrix, Security & Audit Matrix, Threat Model, Architecture/ADR decisions, and N specialized subagents with parallel-safety waves, wired to a host-session Orchestration Operating Model.
- **Cross-runtime, via a Canonical IR.** Emits and *replicates* the same system across five runtimes — Copilot CLI, Claude Code, OpenCode, OpenAI Codex, Gemini CLI — each in its native agent/skill/permission format. `/init` is Copilot-only.
- **Lifecycle, not one-shot.** Five modes: `init`, `update` (non-destructive managed blocks), `improve` (audit → opt-in fixes), `upgrade` (version-stamped migration of an existing system), and `replicate` (port between runtimes).
- **Security & governance gates.** A mandatory MCP approval gate (no MCP config is written without explicit approval) and a source-backed baseline (OWASP GenAI, NIST SSDF, MCP Security Best Practices, SLSA, …).
- **Opt-in plugin/MCP discovery** from vendor-official catalogs, every item tagged `[Tier · Vendor]` and approved per item.

In short: `/init` writes the first file for one agent; this plugin architects, governs, audits, upgrades, and ports a multi-agent system across five.

## What it generates

- `AGENTS.md` at repo root with a **Read First** section, **Context Loading Policy**, **Directory Architecture**, **Agent Roster (with parallel-safety waves)**, **Capability Matrix**, **Security & Audit Matrix**, **Threat Model**, **Architecture / Design Pattern Decisions**, **ADR Index**, and **Quality Gates**.
- **Host-session Orchestration Operating Model + N specialized subagents** — the host CLI session (Copilot CLI, Claude Code, OpenCode, Codex CLI, Gemini CLI) reads the new `## Orchestration Operating Model` section in `AGENTS.md` and adopts the orchestrator role directly. No runtime emits an `orchestrator.agent.md` / `.claude/agents/orchestrator.md` / `.opencode/agents/orchestrator.md` / `.codex/agents/orchestrator.toml` / `.gemini/agents/orchestrator.md` subagent file. Specialized subagents (3–50, sized to scope) are emitted in each runtime's native format with a **fan-out clause** so parallel-safe subagents always run in one wave. `@orchestrator` remains a routing alias for the host session.
- A **Plan Handoff Contract** that normalizes VS Code Plan agent output, Spec-Kit `/plan`, or user-written plans before emitting runtime-correct Copilot, Claude Code, OpenCode, Codex, or Gemini CLI artifacts.
- **`AGENT-TEAMS.md`** for Claude Code projects when the roster benefits from peer-to-peer teammates (3+ independent concerns).
- Project-scoped **skills** under each runtime's conventional path.
- **Curated plugin / MCP recommendations** from vendor-official catalogs, every recommendation tagged `[Tier · Vendor]` and **opt-in per item**.
- **Mandatory MCP approval gate** — no MCP config is ever written without explicit user approval.
- **Source-backed governance baseline** — OWASP GenAI, NIST SSDF, MCP Security Best Practices, GitHub Code Security, SLSA, OPA, Azure Well-Architected, C4, and TOGAF (enterprise only).
- **Code Quality & Maintainability standards** — for software-dev projects, generated coding agents apply source-backed authoring craft *while writing* (Google Eng-Practices, ISO/IEC 25010, refactoring/code-smells, Clean Code concepts, McCabe complexity), leading with **conform to the project's existing linters/conventions first**. A read-only `code-quality-reviewer` reports code smells; the host loads the `code-quality` skill before code edits. Complementary to the SDLC Build Gate (verification) and distinct from content-quality (generated-prose review).
- **Context-optimized output profiles** — `Balanced` by default, with `Compact` and `Full` options for generated files and summaries.
- **Artifact tracking choice** — generated systems can be team-shared in git, local-only via `.git/info/exclude`, or written to personal/global runtime paths.
- **Memory & Learning System** — generated agents can load curated learnings, run a before-finish Learning Check, and propose durable project lessons without silently overwriting past memory.
- **Runtime update audit** — latest upstream drift is tracked in `plugins/agents-system-setup/skills/agents-system-setup/references/runtime-updates.md` for all supported runtimes and future candidates.
- **Optional model overrides — opt-in only.** The interview never asks about model selection by default; the question only surfaces when the user has spontaneously named a model or asked for BYOK/multi-model/cost-perf tuning. Per-runtime accepted formats, defaults, and source-linked rate-limit pointers live in `plugins/agents-system-setup/skills/agents-system-setup/references/models.md`.
- **Version-stamped artifacts + central manifest.** Every generated `AGENTS.md`, subagent, and skill carries an `agents-system-setup:generated-by: vX.Y.Z` marker; `.agents-system-setup/generated.json` records the authoritative version. `upgrade` mode reads stamps and walks the per-version delta playbook to migrate old systems to the current principles non-destructively.
- **Sharper context engine** — generated `AGENTS.md` includes a Task-Type Routing Map, a context-freshness rule, and a single canonical Delegation Packet schema in `references/handoff.md` so subagents skip duplicated reads and load only what each task tag needs.
- **Richer task assignments** — host-orchestrator → subagent handoffs use a canonical Task Assignment Contract with required minimum + opt-in expansion blocks (Goal & Definition of Done, Scope, File Inventory, Background, Reproduction, Constraints, Assumptions, Known Risks, Verification Protocol, Reporting Protocol, Coordination, Size & Timebox, Clarification Protocol). Subagent templates ship with an Acceptance Checklist and Reporting Template so handoffs are well-structured by default.
- **Gemini CLI artifact support** — generated Gemini subagents use `.gemini/agents/*.md` or Gemini extension `agents/*.md`; no Gemini plugin install command is claimed.
- Cross-OS scripts (`.sh` + `.ps1`), `.gitattributes` for line-ending safety.

## Modes

| Mode | When to use |
|---|---|
| `init` | Brand-new repo, no agent artifacts |
| `update` | Existing artifacts, regenerate managed blocks non-destructively |
| `improve` | Audit existing system → propose checklist of targeted fixes → opt-in apply |
| `upgrade` | Version-aware migration of an existing agent system to the current plugin's principles (reads `agents-system-setup:generated-by` stamps + `.agents-system-setup/generated.json`, walks per-version delta playbook). Trigger: `/agents-system-setup upgrade` or `agents-system-setup upgrade` |
| `replicate` | Port agents/skills/MCP from one runtime to another (Copilot ↔ Claude ↔ OpenCode ↔ OpenAI Codex ↔ Gemini CLI) via Canonical IR |

## Install — per runtime

Each runtime has a different install/use mechanism. The repo ships plugin manifests where a runtime supports them; Gemini CLI support is artifact-based and does not claim a plugin install. These commands track the default branch — to pin a released version, see [Install a specific release](#install-a-specific-release).

### GitHub Copilot CLI

```
copilot
> /plugin install ytthuan/agents-system-setup
> /agents-system-setup
```

Reads the root `plugin.json` and exposes the bundled skill as `/agents-system-setup`. Generated Copilot CLI specialized subagents apply a [Standard Tool Profile](./plugins/agents-system-setup/skills/agents-system-setup/references/platforms.md#copilot-cli-standard-tool-profiles) by default — `tools: [vscode, execute, read, agent, edit, search, todo]` for edit-capable subagents, narrows to `[read, search]` for reviewers/auditors, and offers `runner` / `research` / `inherit` variants via interview Q9c. The orchestrator role lives in `AGENTS.md` (read by the host Copilot CLI session); no orchestrator subagent file is emitted.

### Claude Code

```
claude
> /plugin install ytthuan/agents-system-setup
> /agents-system-setup:agents-system-setup
```

Reads `.claude-plugin/plugin.json`. Skills are namespaced as `/<plugin>:<skill>`. Source: <https://docs.anthropic.com/en/docs/claude-code/plugins>.

### OpenAI Codex CLI install

```bash
codex plugin marketplace add ytthuan/agents-system-setup
codex
> /plugins        # browse and install agents-system-setup
> /skills         # list available skills from installed plugins
> $agents-system-setup   # invoke the bundled skill
```

Reads `.codex-plugin/plugin.json` and the marketplace descriptor at `.agents/plugins/marketplace.json`. Source: <https://developers.openai.com/codex/plugins/build>.

After installing via `/plugins`, invoke the bundled skill with `$agents-system-setup` in the Codex CLI prompt, or use `/skills` to list and select skills interactively.

Generated Codex project artifacts are compatible with **OpenAI Codex CLI + App** surfaces that load repo artifacts: `AGENTS.md` contains project memory plus the host-session **Orchestration Operating Model** (orchestrator role), `.codex/agents/*.toml` contains specialized subagents, and `.codex/config.toml` contains `[agents]` defaults. Plugin marketplace install and slash-command examples above are CLI-only; generated repo artifacts remain compatible with both CLI and App. No `.codex/agents/orchestrator.toml` is emitted (Codex has always followed this pattern; v1.3.0 normalizes Copilot/Claude/OpenCode/Gemini to it).

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

### Gemini CLI artifact support

Gemini CLI support is generated artifact support, not a plugin install. This repo does **not** publish or document a Gemini plugin installation command. Generate or copy Gemini artifacts into the target project, then run Gemini CLI normally:

```bash
# Project-local generated subagents
ls .gemini/agents/
gemini
```

Inside Gemini CLI, invoke generated subagents with Gemini's agent invocation syntax, for example `@<agent-name>`. Supported artifact shapes are project `.gemini/agents/*.md`, user `~/.gemini/agents/*.md`, and extension-bundled `agents/*.md` when packaging a Gemini extension yourself.

## Install a specific release

The commands above track the default branch and give you whatever is newest. To pin a released version — for reproducible setups, CI, or to stay on a known-good release — use the syntax below. Replace `v1.13.0` with the tag you want; see [releases](https://github.com/ytthuan/agents-system-setup/releases) and [CHANGELOG.md](./CHANGELOG.md).

Two things to know before picking a command:

- **Copilot CLI and Claude Code pin the *marketplace*, not the plugin.** Neither documents a per-plugin version selector, so you pin the Git ref of the marketplace source and install from it. In `plugin@marketplace` syntax the part after `@` is the **marketplace name** (`ytthuan`), not a version.
- **Pinning is not automatic updating.** A pinned marketplace stays on that ref until you re-add it at a newer one.

### GitHub Copilot CLI

```bash
copilot plugin marketplace add ytthuan/agents-system-setup#v1.13.0
copilot plugin install agents-system-setup@ytthuan
```

`marketplace add` accepts `owner/repo#ref`; the direct `plugin install owner/repo` form has no documented ref syntax. Source: <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference>.

Local-directory alternative, useful when you want the exact tree on disk:

```bash
git clone --depth 1 --branch v1.13.0 https://github.com/ytthuan/agents-system-setup.git
copilot plugin install ./agents-system-setup
```

### Claude Code

```text
/plugin marketplace add https://github.com/ytthuan/agents-system-setup.git#v1.13.0
/plugin install agents-system-setup@ytthuan
```

Appending `#<ref>` to a Git URL pins a branch or tag. Source: <https://code.claude.com/docs/en/plugin-marketplaces>.

### OpenAI Codex CLI

```bash
codex plugin marketplace add ytthuan/agents-system-setup --ref v1.13.0
codex
> /plugins        # install agents-system-setup from the pinned marketplace
```

Codex is the one runtime here with a documented per-marketplace `--ref` flag. Source: <https://developers.openai.com/codex/plugins/build>.

### OpenCode

OpenCode installs by clone-and-copy, so pin the clone:

```bash
git clone --depth 1 --branch v1.13.0 https://github.com/ytthuan/agents-system-setup.git
cd agents-system-setup
./scripts/install-opencode.sh project   # or "global"
```

### Gemini CLI

Gemini support here is artifact-based — this repo ships no `gemini-extension.json`, so `gemini extensions install` does **not** apply to it. Pin by cloning the tag, then generate or copy artifacts into your project:

```bash
git clone --depth 1 --branch v1.13.0 https://github.com/ytthuan/agents-system-setup.git
```

### Universal fallbacks

These work regardless of runtime plugin support:

```bash
# Clone at the tag (detached HEAD at that commit)
git clone --depth 1 --branch v1.13.0 https://github.com/ytthuan/agents-system-setup.git

# Move an existing clone to the tag
git fetch --tags && git checkout v1.13.0

# Release tarball published by the release workflow
gh release download v1.13.0 --repo ytthuan/agents-system-setup

# Or the plain source archive, no gh required
curl -fL -o agents-system-setup-v1.13.0.tar.gz \
  https://github.com/ytthuan/agents-system-setup/archive/refs/tags/v1.13.0.tar.gz
```

Every release ships a `agents-system-setup-<version>.tar.gz` plus a `.sha256` checksum. Verify before use:

```bash
shasum -a 256 -c agents-system-setup-1.13.0.tar.gz.sha256
```

Tags can in principle be moved; pin the commit SHA instead if you need a guarantee stronger than a tag.

### Check what you have installed

Every generated artifact carries a `<!-- agents-system-setup:generated-by: vX.Y.Z -->` stamp, and `.agents-system-setup/generated.json` records the authoritative manifest:

```bash
grep -r "agents-system-setup:generated-by" AGENTS.md
```

Upgrading a project generated by an older version is a first-class mode — run the skill and ask for `agents-system-setup upgrade`, which applies the per-version migration playbook rather than overwriting your files.

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

For Gemini CLI, there is no `/plugin install` or `/agents-system-setup` command documented by this repo. Use Gemini normally after generated `.gemini/agents/*.md` artifacts are present, then call the generated subagents with `@<agent-name>`.

## Wizard flow

The wizard starts by detecting the current repo, then shows a compact profile:
existing agent artifacts, recommended mode, inferred project type, and target
runtime defaults. For low-risk repos, you can accept detected/safe defaults for
non-gated setup questions. The wizard still asks explicitly for artifact
tracking, MCP/config approvals, plan approval, and security-sensitive writes.

Agent behavior choices are grouped together: optional model overrides, Copilot
CLI tool profile, output detail (`Balanced` by default), and Memory & Learning
profile. Model overrides are opt-in and scoped by all agents, role, or
exceptions so large rosters do not trigger one prompt per agent.

## Parallel subagents & Claude Code agent teams

The host CLI session orchestrator always fans out **parallel-safe subagents** in one wave (multiple `Task` calls in a single response), then awaits before the next wave. Parallel-safety is computed automatically from the Directory Architecture — see [parallelism reference](./plugins/agents-system-setup/skills/agents-system-setup/references/parallelism.md). Under the **GitHub Copilot app**, that same parallel-safety computation also identifies which units can become independent **child sessions / parallel PRs** (1 session per branch/PR) via `/orchestrate` — an advisory third primitive that portable generated files never depend on.

Dispatching a child is one half; **supervising it while it runs** is the other. Opt in with `advisory_supervision` (`off` by default) and the host adds a plan gate on children created in plan mode, steers only on premise invalidation by a sibling — polling is banned — and refuses to close a wave until every dispatched unit is `returned`, `reconciled-from-artifact`, or `explicitly-abandoned`, because no completion callback is documented and the branch/PR is the source of truth. It fails closed: if the app-only tools are absent from the host's surface the protocol is `n/a` rather than simulated. See [supervising a running child session](./plugins/agents-system-setup/skills/agents-system-setup/references/parallelism.md#supervising-a-running-child-session).

For Claude Code, when 3+ subagents are independent and would benefit from peer-to-peer challenge, the generator additionally emits `AGENT-TEAMS.md` with the opt-in env var (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`), settings snippet, suggested teammate roster, and a token-cost warning. Source: <https://docs.anthropic.com/en/docs/claude-code/agent-teams>.

## Context optimization

Generated output is **compact by default**. The skill asks for an output profile (`Balanced`, `Compact`, or `Full`) and records where long detail lives. `AGENTS.md` stays the routing and policy index; exhaustive marketplace research, long threat rationale, full ADR text, and platform schema detail are linked as references instead of repeated in every agent file.

Knowledge is placed by **how often it is actually needed**, since `AGENTS.md` is loaded in every host session and is the fallback a subagent opens when it needs a rule beyond its compact project-standard digest. Every-task knowledge — routing, ownership, gates — stays resident there. Project knowledge that only *some* tasks need (business rules, regulatory constraints, this repo's own coordination conventions) becomes a **`skill-kind: domain` skill**, which costs ~100 tokens to discover and loads its body only when its trigger matches. Those skills are derived from the project (purpose, domain classification, stack, ownership zones, existing docs/ADRs) and confirmed at the normal plan gate — never elicited by a blank "what skills do you want?" prompt — and must pass a four-part admission gate so the layer does not become a dumping ground. The plugin owns the scaffold; **you own the body, and `improve`/`upgrade` never overwrite it.** See the [placement rule](./plugins/agents-system-setup/skills/agents-system-setup/references/context-optimization.md#2a-placement-rule--where-a-piece-of-knowledge-goes).

## Local-only vs git-tracked agents

Before writing project-scoped agent files, the skill asks whether artifacts should be git-tracked, local-only, or personal/global. Local-only project artifacts are hidden through `.git/info/exclude` in the current checkout, not `.gitignore`, so team ignore rules are not changed accidentally.

## Why a plugin (not a bare skill)?

- A **skill** is the *unit of capability*.
- A **plugin** is the *distribution unit*.
- Wrapping the skill in plugin manifests for installable runtimes makes it one-line installable on Copilot CLI / Claude Code / Codex CLI, clone-and-copy installable on OpenCode, and able to generate artifact-only support for Gemini CLI.

## Repo layout

```
agents-system-setup/
├── plugin.json                  # Copilot CLI manifest
├── .claude-plugin/plugin.json   # Claude Code manifest
├── .codex-plugin/plugin.json    # Codex CLI plugin manifest
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

| Runtime | Plugin install | Artifact / skill format compatible | Parallel subagents | Agent teams |
|---|---|---|---|---|
| GitHub Copilot CLI | ✅ `/plugin install` | ✅ | ✅ | n/a |
| Claude Code | ✅ `/plugin install` | ✅ | ✅ | ✅ (opt-in env var) |
| OpenAI Codex (CLI + App artifacts) | ✅ CLI: `marketplace add` + `/plugins` | ✅ via `AGENTS.md` + `.codex/agents/*.toml` | ✅ | n/a |
| OpenCode | ⚠️ clone + script copy | ✅ | ✅ | n/a |
| Gemini CLI | ❌ no plugin install claimed | ✅ via `.gemini/agents/*.md` / extension `agents/*.md` artifacts | ✅ with non-recursive subagent use | n/a |

Cross-OS: Linux, macOS, Windows (native PowerShell + Git Bash + WSL).

**Gemini CLI note:** Gemini CLI now has official subagent docs; this repo documents it as supported artifact-first rather than candidate-only. Do not use or document a Gemini plugin install unless Gemini publishes compatible plugin-install semantics and this repo adds matching manifests.

## Design rationale

The procedure is intentional, not arbitrary. See [DESIGN.md](./DESIGN.md) for the reasoning behind every phase (why interview-first, why MCP gate, why Canonical IR, why per-item opt-in, why parallel-by-default).

## Contributing

PRs welcome. The skill is documented heavily in `plugins/agents-system-setup/skills/agents-system-setup/references/`. New marketplace sources go in `references/marketplaces.md` with a `[Tier · Vendor]` tag.

## License

MIT — see [LICENSE](./LICENSE).
