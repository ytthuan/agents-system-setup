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

The orchestrator should pass subagents enough context to act without dumping the full project memory:

```text
Task: <one sentence>
Owned paths: <paths from Directory Architecture>
Relevant gates: <quality/security gates>
Constraints: <security/architecture constraints>
Expected output: <files changed, evidence, risks>
```

Do not include unrelated agent roster, marketplace research, or platform format notes unless the subagent needs them.

## 7. Anti-patterns

- Treating `<details>` blocks as context optimization; models still read the text.
- Moving security/audit/architecture gates into a file that `AGENTS.md` does not link.
- Repeating the same policy paragraph in every subagent.
- Generating full marketplace research inline when only one candidate was selected.
- Hiding lossy replication drops to save space.
