# Design Rationale

This document explains **why** each phase and hard rule of `agents-system-setup` exists. If you contribute, read this first — many constraints look arbitrary until you see what they prevent.

Public runtime support spans **Copilot CLI**, **Claude Code**, **OpenCode**, **OpenAI Codex (CLI + App)**, and **Gemini CLI** artifact layouts. Plugin installation is documented only for runtimes with supported plugin/install surfaces; Gemini CLI remains artifact-first.

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
| 13. Parallelism is mandatory where independent | Agent teams should use the user's available concurrency safely | Sequential bottlenecks and hidden shared-path conflicts |
| 14. Spec-Kit recommendation for software projects | Spec-driven development is valuable but should remain opt-in | Silent tool installs or missed high-value workflow setup |
| 15. Security/audit/architecture governance baseline | Agent systems can change code, config, tools, and release paths; ownership and evidence must be explicit | Unsafe MCP/tool writes, secrets leakage, unauditable changes, architecture drift |
| 16. Security-sensitive writes require evidence | Risky changes need proof, not just a success-shaped summary | "Done" reports with no build/test/security/audit trail |
| 17. Evidence-based improve mode | Audits should prioritize real findings with sources and severity | Cosmetic rewrites that miss security, architecture, or supply-chain risk |
| 18. Context budget is a feature | Generated agent systems become less useful when every file repeats every rule | Prompt bloat, missed routing facts, expensive/noisy subagent delegation |
| 19. Artifact tracking is explicit | Agent systems may be team infrastructure or personal local memory; the write behavior must match user intent | Accidentally committing private prompts, or hiding team-owned agent files |
| 20. Plan handoff normalized before emission | Planning prompts and slash commands have their own metadata, not runtime agent schemas | Copying `agent: Plan`, Spec-Kit metadata, or Copilot frontmatter into Claude/OpenCode/Codex artifacts |
| 21. Runtime drift is source-backed and gated | Upstream agent runtimes change formats independently; support claims must match implemented emitters and validators | Advertising candidate runtimes too early, switching formats on docs ambiguity, stale schema guidance |

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

### Phase 1.6 — Artifact Scope & Tracking

**Why ask before writing?** `AGENTS.md`, subagents, skills, and MCP config can be either team-owned project infrastructure or personal local working memory. Asking first prevents a private local setup from being committed accidentally.

**Why `.git/info/exclude` for local-only project files?** It is local to the checkout. Updating `.gitignore` would change team behavior and can hide files other contributors expect to review.

### Phase 1.8 — Security, Audit, Architecture Intake

**Why before planning?** Security and architecture are not add-ons; they affect topology, tool permissions, MCP approval, owned paths, and verification. Asking after generation would produce the wrong agents.

**Why source-backed?** OWASP GenAI, NIST SSDF, MCP Security Best Practices, GitHub Code Security, SLSA, OPA, Azure Well-Architected, C4, and TOGAF each cover different parts of the risk model. The skill uses them as references, not as automatic installs.

### Phase 1.9 — Output Profile & Context Budget

**Why ask this explicitly?** Some users want exhaustive onboarding docs; others want the shortest useful agent memory. The default `Balanced` profile keeps routing, ownership, security/audit, architecture, and quality gates inline while moving long rationale into references.

**Why not use collapsible Markdown?** Models still receive the text. Real context optimization means shorter inline text plus explicit load-on-demand references.

### Phase 2 — Plan (Directory Architecture, Roster, Matrix, Governance)

**Why a plan before any writes?** Generating files first and then asking for approval means rolling back filesystem changes on disagreement. The plan is the cheap cancellation point.

**Why these three artifacts specifically?**
- *Directory Architecture* — defines path ownership; the orchestrator's routing table.
- *Agent Roster* — the discovery surface; what each agent does, in one row.
- *Capability Matrix* — surfaces overlaps and gaps before they become bugs.
- *Security & Audit Matrix* — assigns risky controls to owners with evidence.
- *Threat Model* — records assets, trust boundaries, threats, and mitigations.
- *Architecture / Design Pattern Matrix* — documents pattern decisions, alternatives, guardrails, and ADR refs.
- *Quality Gates* — defines what proof is required before agents can claim completion.
- *Context Loading Policy* — tells agents what to read first and what to load only when needed.
- *Plan Handoff Contract* — turns upstream planning output into a compact HandoffIR before any platform-specific artifact is emitted, including Codex shared artifacts that work across CLI + App surfaces and Gemini CLI agent artifacts.

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

**Why Gemini is artifact-first?** Gemini CLI has documented agent artifact paths, but this repo does not claim a Gemini plugin installation path. Treating Gemini as artifact support keeps public install docs honest while still letting generated `.gemini/agents/*.md` or extension `agents/*.md` files participate in the same planning, governance, and verification flow.

### Phase 5 — Update Mode (non-destructive)

**Why managed-block markers?** Without explicit `<!-- ...:managed:start -->` / `:end -->` markers, future updates can't tell user content from generated content, and either duplicate or destroy.

**Why `.bak` instead of git stash?** The plugin can't assume a clean working tree or even a git repo. `.bak` is universal.

### Phase 6 — Optional Git Init

**Why optional?** See hard rule #12. Auto-init in a non-git directory that's a subfolder of a parent repo creates a nested repo — a footgun.

**Why script per OS?** `git init` itself is portable, but the surrounding work (line-ending config, `.gitignore` selection) needs OS-aware logic.

### Phase 7 — Verify & Summarize

**Why re-read every generated file?** Frontmatter parse failures are silent on every runtime in scope. The verify pass is the last chance to catch them before the user runs the system and finds nothing triggers.

**Why "Try it" examples in the summary?** Reduces the activation cost from minutes to seconds.

**Why verify governance sections?** Missing frontmatter breaks discovery, but missing security/architecture sections is just as harmful: agents may still run while ignoring the riskiest boundaries.

**Why verify context policy?** A generated system can pass schema checks while still being too noisy to use. The verify pass confirms the output profile and overflow references are visible.

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
- **Treating security/architecture as wrap-up only** — too late to affect topology, permissions, or quality gates.
- **Security auditor with broad write access** — review roles should be read-mostly unless a scoped remediation is explicitly approved.
- **Pattern names without rationale** — "use clean architecture" is not an architecture decision unless alternatives, risks, and boundaries are recorded.
- **Using verbosity as safety** — repeated long policy prose hides the actual routing and quality gates.
- **Assuming generated agents should be committed** — always ask artifact tracking first; use `.git/info/exclude` for local-only project artifacts.
- **Copying planner metadata into agent files** — plan prompts are input surfaces; generated files must use each target runtime's native schema.

## Open questions / future work

- Hooks portability — Copilot CLI uses `.github/hooks/*.json`, Claude uses `.claude/settings.json` › `hooks`, OpenCode uses `.opencode/hooks/`. Round-trip is non-trivial; today the IR doesn't model hooks.
- Plugin-of-plugins — should this skill be able to install other plugins it recommends? Currently it surfaces install commands only.
- LSP server discovery — Copilot CLI plugins can ship LSP configs; not yet covered.
- Codex App capability detection — generated repo artifacts are CLI + App compatible where Codex surfaces load them, but plugin installation remains CLI-documented until OpenAI publishes App plugin-install semantics.
- Gemini CLI plugin distribution — artifact generation is supported; plugin or extension install documentation should wait for explicit Gemini install semantics plus matching manifests and validators.
