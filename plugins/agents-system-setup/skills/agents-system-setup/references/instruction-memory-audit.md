# Instruction Memory Audit

This audit keeps project memory useful across runtimes without turning every
memory file, subagent, and skill into the same long manual.

## Source-backed principles

- `AGENTS.md` is the canonical project memory: a README for agents with setup,
  tests, conventions, security notes, and routing policy.
- `CLAUDE.md` can import `AGENTS.md` with `@AGENTS.md`; new output uses a thin
  regular-file adapter, not an automatic symlink/copy. Existing adapters are
  evidence to inspect, never permission to overwrite custom content.
- Codex uses root `AGENTS.md` for project rules and `.codex/agents/*.toml` for
  specialized subagents. Custom Codex agents should be narrow and opinionated.
- OpenCode and Gemini use their own agent/config surfaces, but canonical
  project policy still points back to `AGENTS.md`.
- The complete synthesized root must be <=150 physical lines AND <=12,288
  UTF-8 bytes in every profile, including preserved user content. This is plugin
  policy, not an OpenAI token/line mandate; see [context optimization](./context-optimization.md).
- Reuse existing instructions before considering native initialization.
  Copilot's default filename is not mandatory; prefer the root request from
  [native initialization](./native-initialization.md), asking only on conflict
  or unsupported behavior.

Source anchors: `https://agents.md/`,
`https://docs.anthropic.com/en/docs/claude-code/memory`,
`https://developers.openai.com/codex/subagents`, and
`https://opencode.ai/docs/agents/`.

## Artifact classification

Classify before flagging anything as a conflict or duplicate.

| Class | Examples | Correct content | Audit behavior |
|---|---|---|---|
| Canonical project memory | `AGENTS.md` | Routing, ownership, security/audit gates, quality gates, build/test/lint, short runtime notes | Keep compact; link overflow detail. |
| Runtime adapter | `CLAUDE.md`, `GEMINI.md`, optional `.github/copilot-instructions.md` | Thin supported import/pointer; preserve approved provider-only overrides | Inspect eager loading, copies, symlinks and actual discovery; do not assume deduplication. |
| Specialized subagent | `.github/agents/*`, `.claude/agents/*`, `.opencode/agents/*`, `.codex/agents/*.toml`, `.gemini/agents/*` | Role, owned/read-only paths, intake, checklist, reporting, compact gates | Flag duplicated full policy or wrong runtime schema. |
| Skill workflow | `*/skills/<name>/SKILL.md` | Reusable multi-step workflow, scripts, assets, examples | Move long procedures here when reusable. |
| Project domain skill | `*/skills/<name>/SKILL.md` marked `<!-- agents-system-setup:skill-kind: domain -->` | Project business rules, regulatory constraints, this repo's coordination conventions — knowledge needed on *some* tasks | Body is **user-authored**: propose additions, never rewrite or overwrite. Flag `domain-skill-restatement` when it copies an `AGENTS.md` row, and flag routing/ownership/gates that were moved here instead of staying in `AGENTS.md`. |
| Path-scoped rule | `.claude/rules/**`, nested `AGENTS.md` where supported | Instructions only for one package, file type, or subsystem | Prefer over root memory for local conventions. |
| Deep reference | `docs/agents/**` or skill `references/**` | Long rationale, research, threat details, ADR text | Link from `AGENTS.md`; do not paste inline. |
| Operational ledger | `.agents-system-setup/*.jsonl`, `.agents-system-setup/generated.json` | Audit, migration, approval, learning events | Never Markdown inside runtime `agents/` directories. |

## Signals

Report these signals with file path, line/section, severity, evidence, and a
recommended delta:

| Signal | Meaning | Recommended delta |
|---|---|---|
| `direct-conflict` | Two active memory files give incompatible instructions. | Keep the canonical rule in `AGENTS.md`; move provider-only exception into the adapter. |
| `adapter-drift` | Active adapter copies stale policy, imports the wrong file, or ignores a configured context filename. | Propose a thin native adapter; retain custom overrides until approved. |
| `duplicate-policy` | Full workflow/governance prose is repeated. | Propose local relocation or a `task-delegation` pointer. Worker inline Required Minimum names, Acceptance Checklist, safety, and Reporting Template (including `Build gate:`) are intentional fail-closed minimums, not duplication to remove. |
| `memory-budget` | Complete root exceeds either hard limit, including unmanaged tail. | Propose compact synthesis and explicit local relocations; never truncate. |
| `eager-workflow-import` | An import loads full workflow libraries as always-on memory. | Keep only canonical imports; replace deep imports with concrete on-demand triggers. |
| `skill-discovery` | Declared skill is missing, mislocated, duplicated, denied, or uses stale active names. | Repair approved paths/consumers/permissions together; file existence alone is not loader evidence. |
| `skill-candidate` | Root memory contains a reusable multi-step workflow, prompt recipe, script, or template. | Move to a skill and leave a one-line invocation note. |
| `domain-skill-restatement` | A `skill-kind: domain` skill repeats knowledge that already has an `AGENTS.md` row, or holds routing / ownership / gates that must stay resident. | Restatement is double context cost, not relocation: delete the copy from the domain skill, or move the knowledge out of `AGENTS.md` — never both. Routing, ownership, and gates always return to `AGENTS.md`. Apply the [placement rule](./context-optimization.md#2a-placement-rule--where-a-piece-of-knowledge-goes). |
| `path-scoped-candidate` | Rule applies only to one package, file type, or subsystem. | Move to nested `AGENTS.md` or provider path-scoped rules where supported. |
| `stale-generated-block` | Generated stamp or manifest is older than current plugin behavior. | Apply version migration first, then re-run this audit. |
| `unsupported-runtime-field` | Runtime adapter or subagent contains another provider's schema. | Re-emit using the target runtime format. |
| `missing-overflow-link` | Detail was moved out but `AGENTS.md` does not link it. | Add a link in Context Loading Policy or the relevant section. |

## Improve / upgrade procedure

1. Inventory `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, nested `AGENTS.md`,
   `.github/agents/`, `.claude/agents/`, `.opencode/agents/`, `.codex/agents/`,
   `.gemini/agents/`, runtime skills, and `.agents-system-setup/generated.json`.
   Include `.github/copilot-instructions.md`, applicable `AGENTS.override.md`,
   configured context filenames and actual eager imports. Do not scan unrelated
   personal directories; mark unknown effective context unknown, not zero.
2. Classify each artifact with the table above before scoring.
3. In `upgrade` mode, classify version/stamp drift and known migration deltas
   before reporting policy conflicts. Do not treat expected legacy content as a
   user-authored conflict.
4. Score each finding: `blocker | high | medium | low`.
5. Use read-only doctor `--memory-only` for exact whole-file sizes and known
   structural/path findings. Semantic conflict and redundancy claims need
   reviewed evidence; do not pretend a parser understands arbitrary policy.
6. Propose deltas, grouped as `safe-managed-block`, `adapter-normalization`,
   `move-to-skill`, `move-to-path-rule`, `reference-link`, or `manual-review`.
   Show before/after sizes, retained rules, concrete local destinations, unresolved
   conflicts and a replacement diff. No unapproved user/domain-body changes.
7. Ask once per group before writes. Capture live preimages and non-overwriting
   backups, preserve user content, and stop for destination/symlink conflicts or
   concurrent edits. Record migrations in the existing JSONL ledger. Never
   restore stale backups over newer changes.
8. Re-read complete output and resolve required local skill/reference targets;
   rerun the same memory checker. Declined or incomplete repair stays
   nonconforming, not clean. Report:
   `Instruction memory audit: ok|warn|fail|n/a; signals=<list|none>; migrations=<count>`.

## Decision rules

- Keep in `AGENTS.md`: durable project facts, routing tables, ownership,
  security/audit boundaries, quality gates, build/test/lint commands, and links
  to overflow detail.
- Keep in runtime adapters: provider-specific memory loading notes, provider-only
  tool or question behavior, and a pointer/import to `AGENTS.md`.
- Move to skills: reusable workflows that have steps, arguments, scripts,
  examples, or assets.
- Move to path-scoped rules: instructions that only apply under one directory,
  package, framework, or file type.
- Move to references: long rationale, market research, standards mapping, threat
  details, ADR bodies, and examples that are not needed every session.
- Never move approval gates, ownership boundaries, or security-critical warnings
  so far away that `AGENTS.md` no longer links them.
