---
name: agents-system-setup
description: 'Bootstrap, update, IMPROVE, or REPLICATE a multi-agent system across GitHub Copilot CLI, Claude Code, OpenCode, and OpenAI Codex CLI — generates AGENTS.md (with Directory Architecture, Agent Roster, Capability Matrix), an orchestrator + N subagents, project-scoped skills, and approved plugin/MCP recommendations sourced from vendor-official catalogs (github/awesome-copilot, anthropics/skills, anthropics/claude-code, openai/codex, modelcontextprotocol/servers) plus high-signal community awesome-lists. Detects existing agent systems on entry and offers to improve them. Bidirectional replication (Copilot ↔ Claude ↔ OpenCode ↔ Codex) goes through a single Canonical IR — no pairwise rewrites. Cross-OS aware (Linux/macOS/Windows). Per-item opt-in recommendations with rationale; mandatory MCP approval gate. USE FOR: "set up agents", "scaffold AGENTS.md", "init agents system", "improve my agents", "audit agent setup", "port agents from copilot to claude code", "replicate agents", "configure copilot/claude/opencode/codex for this repo", "discover plugins/MCP servers". DO NOT USE FOR: editing a single existing agent file (edit directly), unrelated coding work, MCP server implementation. INVOKES: ask_user (interview, per-recommendation choice, MCP approval, replication source/targets), web_fetch/github-search (marketplace lookup), bash or pwsh (git init, mkdir, symlink/copy), file create/edit tools.'
argument-hint: '[init | update | improve | replicate] (omit to auto-detect)'
---

# Setup Copilot Agents (multi-platform)

Scaffold or update a complete agent system for the current project across **Copilot CLI**, **Claude Code**, and/or **OpenCode**. Produces a canonical `AGENTS.md` (with **Directory Architecture**, **Agent Roster**, **Capability Matrix**), an **orchestrator + N subagents**, project-scoped **skills**, and **approved** plugins/MCP servers — derived from a structured interview.

## When to Use

- Brand-new repository needs an agent setup from scratch (**init**)
- Existing project should adopt or extend the orchestrator + subagent pattern (**update**)
- Existing agent system needs an audit and targeted upgrades (**improve**)
- Agents authored for one runtime need to be ported to another (**replicate** — Copilot ↔ Claude Code ↔ OpenCode ↔ Codex CLI)
- Discovering relevant plugins / MCP servers from the well-known marketplaces

## Hard Rules

1. **Always interview first** with `ask_user`. Never assume project type, language, scope, or target platform.
2. **Detect existing agent footprint on entry.** If any of `AGENTS.md`, `CLAUDE.md`, `opencode.json`, `.github/agents/`, `.claude/agents/`, `.opencode/agents/`, `~/.codex/AGENTS.md` exists, present mode choice with `improve` and `replicate` as first-class options — never silently jump to `update`.
3. **Orchestrator + subagent topology is mandatory.** Subagent count (3 to ~50) is decided dynamically from scope.
4. **Directory Architecture is generated and enforced.** Every subagent file references it; the orchestrator routes by ownership.
5. **Per-item opt-in recommendations.** Plugin / skill / MCP candidates are always presented with rationale and explicit `ask_user` choice — never bulk-applied silently.
6. **MCP config approval gate.** Before writing any MCP config (`.mcp.json`, `opencode.json` › `mcp`, agent `mcp-servers:`), render the proposal and call `ask_user` for approval. No silent MCP writes — ever. Replication re-triggers this gate per new target.
7. **Marketplace-first lookup with vendor attribution.** Recommendations come from registries listed in [marketplaces](./references/marketplaces.md), tagged `[Tier · Vendor]` — never invent names or URLs.
8. **Replication goes through Canonical IR, not pairwise mappings.** See [replication](./references/replication.md). Never write a Copilot→Claude (or any other direction) function; always parse → IR → emit.
9. **Non-destructive updates.** `cp <file> <file>.bak` before any edit; merge into managed blocks, preserve user-authored content.
10. **Multi-platform aware.** Emit per-platform paths and frontmatter per [platforms](./references/platforms.md). Never write Copilot frontmatter into a Claude file.
11. **Cross-OS aware.** Detect host OS once (Linux / macOS / Windows-bash / Windows-pwsh) per [cross-platform](./references/cross-platform.md). Pick `.sh` for POSIX shells, `.ps1` for native PowerShell. Forward slashes in generated docs. Never symlink on Windows. Bundle `.gitattributes` so line endings stay correct on every clone.
12. **Git is optional and gated by `ask_user`.**

## Procedure

### Phase 0 — Platform Selection

First question after detecting cwd. Use `ask_user`:

> "Which agent runtime(s) should I configure?"
> Choices: `["Copilot CLI only (Recommended for GitHub-centric teams)", "Claude Code only", "OpenCode only", "OpenAI Codex CLI only", "Copilot CLI + Claude Code", "All four (Copilot + Claude Code + OpenCode + Codex)"]`

Persist the selection. All later phases loop over selected platforms using [platforms.md](./references/platforms.md) as the source of truth for paths and frontmatter.

### Phase 1 — Detect & Choose Mode

1. **Inspect cwd** and detect runtime footprint:
   - Project files: `package.json`, `*.csproj`, `Package.swift`, `build.gradle`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `mkdocs.yml`, `.git/`.
   - Agent artifacts (per runtime):
     - Copilot CLI: `AGENTS.md`, `.github/agents/`, `.github/skills/`, `.mcp.json`
     - Claude Code: `CLAUDE.md`, `.claude/agents/`, `.claude/skills/`, `.claude/settings.json`
     - OpenCode: `opencode.json`, `.opencode/agents/`, `.opencode/skills/`
     - Codex CLI: top-level `## <Name>` headings in `AGENTS.md`, `~/.codex/AGENTS.md`
2. **Decide mode** with `ask_user` — show what was detected:

   | Detected footprint | Default offer | Choices |
   |---|---|---|
   | Nothing | `init` | `["Init (Recommended)", "Cancel"]` |
   | One runtime, looks healthy | `improve` | `["Improve current setup (Recommended)", "Update (regenerate managed blocks)", "Replicate to another runtime", "Init alongside (additive)"]` |
   | One runtime, gaps | `update` | `["Update (Recommended)", "Improve (audit + targeted fixes)", "Replicate to another runtime"]` |
   | Two+ runtimes | `improve` | `["Improve current setup (Recommended)", "Replicate / sync between runtimes", "Update one runtime"]` |

3. Run the interview — see [interview script](./references/interview.md). One question per `ask_user` call. Skip questions already answered by detection (project type, framework). For `improve`/`replicate`, jump straight to Phase 1.5.

### Phase 1.5 — Improve / Replicate branch

If the user picked **improve** → run the [improve procedure](./references/replication.md#4-improve-mode-audit--targeted-upgrade) (audit → score → propose deltas → opt-in apply). Skip Phases 2–4; jump to Phase 5 mechanics for backups + write.

If the user picked **replicate** → run the [replication procedure](./references/replication.md#3-replication-procedure):
1. `ask_user` for **source** runtime (single-select among detected).
2. `ask_user` for **target** runtimes (multi-select; source excluded).
3. Parse source → AgentIR / SkillIR / MCPServerIR records.
4. Render lossiness report; `ask_user` to approve dropped fields per target.
5. Re-run **Phase 3.5** MCP approval gate against each new target.
6. Emit per target with `<!-- agents-system-setup:replicated-from: <source> -->` markers.
7. Write replication ledger (`agent-replication.log`).
8. Verify round-trip (re-parse emitted → diff IR → surface drift).

For both branches, finish with Phase 7 (verify & summarize).

### Phase 2 — Plan (Directory Architecture, Roster, Matrix)

Build the plan and show it before writing anything. The plan must include:

- **Directory Architecture** — table of `path glob | purpose | owner agent | edit rule`. Derived from project type + frameworks. Always covers: source dirs, tests, docs, infra, agent files, generated artifacts.
- **Agent Roster** — table of `name | role | owns | triggers | model (optional)`. Use [topology guide](./references/topology.md). Model column populated only where user provided overrides.
- **Capability Matrix** — capabilities × agents grid (✅ / 🟡).
- Skills to create.
- Plugin/MCP candidates **per capability** (Phase 3 fills this).
- Per-platform file plan (Copilot/Claude/OpenCode paths the user will actually get).
- Git actions (if any).

End the phase with `ask_user`: `["Proceed", "Edit plan first"]`.

### Phase 3 — Marketplace Lookup with per-item Opt-in

For every capability the user named (e.g., "playwright", "azure", "postgres"):

1. **Search** the marketplaces in tier order — see [marketplaces](./references/marketplaces.md). Tier 1 first; only fall through if it misses.
2. Collect **at most 3 candidates per capability**. For each, populate **mandatory rationale fields**: `name`, `source_tier`, `repo_url`, `bundles` (agents/skills/hooks/MCP/LSP), `why_recommended`, `tradeoffs`, `install_command_per_platform`. Empty rationale ⇒ drop the candidate.
3. Render a **comparison table** to the user, then call `ask_user`:
   > "For capability **<x>**, which would you like?"
   > Choices: `["<candidate 1 — short label>", "<candidate 2>", "<candidate 3>", "Show more (Tier-3 fallback search)", "None — skip this capability"]`
4. **Show more** triggers Tier-3 search (capped at +5 additional candidates). Re-render table and re-prompt.
5. Record the user's pick. Skipped capabilities never reach the MCP gate or final write.

See [plugin discovery](./references/plugin-discovery.md) for the comparison-table format and rationale schema.

### Phase 3.5 — MCP Config Approval Gate (mandatory, downstream of Phase 3)

If any user-selected candidate from Phase 3 includes an MCP server:

1. Build the proposed config **per platform**:
   - Copilot CLI / Claude Code → `.mcp.json` (`mcpServers` key)
   - OpenCode → merge into `opencode.json` (`mcp` key)
2. Render each proposed file verbatim (full JSON).
3. `ask_user`:
   > "I'm about to write the MCP configuration above to `<paths>`. Approve?"
   > Choices: `["Approve all (Recommended)", "Approve selectively (per-server)", "Skip MCP entirely"]`
4. If **selective**, loop per server: `["Include", "Skip"]`.
5. If **skip**, strip every `mcp-servers:` from generated agents and do not write `.mcp.json` / `opencode.json` `mcp` key.
6. **No MCP write may occur before this gate returns approval.**

### Phase 4 — Generate Artifacts (per platform, post-approval)

For each selected platform, look up paths and frontmatter in [platforms.md](./references/platforms.md), then render:

- `AGENTS.md` at repo root → [template](./assets/AGENTS.md.template). Fill **Directory Architecture**, **Agent Roster**, **Capability Matrix**, **Skills**, **Plugins/MCP** tables.
- Orchestrator → [template](./assets/orchestrator.agent.md.template) at the platform's agents path.
- Each subagent → [template](./assets/subagent.agent.md.template) at the platform's agents path. Fill `{{OWNED_PATHS}}` / `{{READONLY_PATHS}}` from the Directory Architecture.
- Each skill → [template](./assets/skill.template.md) at the platform's skills path.
- MCP config (only if Phase 3.5 approved) at the platform's MCP path.
- Drop the [directory-architecture snippet](./assets/directory-architecture.snippet.md) into any agent missing the boundary block.

**Project-memory linking** (after AGENTS.md is written):
- If both Claude Code and another platform are selected → pick by detected OS (see [cross-platform](./references/cross-platform.md)):
  - **macOS / Linux / WSL**: `bash ./scripts/link-project-memory.sh` → symlinks `CLAUDE.md → AGENTS.md`.
  - **Windows native**: `pwsh -File ./scripts/link-project-memory.ps1` → tries symlink (Developer Mode/admin), falls back to copy with regenerable header (re-runs keep them in sync).
- OpenCode reads `AGENTS.md` natively — no linking required.

**Frontmatter rules** (silent-failure traps):
- `name` MUST match filename basename (kebab-case).
- Quote any `description` containing colons.
- Subagent `description` MUST start with `"Use when..."`.
- Use the **right frontmatter schema per platform** (see [platforms.md](./references/platforms.md) — Copilot uses `mcp-servers:`, Claude uses comma-string `tools:`, OpenCode uses `mode:` and bool-keyed `tools:` map).
- Restrict tools per subagent to the minimum needed.
- The `model:` line is optional in every platform — emit only if the user specified an override.

### Phase 5 — Update Mode (non-destructive)

For every existing target file:
1. `cp <file> <file>.bak` via bash before any edit.
2. Parse existing frontmatter; preserve user-authored sections.
3. Merge new content under `<!-- agents-system-setup:managed:start -->` … `<!-- agents-system-setup:managed:end -->` markers — replace the block, never duplicate.
4. Print a diff summary at the end.

### Phase 6 — Optional Git Init

Only if user confirmed in Phase 1 AND no `.git/` exists. Pick the script that matches the host OS — see [cross-platform](./references/cross-platform.md):

```bash
# macOS / Linux / Git Bash / WSL
bash ./scripts/git-init.sh
```

```powershell
# Windows native PowerShell (PowerShell 7+ recommended)
pwsh -File ./scripts/git-init.ps1
# or, on stock Windows PowerShell 5.1:
powershell.exe -ExecutionPolicy Bypass -File ./scripts/git-init.ps1
```

Both forms initialize `main`, write a stack-aware `.gitignore` (covering `.github/`, `.claude/`, `.opencode/` local state, `.DS_Store`, `Thumbs.db`, `desktop.ini`), drop a `.gitattributes` for line endings, stage, and commit.

### Phase 7 — Verify & Summarize

1. List every file created/modified with absolute paths, grouped by platform.
2. Re-read each generated agent/skill: confirm `name` matches filename, `description` present, no unquoted colons, frontmatter parses for the *target platform's* schema.
3. Verify `AGENTS.md` contains non-empty **Directory Architecture**, **Agent Roster**, **Capability Matrix**.
4. Print "Try it" examples per selected platform (`copilot`, `claude`, `opencode`).
5. Suggest 2–3 next customizations.

## Decision Aids

- **How many subagents?** [topology guide](./references/topology.md). One subagent per durable concern — also a path owner in the Directory Architecture.
- **Skill vs Subagent?** Reusable workflow with assets → Skill. Context isolation / different tool restrictions → Subagent.
- **Plugin vs MCP?** Plugins extend the runtime; MCP servers expose tools to agents. External-system integrations are usually MCP.
- **Which platform?** Copilot CLI for GitHub-tight teams; Claude Code for Anthropic-first; OpenCode for vendor-neutral / self-hosted; Codex CLI for OpenAI-first / `AGENTS.md`-only setups. Multi-target if uncertain — files coexist cleanly via shared `AGENTS.md` + `.mcp.json`.
- **`update` vs `improve` vs `replicate`?**
  - `update` regenerates managed blocks against the current plan (still asks before writing).
  - `improve` audits the existing system and proposes a checklist of targeted fixes — user picks which to apply.
  - `replicate` ports an existing system from one runtime to others using the [Canonical IR](./references/replication.md#1-canonical-ir).

## Anti-patterns

- Writing files before showing the plan.
- Writing MCP config without explicit `ask_user` approval.
- Bulk-applying recommendations without per-item rationale + choice.
- Mixing platform frontmatters (e.g., Copilot keys in a Claude agent file).
- **Pairwise replication code** (Copilot→Claude function, Claude→OpenCode function, …) — always go through the [Canonical IR](./references/replication.md).
- Replicating without re-triggering the MCP approval gate for the new target(s).
- Symlinking `CLAUDE.md` on Windows (use the `.ps1` fallback-copy path).
- Backslashes in generated Markdown paths — always forward slashes.
- Skipping `.gitattributes` — Windows users get CRLF in `*.sh` and break execution.
- Single monolithic agent (violates orchestrator + subagent rule).
- Overwriting existing `AGENTS.md` / `opencode.json` without `.bak`.
- Generic descriptions ("helps with code") — kills discovery.
- Inventing plugin/skill/MCP names. Always cite `[Tier · Vendor]` from [marketplaces](./references/marketplaces.md).
- Treating Codex CLI as a per-agent-file runtime (it isn't — agents live as `## <Name>` headings inside `AGENTS.md`).

## Output Contract

```
✅ Mode: <init|update|improve|replicate>
✅ Platforms: <copilot-cli, claude-code, opencode, codex-cli>
✅ Detected footprint: <list of pre-existing artifacts, or "none">
✅ Files created: <count>     (per platform: <breakdown>)
✅ Files updated (with .bak): <count>
✅ Subagents: <list>
✅ Skills: <list>
✅ Plugins selected: <list with [Tier · Vendor] and /plugin install (or platform-equivalent)>
✅ Plugins skipped: <list>
✅ MCP servers: <selected list> (approval: <approve-all | selective | skipped>)
✅ Project memory link: <symlink | copy | n/a>
✅ Git: <initialized | left untouched | already present>

# replicate mode adds:
✅ Source runtime: <copilot-cli | claude-code | opencode | codex-cli>
✅ Target runtimes: <list>
✅ Lossy field drops: <list per target>
✅ Round-trip verify: <pass | drift on <fields>>
✅ Replication ledger: <path>

# improve mode adds:
✅ Audit findings: <ok / warn / fail counts>
✅ Deltas applied: <count>
✅ Deltas skipped: <count>
✅ Requires-human: <count>

Try it:
  copilot          # then: "@orchestrator <task>"
  claude           # then: invoke a subagent
  opencode         # then: pick an agent
  codex            # then: reference an AGENTS.md heading

Suggested next customizations:
  - <suggestion 1>
  - <suggestion 2>
```
