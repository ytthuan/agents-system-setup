# Misplaced Artifacts Migration

`.agents-system-setup/` is reserved for **operational state** —
`replication.jsonl`, MCP approval evidence, learning ledgers, `.bak`
files, this skill's own migration ledger. It is `.gitignore`d and **no
runtime loads agents, skills, hooks, commands, prompts, or plugin metadata
from it**, so anything placed there is silently inert.

This reference covers the detection and migration of all six runtime
artifact types when they are found under `.agents-system-setup/`.

## Detection signals

Phase 1 footprint inspection scans for any of:

- `.agents-system-setup/agents/**`
- `.agents-system-setup/skills/**`
- `.agents-system-setup/hooks/**`
- `.agents-system-setup/commands/**`
- `.agents-system-setup/prompts/**`
- `.agents-system-setup/plugins/**`

Each match is recorded as `{type, source_path, kind: file|dir, size,
mtime}`. The orchestrator never silently moves or deletes anything —
detection only feeds the per-artifact prompt below.

## Per-type, per-platform target mapping

The migration target depends on the artifact type and the runtime(s) the
user selected in Phase 0. Use this table as the canonical mapping:

| Artifact | Copilot CLI | Claude Code | OpenCode | OpenAI Codex | Gemini CLI | Notes |
|---|---|---|---|---|---|---|
| Agents | `.github/agents/<name>.agent.md` | `.claude/agents/<name>.md` | `.opencode/agents/<name>.md` | `.codex/agents/<name>.toml` | `.gemini/agents/<name>.md` | File-based |
| Skills | `.github/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` | `.opencode/skills/<name>/SKILL.md` | n/a — describe in `AGENTS.md` | `.gemini/skills/<name>/SKILL.md` | File-based folder |
| Hooks | `.github/hooks/*.json` | `.claude/settings.json` › `"hooks"` (config-embedded) | `.opencode/hooks/` | not supported | `.gemini/settings.json` › `"hooks"` (config-embedded) | Mixed |
| Commands | plugin `commands/<cmd>.md` under plugin root | `.claude/commands/<cmd>.md` | `.opencode/commands/<name>.md` | not a standard surface | extension-bundled `commands/*.md` only | File-based |
| Prompts | `.github/prompts/<name>.prompt.md` (VS Code Chat surface) | not standard | not standard | not standard | not standard | File-based |
| Plugins (marketplace) | `.agents/plugins/marketplace.json` | `.claude-plugin/marketplace.json` | OpenCode catalog config | `.codex-plugin/plugin.json` | extension manifest | File-based |

## Migration choices

For every detected artifact the orchestrator asks the user via `ask_user`.
Choices vary by `kind` (file-based vs config-embedded):

### File-based artifacts

- `Move (Recommended)` — back the source up to
  `.agents-system-setup/.bak/<ts>/<source-rel>`, copy to the platform
  target, verify the portable digest, then remove the original. The
  source directory is `.gitignore`d, so the only recovery path is the
  in-place backup; users are warned before the move.
- `Copy and keep original with deprecation marker` — copy to the
  platform target, then mark the source as deprecated using the
  source-type-safe rule below.
- `Leave with warning` — record the misplacement in `migration.jsonl`
  with `action: leave-with-warning` and add to the output contract.
- `Delete after explicit confirmation` — only after a second `ask_user`
  confirmation; the deletion still writes the in-place
  `.agents-system-setup/.bak/<ts>/<source-rel>` backup and records the
  source digest so the user can recover.

#### Deprecation marker rules (source-type-safe)

- Markdown / Text: append `<!-- DEPRECATED: moved to <target> -->` (or a
  trailing `# DEPRECATED: moved to <target>` for shell/INI).
- TOML: append `# DEPRECATED: moved to <target>` as a trailing comment.
- YAML: append `# DEPRECATED: moved to <target>` as a trailing comment.
- JSON: do **not** mutate the source (JSON has no comment syntax).
  Write a sibling sidecar
  `<source>.agents-system-setup.deprecated.json` containing
  `{"deprecated": true, "moved_to": "<target>", "ts": "<iso8601>"}`.
- Folder artifacts (skills, plugin marketplaces): write a top-level
  `DEPRECATED.md` inside the folder pointing at `<target>`. Do not
  mutate any individual file inside the folder.

### Config-embedded artifacts (Claude/Gemini hooks)

- `Convert manually (Recommended)` — render a copy-pasteable JSON snippet
  the user can merge into the target `settings.json`. The orchestrator
  must NOT auto-rewrite settings.json under any circumstance.
- `Leave with warning` — same as above.
- `Delete after explicit confirmation` — same as above.

> The "Move" choice never appears for config-embedded artifacts. Mixing
> the two would either silently lose hook bindings or auto-edit the user's
> personal settings.
>
> Hook safety warning: render this verbatim above every `Convert manually`
> snippet — *"This hook is currently inert. Pasting it into settings.json
> will enable execution. Review commands, env, and any referenced secrets
> before saving."*

## File-based migration procedure

For each accepted `Move`, `Copy + deprecate`, or `Delete`:

1. **Backup** — `mkdir -p .agents-system-setup/.bak/<ts>/$(dirname <source-rel>)`
   then copy source → backup with `cp -R -p`. The backup is non-destructive
   and survives the migration so users can roll back.
2. **Source digest** — compute the portable digest (see below).
3. **Target resolution** — use the table above and the multi-runtime rules
   in [Multi-runtime portability](#multi-runtime-portability). Confirm
   the target path(s) per artifact via `ask_user` when ambiguous.
4. **Copy** — `cp -p` for files, `cp -R -p` for folder artifacts.
5. **Target digest** — recompute the portable digest. On mismatch, abort
   the migration for that artifact, record `action: failed-verify`, leave
   the source in place, and surface the backup path.
6. **Finish** — for `Move`, `rm -rf` the source. For `Copy + deprecate`,
   apply the source-type-safe deprecation marker rule above. For
   `Delete after explicit confirmation`, `rm -rf` the source after the
   second confirmation; the backup remains.
7. **Ledger** — append one JSON object to `.agents-system-setup/migration.jsonl`.

### Portable digest (cross-environment safe)

A single canonical digest is required for both files and folders so source
and target compare equal regardless of parent path or `tar` flavor.

- **Files**: `sha256(file_bytes)`.
- **Folders**: build a sorted manifest with one line per regular file
  (`<relative-path-from-artifact-root> <sha256-of-bytes> <octal-mode-low-9-bits>`),
  newline-delimited, then `sha256` over the manifest text.
  - Walk the artifact root, sort entries by relative path (LC_ALL=C).
  - Skip platform metadata: `.DS_Store`, `Thumbs.db`, `.Spotlight-V100/`,
    `.Trashes/`, `__MACOSX/`, `*.bak`.
  - Use `octal mode & 0o777`; do not include uid/gid/mtime.
  - Symlinks: if pointing inside the artifact root, store the target
    path as `link:<rel-target>`; if pointing outside, abort and record
    `action: failed-verify` with `reason: external-symlink`.

Pseudocode:

```text
manifest_lines = []
for each regular file under artifact_root, sorted (C locale):
  rel = path.relative_to(artifact_root).as_posix()
  if rel matches skip-list: continue
  manifest_lines.append(f"{rel} {sha256(file)} {oct(mode & 0o777)}")
digest = sha256("\n".join(manifest_lines).encode("utf-8"))
```

## Multi-runtime portability

Different artifact types behave differently across runtimes:

- **Skills are portable.** When the user has multiple runtimes selected,
  default to `Copy to all selected supported runtimes` (one target per
  runtime that supports skills natively; Codex skills stay described in
  `AGENTS.md`). One ledger entry per target with the same `source` and
  shared `migration_id`.
- **Agents, hooks, commands, plugins, prompts are not portable.** Their
  schema differs per runtime. Ask the user via `ask_user` which target
  runtime to migrate to (one per artifact) and emit one ledger entry.

When a portable skill migration triggers, the orchestrator first asks:

> "Skill `<name>` is portable. Copy to **all** selected runtimes
> (`<list>`) or pick one runtime?"
> Choices: `["Copy to all (Recommended)", "Pick one runtime"]`

For `Copy to all`, repeat the digest verify per target and write one
ledger entry per `{source, target}` pair sharing a single
`migration_id`.

### Migration ledger schema

```json
{
  "ts": "2026-05-15T22:09:13Z",
  "migration_id": "<uuid|short-hash>",
  "type": "skill",
  "source": ".agents-system-setup/skills/code-reviewer/SKILL.md",
  "target": ".github/skills/code-reviewer/SKILL.md",
  "backup": ".agents-system-setup/.bak/2026-05-15T22-09-13Z/skills/code-reviewer/SKILL.md",
  "action": "move",
  "digest_alg": "portable-manifest-sha256",
  "digest_source": "<hex>",
  "digest_target": "<hex>",
  "evidence": "user-confirmed via ask_user 2026-05-15T22:09:09Z"
}
```

`action` is one of `move | copy-and-deprecate | leave-with-warning |
delete-after-confirm | convert-manually | failed-verify`. The legacy
`sha256_source` / `sha256_target` field names are retained as aliases
for ledger readers that still expect them.

The ledger lives at `.agents-system-setup/migration.jsonl`. It must
**never** be placed inside any `agents/`, `skills/`, `hooks/`,
`commands/`, `prompts/`, or `plugins/` directory — runtime loaders would
parse a `.md` form of it as a malformed agent. The same rule that applies
to `replication.jsonl` applies here.

## Wiring

- **Phase 1** (init/update/replicate): detection runs as part of the
  footprint inspection. If any artifact is misplaced, the orchestrator
  surfaces a summary and asks per artifact before any Phase 4 write.
- **Phase 1.5 — improve mode**: misplaced artifacts are first-class
  audit deltas alongside missing roles, missing security boundaries, etc.
  The user can apply, defer, or decline each one.
- **Update / replicate**: detection still runs. The orchestrator must not
  silently overwrite the misplaced artifact at the new platform target;
  the user is asked to migrate or skip first.

## Output contract reporting

The orchestrator reports one summary line per session:

```
Path migration: none
Path migration: moved=3 copied=1 skipped=2 manual=1 failed=0
```

Counts:

- `moved` — successful `move`.
- `copied` — successful `copy-and-deprecate`.
- `skipped` — `leave-with-warning`.
- `manual` — `convert-manually` snippet rendered (config-embedded).
- `failed` — `failed-verify` or aborted by the user mid-migration.

When no misplaced artifacts are detected, report `Path migration: none`.

## Anti-patterns

- Auto-rewriting Claude/Gemini `settings.json` to convert hooks. Always
  use the `Convert manually` snippet; the user owns those files.
- Skipping the SHA-256 verification step when copying.
- Writing the migration ledger as `.md` or inside any runtime artifact
  tree.
- Deleting the source before the target is verified.
- Treating multi-runtime ambiguity as an automatic decision; always ask
  the user which target path to use.
- Bundling all migrations into a single `Apply all` button — each
  artifact gets its own `ask_user` so users can defer or skip
  individually.
