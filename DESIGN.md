# Design Rationale

This document explains **why** each phase and hard rule of `agents-system-setup` exists. If you contribute, read this first — many constraints look arbitrary until you see what they prevent.

## Hard rules — reasoning

| Rule | Why it exists | What it prevents |
|---|---|---|
| 1. Always interview first | Project type / language / scope drive every later decision; assumptions silently produce wrong subagents | Generic "helper" agents with no discovery surface |
| 2. Detect existing footprint on entry | Users with an existing system mostly want **improve** or **replicate**, not a re-init that overwrites their work | Silent overwrite of `AGENTS.md` |
| 3. Orchestrator + subagent topology mandatory | Single-agent systems collapse into a god-prompt; subagent topology preserves context and enables tool restriction | Context-window exhaustion, runaway tool calls |
| 4. Directory Architecture enforced | Subagent boundaries must be machine-checkable for the orchestrator to route correctly | Two subagents fighting over the same files |
| 5. Per-item opt-in for recommendations | Plugins/MCP servers carry security and trust implications — bulk-applying is hostile | Supply-chain compromise via a single bad MCP server |
| 6. MCP approval gate | MCP servers run code on the user's machine and often hold credentials | Silent credential exfiltration; surprise network calls |
| 7. Marketplace-first lookup with vendor attribution | Provenance must be auditable | Users installing forks of forks; typosquatting |
| 8. Replication via Canonical IR (no pairwise mappings) | N runtimes × N targets = N² mappings; IR makes it N | Drift between mappings, dead code paths |
| 9. Non-destructive updates with `.bak` | Users edit generated files; we must preserve their work | Lost manual customizations |
| 10. Per-platform paths and frontmatter | Copilot frontmatter in a Claude file is silently ignored | Agents that look installed but never trigger |
| 11. Cross-OS aware | Plugin will be installed on Linux, macOS, Windows | `.sh` scripts on Windows, CRLF in bash files |
| 12. Git is opt-in | Some users scaffold inside an existing repo; auto-initing would corrupt history | Detached HEAD, lost commits |

## Phase-by-phase reasoning

### Phase 0 — Platform Selection (FIRST)

**Why first?** Every later decision (paths, frontmatter, script extension, MCP file format) depends on which runtimes are targeted. Asking later means re-doing work.

**Why a multi-select?** Many teams run two or more runtimes side-by-side; the plugin must handle that natively.

### Phase 1 — Detect & Choose Mode

**Why detect before asking mode?** A user typing "set up agents" in a repo with existing `.claude/agents/` almost never means "wipe and start over". Detection-driven defaults make the right thing the easy thing.

**Why offer `improve` as the default for healthy footprints?** The cheapest valuable action on a working system is targeted polish, not regeneration.

### Phase 1.5 — Improve / Replicate branch

**Why a separate branch?** Improve and replicate share none of the generation pipeline (Phases 2–4). They reuse only the write-side mechanics (Phase 5) and verification (Phase 7). Branching keeps the main path simple.

**Why score (ok/warn/fail) before proposing?** Without a numeric prior, every audit finding looks equally important. Scoring lets the user triage the checklist.

### Phase 2 — Plan (Directory Architecture, Roster, Matrix)

**Why a plan before any writes?** Generating files first and then asking for approval means rolling back filesystem changes on disagreement. The plan is the cheap cancellation point.

**Why these three artifacts specifically?**
- *Directory Architecture* — defines path ownership; the orchestrator's routing table.
- *Agent Roster* — the discovery surface; what each agent does, in one row.
- *Capability Matrix* — surfaces overlaps and gaps before they become bugs.

### Phase 3 — Marketplace Lookup with per-item opt-in

**Why a fixed tier order?** Vendor-official sources (Tier 1) are maintained by people whose job depends on them. Community awesome-lists (Tier 2) carry value but more variance. Random search (Tier 3) is a fallback only.

**Why max 3 candidates per capability?** More than 3 turns the question into a research task for the user and degrades opt-in quality.

**Why mandatory rationale fields?** A recommendation without `why_recommended` and `tradeoffs` is noise. Empty rationale ⇒ drop.

### Phase 3.5 — MCP Config Approval Gate

**Why a gate, not a confirmation?** A confirmation invites yes-fatigue. A gate that renders the actual JSON the user is approving forces a real decision.

**Why per-server selective option?** Bundles often contain servers a user wants and one they don't. Forcing all-or-nothing pushes users to "all", which loses the safety property.

### Phase 4 — Generate Artifacts (per platform, post-approval)

**Why post-approval?** Pre-approval generation means the disk gets dirty even if the user rejects MCP. Post-approval keeps the rejection lossless.

**Why one loop over selected platforms?** Avoids the temptation of platform-specific code paths that drift over time.

### Phase 5 — Update Mode (non-destructive)

**Why managed-block markers?** Without explicit `<!-- ...:managed:start -->` / `:end -->` markers, future updates can't tell user content from generated content, and either duplicate or destroy.

**Why `.bak` instead of git stash?** The plugin can't assume a clean working tree or even a git repo. `.bak` is universal.

### Phase 6 — Optional Git Init

**Why optional?** See hard rule #12. Auto-init in a non-git directory that's a subfolder of a parent repo creates a nested repo — a footgun.

**Why script per OS?** `git init` itself is portable, but the surrounding work (line-ending config, `.gitignore` selection) needs OS-aware logic.

### Phase 7 — Verify & Summarize

**Why re-read every generated file?** Frontmatter parse failures are silent on every runtime in scope. The verify pass is the last chance to catch them before the user runs the system and finds nothing triggers.

**Why "Try it" examples in the summary?** Reduces the activation cost from minutes to seconds.

## Replication design — reasoning

### Why a Canonical IR

Without IR, supporting N runtimes requires N×(N-1) pairwise mappings. With IR, it's 2N (parser + emitter per runtime). The economics flip the moment a fourth runtime appears.

### Why round-trip verify

A successful emit is necessary but not sufficient. Round-tripping (re-parse the emitted file back to IR, diff against source IR) is the only way to detect lossy mappings the user accepted-but-forgot.

### Why a replication ledger

Replicated files drift over time as either the source or target changes. The ledger (timestamp + sha256 per file) lets `improve` mode detect "this Claude agent was replicated from Copilot 60 days ago and the source has changed since".

### Why MCP gate re-runs per new target

MCP approval is per-target, not global. Approving a server for Copilot CLI tells us nothing about whether the user wants the same server inside Claude Code or OpenCode (different credential scopes, different blast radius).

## Anti-patterns and why we ban them

- **Single monolithic agent** — kills tool-restriction and context-isolation benefits; everything funnels into one prompt.
- **Generic descriptions** ("helps with code") — orchestrator never picks the agent.
- **Bulk MCP install** — supply-chain risk concentrated into a single yes-click.
- **Pairwise replication code** — N² maintenance burden.
- **Symlink CLAUDE.md on Windows** — silently replaced with text-stub copies by Git for Windows.
- **Backslash paths in Markdown** — render wrong on macOS/Linux, render right but break on Windows when copy-pasted.
- **Skipping `.gitattributes`** — `.sh` files arrive with CRLF on Windows clones, fail with `bad interpreter`.
- **Inventing plugin/MCP names** — exact opposite of provenance.

## Open questions / future work

- Hooks portability — Copilot CLI uses `.github/hooks/*.json`, Claude uses `.claude/settings.json` › `hooks`, OpenCode uses `.opencode/hooks/`. Round-trip is non-trivial; today the IR doesn't model hooks.
- Plugin-of-plugins — should this skill be able to install other plugins it recommends? Currently it surfaces install commands only.
- LSP server discovery — Copilot CLI plugins can ship LSP configs; not yet covered.
