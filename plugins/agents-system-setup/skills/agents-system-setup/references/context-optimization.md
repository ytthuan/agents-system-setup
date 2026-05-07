# Context Optimization

Generated agent systems should be clear enough to route safely and compact enough to stay useful in long sessions. Optimize by **summarizing inline, linking details on demand**, and preserving all hard gates.

## 1. Output profiles

Ask once during setup and record the answer in the plan.

| Profile | Default? | Use when | Inline detail level |
|---|---:|---|---|
| `Balanced` | yes | Most projects | Keep routing, ownership, security/audit, architecture decisions, and quality gates inline; cap examples and long candidate lists. |
| `Compact` | no | Small repos, expert teams, tight context windows | Keep only non-negotiable rules, owners, gates, and links. Move most rationale and overflow rows to reference files. |
| `Full` | no | Audits, onboarding docs, regulated projects | Include full matrices and rationale inline when the user explicitly asks. |

If the user is unsure, choose `Balanced`.

## 2. Generated-output hierarchy

| Artifact | Purpose | Context rule |
|---|---|---|
| `AGENTS.md` | Canonical routing and policy index | One-screen "Read First"; compact matrices; link overflow details. |
| Runtime agent files | Role-specific execution instructions | Include role, owned/read-only paths, triggers, security boundary, output contract. Avoid repeating full project policy. |
| Requirements triage output | Intake brief before planning | Keep inline in the plan as a compact scope/risk/routing seed; do not duplicate full repo memory. |
| Content quality review | Anti-slop signal check before final output | Keep only status/signals inline; link `content-quality.md` for taxonomy and fixes. |
| Memory & learning files | Durable lessons and Learning Index | Load the index first; load detailed entries only when category/path/runtime matches the task. |
| Reference files | Deep detail | Load only when task needs that domain or when the user asks for full detail. |
| Plans / summaries | Temporary task state | Lead with outcome, keep evidence concise, link or name files for detail. |

Never move mandatory gates out of sight. If details overflow, `AGENTS.md` must say where they went.

## 3. Context budgets

Budgets are guidance unless a validator explicitly enforces them.

| Surface | Target | Hard rule |
|---|---:|---|
| Skill frontmatter description | Trigger-rich and under ~900 chars | Must include what/when, not long procedure. |
| `SKILL.md` body | About 250 lines | Must stay under 500 lines. Move depth to `references/`. |
| Generated `AGENTS.md` | Top policy readable in one screen | Must include routing, ownership, security/audit, architecture, and quality gates. |
| Subagent file | Under ~80 lines | Must not duplicate full `AGENTS.md` policy. |
| Final response | 1-2 short paragraphs or compact table | Include validation/evidence only when useful or requested. |

## 4. Inline vs reference split

Keep inline:
- Project snapshot.
- Golden rules.
- Directory Architecture summary.
- Agent roster.
- Capability matrix summary.
- Security & Audit Matrix summary.
- Threat Model top risks.
- Architecture decisions with ADR refs.
- Quality gates.
- Runtime "try it" commands.
- Plan Handoff Contract summary.
- Requirements triage status and latest intake evidence.
- Content-quality status, curator mode, and signals.
- Memory & Learning System summary, including Learning Check and memory owner.

Move or link when large:
- Full marketplace candidate research.
- Full OWASP / SSDF / SLSA rationale.
- Long threat lists.
- Full ADR text.
- Long subagent examples.
- Full platform schema details.

Recommended overflow paths:
- `docs/agents/security-audit.md`
- `docs/agents/architecture-decisions.md`
- `docs/agents/plugin-recommendations.md`
- `docs/agents/runtime-formats.md`

Only create docs files after the normal write approval path. Otherwise keep overflow as "recommended file plan" rows.

## 5. Clear generated writing style

Use these defaults in generated content:

1. Outcome or rule first.
2. Prefer tables for routing, ownership, gates, and decisions.
3. One sentence per table cell where possible.
4. No duplicate hard-rule prose across `AGENTS.md` and every subagent.
5. Use "read this first" / "load when needed" language.
6. Use explicit `n/a — <reason>` instead of omitting mandatory sections.
7. Cap recommendations at 3 unless the user asks for "show more".

## 6. Concise delegation packets

The orchestrator should pass subagents enough context to act without dumping the full project memory. **The canonical Delegation Packet schema lives in [`handoff.md`](./handoff.md#delegation-packet-canonical-schema).** Every orchestrator template and runtime renderer fills the same fields in the same order; do not redefine the schema here.

When updating field semantics or adding a field, edit `handoff.md` first, then re-link from this section.

## Context freshness rule

Agents in the same turn should not re-read every `AGENTS.md` row when the orchestrator already loaded it. Use the `Context freshness` field of the canonical Delegation Packet:

| Freshness value | Meaning | Subagent behavior |
|---|---|---|
| `AGENTS.md@<sha>` | Orchestrator computed sha during this turn | Trust the snapshot; reload only sections relevant to the new task tag. |
| `recent` | Same orchestrator turn, no sha available | Skip row-by-row reload; load only Task-Type Routing rows for the current task tag. |
| `reload` | Stale or unknown | Re-read `AGENTS.md` Read First plus rows for the task tag. |

Orchestrators must set this field whenever they know `AGENTS.md` is fresh; subagents must respect it. Replication and update flows revert to `reload`.

## Task-Type Routing Map

Map common task tags to the references each agent should load (or skip), and to the **Recommended Packet Form** for the Task Assignment Contract (see [`handoff.md`](./handoff.md#recommended-packet-form)). Agents look up their task tag here before reading anything beyond `AGENTS.md` Read First.

| Task tag | Always load | Load when applicable | Safe to skip | Recommended packet form |
|---|---|---|---|---|
| `read-only-research` | `AGENTS.md` Read First, Directory Architecture | `topology.md` if topology questions | Security & Audit Matrix detail, Threat Model long rationale, MCP gate | short-form |
| `requirements-triage` | `AGENTS.md` Read First, Directory Architecture, Human Input / Question Protocol | `topology.md`, platform/runtime refs, Security & Audit rows, prior plan only when relevant | Source files outside requested scope, full marketplace research | short-form intake brief |
| `content-quality-review` | `AGENTS.md` Read First, Content Quality / Anti-Slop Review, Directory Architecture | `content-quality.md`, `output-contract.md`, `handoff.md`, runtime refs for generated artifacts | Source implementation files unrelated to generated prose | short-form quality signals |
| `code-edit` | `AGENTS.md` Read First, Directory Architecture, owning agent boundary | Quality Gates row for this path | Marketplace research, full platform schemas | short-form (≤2 files) · full-form when >2 files or shared boundary |
| `security-write` | Security & Audit Matrix, Threat Model, owning agent boundary | `security-audit-architecture.md` rows for the change | Long marketplace candidate research | full-form |
| `mcp-write` | MCP approval gate (Phase 3.5), Security & Audit Matrix | `plugin-discovery.md` MCP rendering | Architecture Decisions detail | full-form |
| `replication` | `replication.md`, `handoff.md`, `output-contract.md` | `models.md` for explicit overrides | Project-specific quality gate detail | full-form |
| `release` | Quality Gates, manifests, version sync rules | `runtime-updates.md` for upstream drift | Long architecture rationale | full-form |
| `docs-only` | `AGENTS.md` Read First | Quality Gates only if doc CI exists | Security/MCP gates unless docs touch credentials | short-form |
| `bug-fix` | `AGENTS.md` Read First, Directory Architecture, owning agent boundary | Quality Gates row, repro logs, related ADRs | Long marketplace research | full-form (Reproduction block required) |
| `learning-check` | `AGENTS.md` Memory & Learning System, Learning Index | `learning-memory.md` for update/supersede policy | Full operational ledger, unrelated learnings | short-form |

The map is guidance, not a hard schema. Agents may load more references when the task warrants it; they must not skip load rows that include a hard gate, and they must not downgrade the recommended form for security/MCP/release tasks.

## Compact mode trimming

Output profile (Phase 1.9) controls subagent body verbosity. The frontmatter and section anchors stay intact; only body prose is trimmed.

| Section | Compact | Balanced (default) | Full |
|---|---|---|---|
| Context Load Order | Single bulleted line referencing `AGENTS.md` rows | Numbered list (current default) | Numbered list plus rationale |
| Security & Audit Boundaries | One line + link to the matching `AGENTS.md` row | Current expanded list | Expanded list plus evidence template |
| Architecture & Design Expectations | One line + link to the matching ADR row | Current expanded list | Expanded list plus rejected alternatives |
| Outputs | One sentence | Current bullet list | Bullet list plus example output |
| Memory & Learning System | Profile + owner + link | Current compact section | Section plus schema example |

Renderers must keep section headings (so validators and humans can find them) and keep the link target valid. Codex TOML `developer_instructions` follows the "summary + pointer" rule from [agent-format](./agent-format.md#codex-toml-summary--pointer-rule) regardless of profile because TOML cannot link inline.

## 7. Anti-patterns

- Treating `<details>` blocks as context optimization; models still read the text.
- Moving security/audit/architecture gates into a file that `AGENTS.md` does not link.
- Repeating the same policy paragraph in every subagent.
- Adding anti-slop bloat instead of a compact `Content quality` status and linked signal taxonomy.
- Generating full marketplace research inline when only one candidate was selected.
- Hiding lossy replication drops to save space.
- Loading the full learning ledger for every task instead of the Learning Index and matching entries.
