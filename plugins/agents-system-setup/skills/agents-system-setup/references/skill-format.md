# Skill Format (Agent Skills — multi-platform)

Source: https://docs.github.com/en/copilot/concepts/agents/about-agent-skills · open standard at https://github.com/agentskills/agentskills

Skills use the **same SKILL.md format across platforms** — only the *location* differs.

## Locations (per platform)

| Path | Platform | Scope |
|---|---|---|
| `.github/skills/<name>/SKILL.md` | Copilot CLI | Project |
| `.claude/skills/<name>/SKILL.md` | Claude Code | Project |
| `.opencode/skills/<name>/SKILL.md` | OpenCode | Project |
| `.gemini/skills/<name>/SKILL.md` | Gemini CLI | Project |
| `.agents/skills/<name>/SKILL.md` | Gemini CLI / Universal | Project |
| `~/.copilot/skills/<name>/SKILL.md` | Copilot CLI | Personal |
| `~/.claude/skills/<name>/SKILL.md` | Claude Code | Personal |
| `~/.gemini/skills/<name>/SKILL.md` | Gemini CLI | Personal |
| `~/.agents/skills/<name>/SKILL.md` | Universal fallback | Personal |

Folder name MUST equal `name` in frontmatter.

> When emitting to multiple platforms, write the **same** `SKILL.md` to each platform's path. Skills are portable.

## Activation & Invocation

| Platform | How model loads skill | How user invokes | Notes |
|---|---|---|---|
| Copilot CLI | Auto-loads when relevant (`disable-model-invocation: false`) | `/<name>` slash command when `user-invocable: true` | Default behavior |
| Claude Code | Auto-loads when relevant | `/<name>` slash command | Same frontmatter |
| OpenCode | Loaded on demand through the `skill` tool | No direct `/<name>` shortcut; use commands for slash UX | Gated by `permission.skill` |
| Gemini CLI | Model activates via skill loading/tooling | `/skills` to list/manage; no `/<name>` slash command | No direct per-skill slash command |
| Codex CLI | Model activates via skill loading | `$skill-name` selects a skill | `$` prefix is Codex-specific — not universal syntax |

> **Gemini note:** Gemini does not expose a `/<skill-name>` shortcut. Users browse available skills with `/skills` and the model applies them automatically. Do not document `/<name>` invocation for Gemini.
> **Codex note:** `$skill-name` is Codex's selection syntax. Do not use `$` as a cross-platform skill invocation pattern.

## Structure

```
.github/skills/<name>/
├── SKILL.md          # required, < 500 lines
├── references/       # docs loaded on demand
├── assets/           # templates / boilerplate
└── scripts/          # executable helpers
```

## Frontmatter

```yaml
---
name: <kebab-case-name>            # 1–64 chars, must match folder
description: 'What & when. Trigger keywords. Max 1024 chars.'
argument-hint: '[optional CLI hint]'
user-invocable: true               # default true → appears as /<name>
disable-model-invocation: false    # default false → auto-loadable
---
```

## Body Sections (recommended)

1. One-sentence mission
2. **When to Use** (triggers + use cases)
3. **Hard Rules** (invariants)
4. **Procedure** (numbered steps; reference `./scripts/*` and `./references/*`)
5. **Anti-patterns**
6. **Output Contract**

## Skill kinds

Every generated `SKILL.md` carries a kind marker on its own line so `improve` /
`upgrade` and `agents-doctor` can tell plugin-owned skills from project-owned ones:

```html
<!-- agents-system-setup:skill-kind: <kind> -->
```

| Kind | Owner | Body authored by | Upgrade behavior |
|---|---|---|---|
| `host-handoff`, `host-audit`, `host-doctor`, `sdlc-build-gate`, `code-quality` | plugin | plugin | Regenerated from the plugin's templates. |
| `domain` | project | **the user** | **Never overwritten.** Scaffold only; `improve`/`upgrade` may propose additions, never replace the body. |

`domain` skills hold project business rules, regulatory or compliance constraints,
and this repo's own coordination conventions — the knowledge that is specific to
*this* project and needed on *some* tasks. Which knowledge belongs there rather
than in `AGENTS.md` is decided by the placement rule in
[context optimization](./context-optimization.md#2a-placement-rule--where-a-piece-of-knowledge-goes).

### Admission gate for a `domain` skill

A candidate becomes a domain skill only when **all four** hold. Fail any one and
it stays in `AGENTS.md`, moves to an existing `host-*` skill, or is dropped:

1. **Project-specific** — not generic engineering craft (that is `code-quality`).
2. **Load-on-demand** — needed for *some* tasks, not every task.
3. **Stable trigger** — expressible as `USE FOR:` / `DO NOT USE FOR:` in the description.
4. **Not already covered** by a `host-*` skill or an `AGENTS.md` table.

Soft cap: roughly one domain skill per major ownership zone in the Directory
Architecture. More than that usually means `AGENTS.md` content was copied rather
than knowledge relocated — `instruction-memory-audit` treats a domain skill that
restates an `AGENTS.md` row as redundancy, not coverage.

## Progressive Loading

- Discovery: ~100 tokens (name + description)
- SKILL.md body loads when relevant
- `./references/*` and `./assets/*` load only when explicitly referenced

Keep SKILL.md focused. Push depth into `references/`.

## Anti-patterns

- Vague description ("helpful skill")
- Monolithic SKILL.md
- Folder/name mismatch
- Absolute paths instead of `./`
- Procedure without numbered steps
- **A `domain` skill that restates an `AGENTS.md` row** — that is double context cost, not relocation. Move the knowledge or leave it; never copy it.
- **Routing, ownership, or gates pushed into a `domain` skill** — they become invisible unless a trigger fires. Those stay in `AGENTS.md`.
- **Overwriting a user-authored `domain` skill body on upgrade** — the plugin owns the scaffold, the user owns the content.
- Writing the skill folder under `.agents-system-setup/skills/`. That directory is operational state only; runtimes do not load skills from it. Existing misroutes go through [misplaced-artifacts-migration](./misplaced-artifacts-migration.md).
