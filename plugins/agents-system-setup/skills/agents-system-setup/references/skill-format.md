# Skill Format (Agent Skills — multi-platform)

Source: https://docs.github.com/en/copilot/concepts/agents/about-agent-skills · open standard at https://github.com/agentskills/agentskills

Skills use the **same SKILL.md format across platforms** — only the *location* differs.

## Locations (per platform)

| Path | Platform | Scope |
|---|---|---|
| `.github/skills/<name>/SKILL.md` | Copilot CLI | Project |
| `.claude/skills/<name>/SKILL.md` | Claude Code | Project |
| `.opencode/skills/<name>/SKILL.md` | OpenCode | Project |
| `~/.copilot/skills/<name>/SKILL.md` | Copilot CLI | Personal |
| `~/.claude/skills/<name>/SKILL.md` | Claude Code | Personal |
| `~/.agents/skills/<name>/SKILL.md` | Universal fallback | Personal |

Folder name MUST equal `name` in frontmatter.

> When emitting to multiple platforms, write the **same** `SKILL.md` to each platform's path. Skills are portable.

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
