# Instruction Memory Audit

This audit keeps project memory useful across runtimes without turning every
memory file, subagent, and skill into the same long manual.

## Source-backed principles

- `AGENTS.md` is the canonical project memory: a README for agents with setup,
  tests, conventions, security notes, and routing policy.
- `CLAUDE.md` can import `AGENTS.md` with `@AGENTS.md`; use a symlink only where
  the OS and team workflow make that safe. Claude's project memory should stay
  concise; move multi-step procedures to skills or path-scoped rules.
- Codex uses root `AGENTS.md` for project rules and `.codex/agents/*.toml` for
  specialized subagents. Custom Codex agents should be narrow and opinionated.
- OpenCode and Gemini use their own agent/config surfaces, but canonical
  project policy still points back to `AGENTS.md`.

Source anchors: `https://agents.md/`,
`https://docs.anthropic.com/en/docs/claude-code/memory`,
`https://developers.openai.com/codex/subagents`, and
`https://opencode.ai/docs/agents/`.

## Artifact classification

Classify before flagging anything as a conflict or duplicate.

| Class | Examples | Correct content | Audit behavior |
|---|---|---|---|
| Canonical project memory | `AGENTS.md` | Routing, ownership, security/audit gates, quality gates, build/test/lint, short runtime notes | Keep compact; link overflow detail. |
| Runtime adapter | `CLAUDE.md`, `GEMINI.md` | Import, symlink, or compact pointer to `AGENTS.md` plus provider-specific overrides | Expected redundancy; flag only drift or contradiction. |
| Specialized subagent | `.github/agents/*`, `.claude/agents/*`, `.opencode/agents/*`, `.codex/agents/*.toml`, `.gemini/agents/*` | Role, owned/read-only paths, intake, checklist, reporting, compact gates | Flag duplicated full policy or wrong runtime schema. |
| Skill workflow | `*/skills/<name>/SKILL.md` | Reusable multi-step workflow, scripts, assets, examples | Move long procedures here when reusable. |
| Path-scoped rule | `.claude/rules/**`, nested `AGENTS.md` where supported | Instructions only for one package, file type, or subsystem | Prefer over root memory for local conventions. |
| Deep reference | `docs/agents/**` or skill `references/**` | Long rationale, research, threat details, ADR text | Link from `AGENTS.md`; do not paste inline. |
| Operational ledger | `.agents-system-setup/*.jsonl`, `.agents-system-setup/generated.json` | Audit, migration, approval, learning events | Never Markdown inside runtime `agents/` directories. |

## Signals

Report these signals with file path, line/section, severity, evidence, and a
recommended delta:

| Signal | Meaning | Recommended delta |
|---|---|---|
| `direct-conflict` | Two active memory files give incompatible instructions. | Keep the canonical rule in `AGENTS.md`; move provider-only exception into the adapter. |
| `adapter-drift` | `CLAUDE.md` / `GEMINI.md` is neither a pointer nor a marked generated copy and duplicates stale policy. | Convert to import/symlink/copy with provider-specific override block. |
| `duplicate-policy` | Full security, handoff, context, or quality policy is repeated in subagents or adapters. | Replace with a short pointer to `AGENTS.md` or the owning reference. **Expected exception:** subagent templates intentionally keep a compact **fail-closed inline minimum** (12 Required Minimum field names, Acceptance Checklist short form, Reporting Template skeleton including the `Build gate:` line) plus a one-line `task-handoff` source-of-truth pointer. That layering is the canonical structure since v1.5.0 and must not be flagged as `duplicate-policy`. Only full long-form policy duplication is. |
| `skill-candidate` | Root memory contains a reusable multi-step workflow, prompt recipe, script, or template. | Move to a skill and leave a one-line invocation note. |
| `path-scoped-candidate` | Rule applies only to one package, file type, or subsystem. | Move to nested `AGENTS.md` or provider path-scoped rules where supported. |
| `stale-generated-block` | Generated stamp or manifest is older than current plugin behavior. | Apply version migration first, then re-run this audit. |
| `unsupported-runtime-field` | Runtime adapter or subagent contains another provider's schema. | Re-emit using the target runtime format. |
| `missing-overflow-link` | Detail was moved out but `AGENTS.md` does not link it. | Add a link in Context Loading Policy or the relevant section. |

## Improve / upgrade procedure

1. Inventory `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, nested `AGENTS.md`,
   `.github/agents/`, `.claude/agents/`, `.opencode/agents/`, `.codex/agents/`,
   `.gemini/agents/`, runtime skills, and `.agents-system-setup/generated.json`.
2. Classify each artifact with the table above before scoring.
3. In `upgrade` mode, classify version/stamp drift and known migration deltas
   before reporting policy conflicts. Do not treat expected legacy content as a
   user-authored conflict.
4. Score each finding: `blocker | high | medium | low`.
5. Propose deltas, grouped as `safe-managed-block`, `adapter-normalization`,
   `move-to-skill`, `move-to-path-rule`, `reference-link`, or `manual-review`.
6. Ask once per group before writes. Back up each changed file, preserve
   user-authored content outside managed blocks, and record migrations in the
   existing operational ledger.
7. Re-read changed artifacts and report:
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
