---
name: spec-kit
description: When and how to recommend GitHub Spec-Kit alongside a generated agent system.
---

# GitHub Spec-Kit (companion, not replacement)

[GitHub Spec-Kit](https://github.com/github/spec-kit) is a Spec-Driven Development toolkit. It installs four slash-commands into the user's coding agent: `/specify`, `/plan`, `/tasks`, `/implement`. The flow is **intent → specification → executable plan → atomic tasks → code**.

## When to recommend (Hard Rule #14)

Recommend **only** when the project is software-development. The detection heuristic lives in `SKILL.md` Phase 1.7 and matches a keyword set (`app, api, library, sdk, cli, framework, …`) or source-language signals (`package.json`, `go.mod`, `pyproject.toml`, `Cargo.toml`, `Package.swift`, etc.).

Do **not** recommend for: marketing-content systems, research/analysis agents, data-pipeline orchestration, customer-support bots, or any non-dev domain.

## Position vs. the agent system we scaffold

| Layer | Tool | Owns |
|---|---|---|
| **What to build** | Spec-Kit | Specs, plans, atomic tasks |
| **Who builds it** | agents-system-setup | Orchestrator + parallel subagents that execute the tasks |

They compose. Spec-Kit's `/tasks` output feeds the orchestrator's wave planner. Never frame them as competing.

## Install commands per runtime

Spec-Kit ships an installer that takes an `--ai` flag — values map 1:1 to the four runtimes we already target:

| Runtime | Init command |
|---|---|
| Copilot CLI | `specify init --here --ai copilot` |
| Claude Code | `specify init --here --ai claude` |
| Codex CLI | `specify init --here --ai codex` |
| OpenCode | `specify init --here --ai opencode` |

Bootstrap (one-time, host-wide):

```bash
# Requires uv (https://docs.astral.sh/uv/). If absent:
#   curl -LsSf https://astral.sh/uv/install.sh | sh   (POSIX)
#   irm https://astral.sh/uv/install.ps1 | iex        (Windows)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

Then `cd` into the project and run `specify init --here --ai <runtime>`.

## What the orchestrator should know about it

When Phase 1.7 records "spec-kit installed = yes", the emitted orchestrator prompt (`AGENTS.md` / `CLAUDE.md` / runtime equivalent) should add a managed block:

> ### Spec-Driven Workflow (via Spec-Kit)
> Before fanning out to subagents, drive intent through Spec-Kit:
> 1. `/specify` — capture what the user wants in their own words.
> 2. `/plan` — turn it into a checked plan with constraints.
> 3. `/tasks` — break the plan into atomic, parallel-safe tasks.
> 4. Hand each task to the matching subagent per the Capability Matrix.
> 5. `/implement` only after the orchestrator has greenlit the wave.

This belongs in the managed block (`<!-- agents-system-setup:managed:start -->`), not user-authored content, so future updates can refresh it without trampling user edits.

## Anti-patterns

- Auto-running `specify init` without explicit user consent.
- Recommending Spec-Kit for non-dev domains (marketing, research, ops content).
- Treating Spec-Kit as a replacement for the agent topology — it does not run subagents.
- Writing both `/plan` (Spec-Kit) and the orchestrator's wave planner without explaining the handoff.
