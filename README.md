# agents-system-setup

A Copilot CLI plugin that bootstraps, updates, **improves**, or **replicates** a complete multi-agent system across **GitHub Copilot CLI**, **Claude Code**, **OpenCode**, and **OpenAI Codex CLI** — from a single skill, with a single Canonical IR for bidirectional replication.

> Bundles one skill: [`agents-system-setup`](./skills/agents-system-setup/SKILL.md).

## What you get

- **`AGENTS.md`** at repo root with Directory Architecture, Agent Roster, Capability Matrix.
- **Orchestrator + N subagents** (3–50, sized to scope) emitted in the right format for every selected runtime.
- **Project-scoped skills** under each runtime's conventional path.
- **Curated plugin / MCP recommendations** from vendor-official catalogs (`github/awesome-copilot`, `anthropics/skills`, `anthropics/claude-code`, `openai/codex`, `modelcontextprotocol/servers`) plus high-signal community awesome-lists — every recommendation tagged `[Tier · Vendor]` and opt-in per item.
- **MCP approval gate** — no MCP config is ever written without explicit user approval.
- **Cross-OS scripts** — `.sh` for POSIX, `.ps1` for native PowerShell, `.gitattributes` for line-ending safety.

## Modes

| Mode | When to use |
|---|---|
| `init` | Brand-new repo, no agent artifacts |
| `update` | Existing artifacts, regenerate managed blocks non-destructively |
| `improve` | Audit existing system → propose checklist of targeted fixes → opt-in apply |
| `replicate` | Port agents/skills/MCP from one runtime to another (Copilot ↔ Claude ↔ OpenCode ↔ Codex) via Canonical IR |

## Install

### Copilot CLI

```
copilot
> /plugin install ytthuan/agents-system-setup
> /agents-system-setup
```

### Claude Code

```bash
mkdir -p ~/.claude/skills && \
  cp -R skills/agents-system-setup ~/.claude/skills/
```

Then in Claude Code:

```
/skills agents-system-setup
```

### OpenCode

```bash
mkdir -p ~/.config/opencode/skills && \
  cp -R skills/agents-system-setup ~/.config/opencode/skills/
```

### Manual (any runtime that reads agents.md skills)

Drop the `skills/agents-system-setup/` folder into the runtime's skill search path.

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

## Why a plugin (not a bare skill)?

- A **skill** (`SKILL.md` + assets) is the *unit of capability*.
- A **plugin** is the *distribution unit* — a GitHub repo installable via `/plugin install owner/repo`.
- Wrapping the skill in a plugin manifest makes it one-line installable for Copilot CLI users while leaving the skill folder portable to Claude Code and OpenCode by simple copy.

## Design rationale

The procedure is intentional, not arbitrary. See [DESIGN.md](./DESIGN.md) for the reasoning behind every phase (why interview-first, why MCP gate, why Canonical IR, why per-item opt-in).

## Compatibility

| Runtime | Status |
|---|---|
| GitHub Copilot CLI | ✅ Primary target |
| Claude Code | ✅ Skill format compatible |
| OpenCode | ✅ Skill format compatible |
| OpenAI Codex CLI | ✅ Emits `AGENTS.md` headings; reads shared `.mcp.json` |

Cross-OS: Linux, macOS, Windows (native PowerShell + Git Bash + WSL).

## Contributing

PRs welcome. The skill is documented heavily in `skills/agents-system-setup/references/`. New marketplace sources go in `references/marketplaces.md` with a `[Tier · Vendor]` tag.

## License

MIT — see [LICENSE](./LICENSE).
