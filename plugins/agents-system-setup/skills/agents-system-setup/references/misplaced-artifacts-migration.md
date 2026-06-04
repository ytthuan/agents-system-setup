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
| Skills | `.github/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` | `.opencode/skills/<name>/SKILL.md` (loaded via `skill` tool, gated by `permission.skill`) | `.codex/skills/<name>/SKILL.md` (project) or `~/.codex/skills/<name>/SKILL.md` (user); activates via Codex skill loader | `.gemini/skills/<name>/SKILL.md` | File-based folder |
| Hooks | `.github/hooks/*.json` | `.claude/settings.json` › `"hooks"` (config-embedded) | `.opencode/hooks/` | not supported | `.gemini/settings.json` › `"hooks"` (config-embedded) | Mixed |
| Commands | plugin `commands/<cmd>.md` under plugin root | `.claude/commands/<cmd>.md` | `.opencode/commands/<name>.md` | not a standard surface | extension-bundled `commands/*.md` only | File-based |
| Prompts | `.github/prompts/<name>.prompt.md` (VS Code Chat surface) | not standard | not standard | not standard | not standard | File-based |
| Plugins (marketplace) | `.agents/plugins/marketplace.json` | `.claude-plugin/marketplace.json` | OpenCode catalog config | `.codex-plugin/plugin.json` | extension manifest | File-based |

## Migration choices

For every detected artifact the orchestrator asks the user via `ask_user`.
Choices vary by `kind` (file-based vs config-embedded):

### File-based artifacts

- `Move (Recommended)` — back the source up to
  `.agents-system-setup/.bak/<ts>-<migration_id>/<source-rel>` (see
  [Backup directory naming](#backup-directory-naming)), copy to the
  platform target, verify the portable digest, then remove the original.
  The source directory is `.gitignore`d, so the only recovery path is the
  in-place backup; users are warned before the move.
- `Copy and keep original with deprecation marker` — copy to the
  platform target, then mark the source as deprecated using the
  source-type-safe rule below.
- `Leave with warning` — record the misplacement in `migration.jsonl`
  with `action: leave-with-warning` and add to the output contract.
- `Delete after explicit confirmation` — only after a second `ask_user`
  confirmation; the deletion still writes the in-place
  `.agents-system-setup/.bak/<ts>-<migration_id>/<source-rel>` backup
  and records the source digest so the user can recover.

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

1. **Backup** — resolve the backup path per
   [Backup directory naming](#backup-directory-naming), then `mkdir`
   the leaf directory exclusively (no `-p` for the leaf; retry with a
   fresh `migration_id` on `EEXIST`). Copy source → backup with
   `cp -R -p`. The backup is non-destructive and survives the migration
   so users can roll back.
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
- **Folders**: build a sorted manifest with one line per entry, then
  `sha256` over the manifest text.
  - Walk the artifact root with `followlinks=False` (do not descend into
    symlinked directories) and sort entries by relative path under
    `LC_ALL=C`.
  - Track visited inodes (`(st_dev, st_ino)`) to break cycles defensively
    even though `followlinks=False` already prevents directory loops; if
    an inode repeats, abort with `reason: digest-loop`.
  - Skip platform metadata: `.DS_Store`, `Thumbs.db`, `.Spotlight-V100/`,
    `.Trashes/`, `__MACOSX/`, `*.bak`.
  - **Regular file line:**
    `<relative-path-from-artifact-root> <sha256-of-bytes> <octal-mode-low-9-bits>`.
  - **Symlink line:**
    `<relative-path-from-artifact-root> link:<rel-target> <octal-mode-low-9-bits>`.
    `<rel-target>` is the symlink target as stored on disk; resolve it
    relative to the artifact root and abort with
    `reason: external-symlink` when the resolved path leaves the
    artifact root.
  - Use `octal mode & 0o777`; do not include uid/gid/mtime.

Pseudocode:

```text
manifest_lines = []
visited_inodes = set()
for path in walk(artifact_root, followlinks=False, sorted_C_locale=True):
  rel = path.relative_to(artifact_root).as_posix()
  if rel matches skip-list: continue
  st = path.lstat()
  ino_key = (st.st_dev, st.st_ino)
  if ino_key in visited_inodes: abort(reason="digest-loop")
  visited_inodes.add(ino_key)
  mode = oct(st.st_mode & 0o777)
  if path.is_symlink():
    target = readlink(path)
    resolved = (path.parent / target).resolve()
    if not resolved.is_relative_to(artifact_root): abort(reason="external-symlink")
    rel_target = resolved.relative_to(artifact_root).as_posix()
    manifest_lines.append(f"{rel} link:{rel_target} {mode}")
  elif path.is_file():
    manifest_lines.append(f"{rel} {sha256(path.read_bytes())} {mode}")
  # directories contribute nothing themselves; their entries are walked
digest = sha256("\n".join(manifest_lines).encode("utf-8"))
```

### Backup directory naming

The backup path is
`.agents-system-setup/.bak/<ts>-<migration_id>/<source-rel>` where:

- `<ts>` — filesystem-safe ISO-8601 UTC timestamp at second precision,
  e.g. `2026-05-15T22-09-13Z` (colons replaced with `-`).
- `<migration_id>` — short collision-resistant id; recommended
  implementation is the first 8 characters of `base32(uuid4())` (lower
  case, no padding), e.g. `bxa4zk6q`.
- The leaf directory `<ts>-<migration_id>` is created exclusively (no
  `-p` for the leaf — `mkdir` without parents-or-recreate). On
  `EEXIST`, regenerate `<migration_id>` and retry up to three times
  before aborting with `reason: backup-collision`. The intermediate
  `.agents-system-setup/.bak/` directory is created with `-p` if
  missing, since it is shared.

## Multi-runtime portability

Different artifact types behave differently across runtimes:

- **Skills are portable.** When the user has multiple runtimes selected,
  default to `Copy to all selected supported runtimes` (one target per
  runtime that supports skills natively, including Codex which loads
  `.codex/skills/<name>/SKILL.md`). One ledger entry per target with the
  same `source` and shared `migration_id`.
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

## Deprecated orchestrator subagent files

As of v1.3.0 the plugin no longer emits an `orchestrator` subagent file for
any runtime. The Orchestration Operating Model lives in `AGENTS.md`
and is read by the host CLI session. When improve/update detects an
existing orchestrator subagent file, surface it as a first-class migration
delta (similar to misplaced artifacts) before any Phase 5 write.

### Detection signals

Phase 1 footprint inspection scans for any of:

- `.github/agents/orchestrator.agent.md` (Copilot CLI)
- `.github/agents/orchestrator.md` (Copilot CLI docs-drift)
- `.claude/agents/orchestrator.md` (Claude Code)
- `.opencode/agents/orchestrator.md` (OpenCode — note `permission.task` migration)
- `.codex/agents/orchestrator.toml` (Codex — should never exist, but detect)
- `.gemini/agents/orchestrator.md` (Gemini CLI)

Each match is recorded as `{path, runtime, size, mtime, has_custom_content}`.
`has_custom_content` is `true` when the file's content meaningfully deviates
from the v1.2.0 (now-deleted) orchestrator subagent baseline (heuristic: > 8 lines of body
prose outside the managed block, or any sections not in the template).

### Migration choices (per detected file)

For every detected orchestrator subagent file the host orchestrator asks the
user via the provider-native human-input surface:

> "Found `<path>` (`<runtime>`). The Orchestration Operating Model now lives
> in `AGENTS.md` (v1.3.0). How should I handle this file?"
> Choices:
> 1. `Back up and delete (Recommended)`
> 2. `Keep but mark deprecated`
> 3. `Back up + report custom additions for manual review`
> 4. `Skip`

#### 1. Back up and delete

1. Back the source up to
   `.agents-system-setup/.bak/<ts>-<migration_id>/orchestrator-deprecation/<source-rel>`
   per the [Backup directory naming](#backup-directory-naming) rule.
2. Compute the portable digest.
3. `rm` the source.
4. For OpenCode: render the `permission.task` rules that were in the deleted
   file as a suggested `opencode.json` › `agent.<root>.permission.task` block
   in the output contract. **Do not auto-write** `opencode.json` here —
   the user reviews and merges it under the existing approval gate.
5. Append `{action: "orchestrator-deprecation-deleted", ...}` to
   `.agents-system-setup/migration.jsonl`.

#### 2. Keep but mark deprecated

1. Apply the source-type-safe deprecation marker rule:
   - Markdown files: append `<!-- DEPRECATED: orchestration moved into AGENTS.md › Orchestration Operating Model (v1.3.0). This file may be safely deleted. -->`.
   - TOML files: append `# DEPRECATED: orchestration moved into AGENTS.md › Orchestration Operating Model (v1.3.0). This file may be safely deleted.`.
2. Append `{action: "orchestrator-deprecation-marked", ...}` to
   `.agents-system-setup/migration.jsonl`.

#### 3. Back up + report custom additions for manual review

This is the safe choice when `has_custom_content` is true.

1. Back up the source as in choice 1.
2. Compute the diff between the source and the closest v1.2.0 orchestrator
   template baseline (Copilot/Claude/OpenCode). Render a concise diff (or
   the full source body if the diff is large) in the output contract under
   `Custom orchestrator content to review:` so the user can manually move
   the custom additions into `AGENTS.md` › Orchestration Operating Model.
3. Append `<!-- DEPRECATED: see Custom orchestrator content in output contract for manual migration. -->` to the source.
4. Append `{action: "orchestrator-deprecation-reviewed", custom_summary: "<diff_or_body_len>", ...}` to
   `.agents-system-setup/migration.jsonl`.
5. **Never auto-merge** custom prose into `AGENTS.md`; user owns the merge.

#### 4. Skip

1. Append `{action: "orchestrator-deprecation-skipped", ...}` to
   `.agents-system-setup/migration.jsonl`.
2. Surface a warning in the output contract: "Deprecated orchestrator
   subagent file `<path>` left in place. Future replication / improve runs
   will re-prompt."

### OpenCode `permission.task` migration

When deleting `.opencode/agents/orchestrator.md`, **first parse and extract**
the existing `permission.task` frontmatter from the source file. Preserve
the user's customizations (specific allows, `ask` overrides, named roster
entries) and render them into the proposed `opencode.json` snippet —
**never replace user customizations with the generic template** unless
the source has no parseable `permission.task` block at all.

Render the extracted snippet (or fall through to the template below when
no source block exists) for the user to review under a **separate
OpenCode config approval gate** (not the MCP approval gate; the MCP gate
is reserved for MCP servers). Ask once before writing; on decline, record
`opencode_task_gate: declined` and report degraded-mode warning in the
output contract.

Generic template (used only when no source `permission.task` exists):

```jsonc
{
  "agent": {
    "<root-agent-name>": {
      "permission": {
        "task": {
          "*": "deny",
          "<allowed-subagent-1>": "allow",
          "<allowed-subagent-2>": "allow"
        }
      }
    }
  }
}
```

Render the snippet under the separate OpenCode config approval gate
(verbatim, with the `agents-system-setup:permission-task-approved`
marker). Treat as a config write requiring user confirmation; no silent
merge into `opencode.json`. If the source contained unparseable or
unsafe entries (e.g., `"*": "allow"`), flag them for manual review and
do NOT include them in the proposed snippet.

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
- **Auto-deleting an orchestrator subagent file with custom content.**
  Default to `Back up + report custom additions for manual review` when
  `has_custom_content` is true; never auto-merge custom prose into
  `AGENTS.md`.
- **Auto-writing `opencode.json` › `agent.<root>.permission.task` during
  orchestrator-deprecation migration.** Render the snippet under the
  separate OpenCode config approval gate and ask before writing.
- **Replacing user customizations in the OpenCode `permission.task`
  block** with the generic template. Parse the source `permission.task`
  first; preserve allows, asks, and named entries unless they are
  unsafe (e.g., wildcard `allow`).

## Version Stamp Detection & Migration Playbook

Every artifact emitted by this plugin carries a `generated-by` stamp so
`improve` mode can detect stale content and apply per-version migrations
without guessing.

### Stamp format

| Artifact | Stamp surface | Example |
|---|---|---|
| `AGENTS.md` | HTML comment after `<!-- agents-system-setup:managed:start -->` | `<!-- agents-system-setup:generated-by: v1.4.0 -->` |
| `.github/agents/*.agent.md` | HTML comment after platform marker | `<!-- agents-system-setup:generated-by: v1.4.0 -->` |
| `.claude/agents/*.md` | HTML comment after platform marker | `<!-- agents-system-setup:generated-by: v1.4.0 -->` |
| `.opencode/agents/*.md` | HTML comment after platform marker | `<!-- agents-system-setup:generated-by: v1.4.0 -->` |
| `.gemini/agents/*.md` | HTML comment after platform marker | `<!-- agents-system-setup:generated-by: v1.4.0 -->` |
| `.codex/agents/*.toml` | TOML `#` comment in header block | `# agents-system-setup:generated-by: v1.4.0` |
| Skills (`*/skills/*/SKILL.md`) | HTML comment after frontmatter | `<!-- agents-system-setup:generated-by: v1.4.0 -->` |

A second optional marker `agents-system-setup:generated-at: <ISO-8601>` records when
the artifact was emitted. Both markers are substituted by the renderer from
`plugin.json` (`{{PLUGIN_VERSION}}` → `version` field; `{{GENERATED_AT}}` →
emission timestamp).

### Central manifest `.agents-system-setup/generated.json`

Authoritative source-of-truth in case per-file stamps are accidentally edited
away. Written atomically after every `init` / `update` / `improve` / `replicate`
run.

```json
{
  "schema": 1,
  "plugin_version": "1.4.0",
  "last_run": {
    "at": "2026-05-26T08:00:00Z",
    "mode": "init|update|improve|replicate",
    "host_runtime": "copilot-cli|claude-code|opencode|codex-cli|gemini-cli"
  },
  "artifacts": [
    {
      "path": "AGENTS.md",
      "stamp_version": "1.4.0",
      "stamp_at": "2026-05-26T08:00:00Z",
      "kind": "agents-md|subagent|skill|mcp-config|hooks|other",
      "platform": "host|copilot-cli|claude-code|opencode|codex-cli|gemini-cli",
      "checksum": "sha256:<hex>"
    }
  ]
}
```

The manifest is operational state only — never inside any `agents/` directory and
never tracked by git unless the user explicitly opts in via the artifact tracking
question.

### Detection signals (improve mode)

1. Read `.agents-system-setup/generated.json` if present; treat `plugin_version`
   as authoritative.
2. Otherwise, scan every generated artifact for the inline stamp and take the
   highest version found.
3. If neither manifest nor stamp is present, treat as `pre-stamp` and assume
   `v1.3.0` (the last version before stamping was introduced).
4. Compare detected version against the current plugin version from
   `plugin.json`. If the detected version is older, run the migration playbook
   below.

### Per-version migration playbook

Each row describes the **minimum content delta** for a major/minor bump. The
playbook is additive — running `improve` from `v1.2.0` to `v1.4.0` applies the
`v1.2.0 → v1.3.0` row, then the `v1.3.0 → v1.4.0` row, in order.

| From → To | Required deltas |
|---|---|
| `pre-stamp → v1.3.0` | Add `<!-- agents-system-setup:generated-by: ... -->` marker to every artifact; emit `.agents-system-setup/generated.json`. |
| `v1.2.0 → v1.3.0` | Delete `orchestrator.agent.md` / `.claude/agents/orchestrator.md` / `.opencode/agents/orchestrator.md` / `.gemini/agents/orchestrator.md`; consolidate Orchestration Operating Model into `AGENTS.md`; relocate OpenCode `permission.task` to `opencode.json` with extract-and-preserve. (See [Deprecated orchestrator subagent files](#deprecated-orchestrator-subagent-files) above.) |
| `v1.3.0 → v1.4.0` | Trim AGENTS.md › Orchestration Operating Model from ~83 to ~37 lines (preserve inline Required Minimum 12-field summary and malformed-assignment behavior); trim subagent Acceptance Checklist from 14 → 6 items (preserve receiver-side defenses: required-min, owned-paths intersection, approvals, full-form gate, security-team fields, no-invent rule); add `generated-by` stamps; emit central manifest. |
| `v1.4.0 → v1.5.0` | See [v1.4.0 → v1.5.0 details](#v140--v150-migration-details) below — the row was extracted because it spans multiple coordinated emissions across skills, AGENTS.md sections, roster roles, and all 5 subagent templates. |
| `v1.5.0 → v1.6.0` | See [v1.5.0 → v1.6.0 details](#v150--v160-migration-details) below — adds audience tags to AGENTS.md, inlines project-standard digest into every subagent file. Subagents migrated FIRST per atomic 3-state ledger. |
| `v1.6.0 → v1.7.0` | See [v1.6.0 → v1.7.0 details](#v160--v170-details) below — add `## Orchestration Operating Model` › `### Native Runtime Agents` with `<!-- agents-system-setup:host-builtins-routing -->` anchor to `AGENTS.md`; for OpenCode targets, propose extending `permission.task` with `explore` and `general` allows; no subagent file mutations (orchestrator-side only per hard rule #38). |
| `v1.7.0 → v1.8.0` | See [v1.7.0 → v1.8.0 details](#v170--v180-details) below — emit `tool-catalog-audit` skill at every selected runtime's skills path; add `tool_catalog_version` field to `.agents-system-setup/generated.json`; add per-file `<!-- agents-system-setup:tool-catalog-version: {{PLUGIN_VERSION}} -->` stamp to AGENTS.md and every generated agent. Tool list changes default to `manual-review` — never auto-patch subagent `tools:` / `tool_allowlist` (security boundary). |

### v1.4.0 → v1.5.0 migration details

When the detected version is `v1.4.0` (or any pre-stamp `v1.4.0`-shaped
artifact), apply these deltas in order:

1. **`task-handoff` skill emission.** Emit
   `task-handoff` skill at every selected runtime's skills path including
   Codex at `.codex/skills/task-handoff/SKILL.md`.
2. **Build Gate (SDLC) — software-dev projects only.** Ask interview Q9d
   Build Gate strictness. If not `Skip`:
   - Emit the `code-change-build-gate` skill at every runtime's skills path.
   - Render `## Build Gate (SDLC)` in `AGENTS.md` with the matrix snippet.
   - Add `build-runner`, `change-bug-hunter`, `change-validator` to the
     roster. Merge `change-validator` into `@reviewer` for `Light`.

   For non-software-dev projects or strictness `Skip`, render the section
   as `Build Gate (SDLC): n/a — non-software project or user skipped`.
3. **Instruction Memory Audit section.** Add `## Instruction Memory Audit`
   to `AGENTS.md` with the standard placeholders.
4. **Subagent template patches.** Patch every subagent template
   (Markdown for Copilot/Claude/OpenCode/Gemini and TOML for Codex) to
   include the `task-handoff` source-of-truth pointer at the top of
   Acceptance Checklist and Reporting Template sections. Preserve the
   existing inline content as the fail-closed minimum and add the new
   `Build gate:` line in the Reporting Template.
5. **Orchestration Operating Model update.** Update `AGENTS.md` so the host
   CLI session loads `task-handoff` and passes
   `Skills Referenced: task-handoff loaded=true` in delegation packets.
6. **Codex skills documentation fix.** Replace any stale wording such as
   "Codex → no native skills" in generated `AGENTS.md` or skills tables.
   Codex supports `.codex/skills/<name>/SKILL.md` (project) or
   `~/.codex/skills/<name>/SKILL.md` (user).

### v1.5.0 → v1.6.0 migration details

The v1.5.0 → v1.6.0 upgrade introduces layered context (visible audience tags) and self-contained subagent files with inline project-standard digests. Migration is atomic via a 3-state ledger (`prepared` → `applied` → `verified`). Subagent files are migrated FIRST; AGENTS.md is migrated LAST; the manifest version bumps only after every artifact is `verified`.

#### Detection signals

- `missing-audience-tag` — AGENTS.md `## Section` heading lacks a visible `**Audience:** <value>` line (only flagged when `subagent_count >= 2` AND profile in {balanced, full}; skipped for Compact/single-agent setups).
- `non-self-contained-subagent` — subagent file (`.agent.md`/`.md` or Codex `.toml`) lacks the `<!-- subagent-digest:managed:start v=<hash> --> ... :end -->` block, OR the body hash does not match the marker (drift; severity WARNING).

#### 8-step atomic procedure

1. Read `.agents-system-setup/generated.json`; confirm stamp is `1.5.x`.
2. Render the v1.5.0 → v1.6.0 migration plan; `ask_user` for approval.
3. For each subagent file:
   a. Back up to `.agents-system-setup/migration-backup/<ts>/<rel-path>`.
   b. **Write-ahead ledger** — append `{"artifact":"<rel-path>","state":"prepared","backup_path":"<abs-backup>","intended_action":"inject-digest","ts":"<iso>","migration":"v1.5.0-v1.6.0"}` to `.agents-system-setup/migration.jsonl` and fsync; the row MUST exist on disk before the artifact is touched.
   c. Inject `<!-- subagent-digest:managed:start v=<hash> --> ... :end -->` block (Codex uses 3-line literal variant; others use rendered digest).
   d. Append `{"artifact":"<rel-path>","state":"applied","ts":"<iso>"}` to the ledger after the artifact write succeeds.
4. After ALL subagents reach `applied`: back up `AGENTS.md`, write-ahead `{"artifact":"AGENTS.md","state":"prepared","backup_path":"<abs-backup>","intended_action":"insert-audience-tags-and-notice",...}`, insert `**Audience:**` markers under every `## Section` (gated), append `## Subagent Self-Contained Notice` block, then append `{"artifact":"AGENTS.md","state":"applied",...}`.
5. Validation pass: re-read every modified artifact, parse frontmatter, recompute digest hash, confirm marker matches body.
6. On pass: append `{"artifact":"<rel-path>","state":"verified","ts":"<iso>"}` for every artifact (do not mutate prior `prepared` / `applied` rows — JSONL is append-only).
7. Update `.agents-system-setup/generated.json` › `version` to `1.6.0`. This step is the ONLY artifact that fails closed — if any earlier step errored, this never runs and the system remains a half-migrated state (some artifacts at `applied`, others at `prepared`) for the next `upgrade` resume.
8. On resume after partial run: scan ledger for each artifact's last state. If the last state is `prepared` (write-ahead recorded but `applied` never appended), restore from `backup_path` and re-prompt user to retry or abort. If the last state is `applied` (modification succeeded but `verified` never appended), re-run the step 5 validation pass.

#### Anti-patterns

- Migrating AGENTS.md before subagents (rollback target unclear).
- Bumping `generated.json` version before all artifacts reach `verified`.
- Auto-applying without `ask_user` approval at step 2.
- Treating digest hash drift as ERROR (it's WARNING — content evolves naturally).

### v1.6.0 → v1.7.0 details

The v1.6.0 → v1.7.0 upgrade introduces orchestrator-side native runtime agent
routing. Migration is atomic via the same append-only 3-state ledger
(`prepared` → `applied` → `verified`) in
`.agents-system-setup/migration.jsonl`.

#### 8-step atomic procedure

1. Read `.agents-system-setup/generated.json` and the generated artifact stamp;
   confirm the source version is `1.6.0` or `1.6.x`.
2. Render the proposed diff: insert the `### Native Runtime Agents` subsection
   under `## Orchestration Operating Model` in `AGENTS.md` using the full or
   compact variant from `host-builtins-routing.snippet.md` based on the recorded
   `output_profile`.
3. **Conflict scan (manual-review classification):** grep `AGENTS.md` outside
   any managed block for existing prose containing: `Host Built-in`,
   `native runtime agents`, `general-purpose`, `task-class`, `explore-class`,
   `host_builtins_routing`. Any match outside managed blocks classifies the row
   as `manual-review` and prompts the user to either (a) merge their custom prose
   into the managed block, (b) keep the custom prose and skip emission, or
   (c) overwrite (requires explicit confirmation). Do NOT auto-modify unmanaged
   prose.
4. `ask_user` per-group approval (`add`, `patch`, and `manual-review` groups
   separately).
5. For each approved file: back up to
   `.agents-system-setup/migration-backup/<timestamp>/`, append a `prepared`
   ledger row with `backup_path` and `intended_action` to
   `.agents-system-setup/migration.jsonl`, modify the file, then append an
   `applied` ledger row.
6. For OpenCode targets: ALSO update `opencode.json` `permission.task` to add
   `explore: allow` and `general: allow` entries (or record
   `host_builtins_routing: declined` in the manifest if the user declines this
   gate); use the same `prepared` → `applied` ledger pattern.
7. Run the validation pass: re-run the 2 new validator functions
   (`check_host_builtins_routing_in_agents_md` cannot fully verify the rendered
   `AGENTS.md`, but the manifest update can record the anchor presence);
   manually grep for the `<!-- agents-system-setup:host-builtins-routing -->`
   anchor in the user's emitted `AGENTS.md`.
8. On success, append `verified` ledger rows for every modified file, then bump
   `.agents-system-setup/generated.json` version to `1.7.0`. Resume protocol:
   scan the ledger; entries with `prepared` but no `applied` restore from
   backup; entries with `applied` but no `verified` re-run validation.

#### Rollback

`prepared` rows without `applied` indicate aborted migrations; restore from
`backup_path`. JSONL is append-only.

### v1.7.0 → v1.8.0 details

The v1.7.0 → v1.8.0 upgrade introduces catalog-aware tool validation and a
host-side read-only `tool-catalog-audit` skill. Migration stays additive and
uses the same append-only ledger pattern.

#### 8-step write-ahead procedure

1. Read `.agents-system-setup/generated.json` and stamps; confirm source
   version is `1.7.0` or `1.7.x`.
2. Render the proposed diff: insert `tool-catalog-audit` skill files at every
   selected runtime's skills path; add `tool_catalog_version: "1.8.0"` to the
   manifest; render per-file stamp markers in any regenerated file. Do NOT
   modify any existing subagent `tools:` / `tool_allowlist` lists in this step.
3. Run the `tool-catalog-audit` skill in REPORT mode against every generated
   agent file. Classify each finding:
   - `unknown-tool-name-in-agent` → `manual-review` (suggested closest match
     shown to user; never auto-applied).
   - `legacy-tool-name-in-agent` → `manual-review` (alias map shows old → new;
     never auto-applied).
   - `cross-runtime-tool-leak` → `manual-review` (severe; usually means
     runtime mix-up).
   - `missing-tool-catalog-stamp` → `audit-needed` (informational; user may add
     stamp at next regeneration).
   - `opencode-permission-wildcard-too-broad` (when OpenCode files have
     `"*": allow` on `permission.task` or `permission.skill`) →
     `manual-review`.
4. `ask_user` per-group approval (`add` = new skill files; `audit-needed` =
   stamp additions; `manual-review` = grouped per-file, user opts in to each
   fix).
5. For each approved file: backup to
   `.agents-system-setup/migration-backup/<timestamp>/`, append `prepared`
   ledger row with `backup_path` + `intended_action` to
   `.agents-system-setup/migration.jsonl`, modify file, append `applied`
   ledger row.
6. Add `tool_catalog_version: "1.8.0"` and
   `tool_catalog_hash: "<sha256-first-12-of-tool-catalog.json>"` to
   `.agents-system-setup/generated.json` (write-ahead pattern: `prepared` →
   modify → `applied`).
7. Run validation: re-run `check_tool_catalog_stamp_in_templates` against the
   user's emitted files; run the audit skill again to confirm no new ERRORs.
8. On success, append `verified` ledger rows for every modified file. Resume
   protocol: scan ledger; `prepared` without `applied` → restore from backup;
   `applied` without `verified` → re-validate.

#### Rollback

Tool-list changes are NEVER auto-applied, so rollback typically only restores
stamp markers, skill files, and manifest fields. JSONL is append-only.

## Mismatch & Deprecation Detection (upgrade mode)

The version-stamp playbook above handles the **content delta** between known
versions. `upgrade` mode also runs a **structural diff** against the current
plugin's expected output, so deprecated artifacts and missing/stale prose are
caught even when version stamps are absent, edited, or correct but the file
content has drifted. The audit runs after Phase 1 footprint detection and
before any write.

### Detection signals

| Signal | What it catches | Detection rule |
|---|---|---|
| `stale-stamp` | Old version stamp | Per-file stamp or central manifest `plugin_version` < current `plugin.json` `version`. |
| `missing-section` | Required `AGENTS.md` section absent | Required sections by current version: `Plan Handoff Contract`, `Context Loading Policy`, `Instruction Memory Audit`, `Memory & Learning System`, `Task-Type Routing Map`, `Security & Audit Matrix`, `Threat Model`, `Architecture & Design Pattern Decisions`, `ADR Index`, `Quality Gates`, plus `Build Gate (SDLC)` for software-dev or its `n/a` rationale. Match section headings literally (the exact `&`, not `/`). |
| `missing-skill` | Required skill not emitted | `task-handoff` skill missing at any selected runtime's skills path (Codex included); `code-change-build-gate` skill missing for software-dev projects with strictness != `skipped`. |
| `missing-role` | Required roster role missing | For software-dev with strictness != `skipped`: `build-runner`, `change-bug-hunter`, `change-validator` (or `change-validator merged into @reviewer` for `Light`). |
| `deprecated-artifact` | File should no longer exist | `orchestrator.agent.md`, `.claude/agents/orchestrator.md`, `.opencode/agents/orchestrator.md`, `.gemini/agents/orchestrator.md`, `.codex/agents/orchestrator.toml`, anything under `.agents-system-setup/{agents,skills,hooks,commands,prompts,plugins}/`. |
| `stale-prose` | Generated prose contradicts current plugin truth | "Codex → no native skills" in AGENTS.md skills table, `permission.task` block in an OpenCode subagent file (must be in `opencode.json`), subagent templates missing the `task-handoff` pointer, subagent Reporting Template missing the `Build gate:` line. |
| `unsupported-runtime-field` | Field that the runtime never loaded | Codex agent TOML `memory` or `request_user_input`, Gemini `mcpServers` (must be `mcp_servers`), Copilot custom-agent `tools:` containing `ask_user`, OpenCode `mcp-servers:` in agent frontmatter. |
| `adapter-drift` | `CLAUDE.md` / `GEMINI.md` no longer mirrors `AGENTS.md` | Hash mismatch when adapter was originally a copy; resolve via [instruction-memory-audit](./instruction-memory-audit.md). |
| `missing-overflow-link` | Long section moved to references with no pointer | `AGENTS.md` references a moved section by name but the Overflow Details link is missing. |

- `missing-audience-tag` — AGENTS.md `## Section` heading lacks a visible `**Audience:** <value>` line when conditions warrant (subagent_count >= 2, profile balanced/full). Classify: `patch` (insert marker via section-header rewrite).
- `non-self-contained-subagent` — subagent file lacks the `<!-- subagent-digest:managed:start v=<hash> -->` block or has hash mismatch. Classify: `patch` (inject block or update body+hash).
- `missing-native-runtime-agents-subsection` — AGENTS.md has no `### Native Runtime Agents` subsection AND subagent_count >= 2 (regardless of profile: Balanced/Full → full variant; Compact → compact variant). Classify: `add`.
- `missing-host-builtins-anchor` — AGENTS.md has the heading but no `<!-- agents-system-setup:host-builtins-routing -->` anchor. Classify: `patch` (insert anchor before the heading).
- `unmanaged-host-routing-prose` — AGENTS.md outside any managed block contains the conflict-scan terms from the v1.6.0 → v1.7.0 procedure. Classify: `manual-review` (never auto-modify).
- `missing-tool-catalog-stamp` — generated file has no `<!-- agents-system-setup:tool-catalog-version: ... -->` marker AND has a `generated-by` stamp ≥ 1.8.0. Classify: `audit-needed` (informational; user may add stamp at next regeneration).
- `unknown-tool-name-in-agent` — agent file references a tool name not in the runtime's catalog block. Classify: `manual-review` (suggested closest match shown; never auto-applied — tool allowlists are security boundaries).
- `legacy-tool-name-in-agent` — agent file references a tool name in the runtime's `aliases[]`. Classify: `manual-review` (alias map shows old → new; user approves per file).
- `cross-runtime-tool-leak` — agent file references a tool name that belongs to a DIFFERENT runtime's catalog (e.g., Copilot `vscode` in `.claude/agents/*.md`, or Claude `Bash` in `.gemini/agents/*.md`). Classify: `manual-review` (severe; usually means runtime mix-up).

### Upgrade procedure

1. **Detect.** Walk every generated artifact and emit one report row per
   signal. Group by file and severity (`required`, `recommended`,
   `informational`).
2. **Classify.** Tag each signal as `delete`, `add`, `patch`, or `replace`.
   `delete` is reserved for deprecated artifacts; `add` for missing
   sections/skills/roles; `patch` for stale prose where the existing prose
   can be safely amended in place; `replace` for whole-block rewrites.
3. **Propose.** Render a compact upgrade card to the user with the per-file
   plan, citing the version playbook row(s) that justify each delta. Wait
   for `ask_user` approval. Approval is per-group (all `delete`s together,
   all `add`s together, etc.) — the user may decline individual groups.
4. **Backup.** `cp <file> <file>.bak` for every artifact about to be touched.
   For directories that will be removed, copy contents into
   `.agents-system-setup/migration-backup/<timestamp>/`.
5. **Apply.** Execute approved deltas in order: `delete` → `add` → `patch`
   → `replace`. Preserve user-authored content outside managed blocks at
   all times.
6. **Ledger.** Append one JSONL entry to `.agents-system-setup/migration.jsonl`
   per touched artifact (old version, new version, signal, classification,
   backup path, decision).
7. **Manifest.** Update `.agents-system-setup/generated.json` atomically
   after all artifact writes succeed (write-temp + rename).
8. **Verify.** Re-run the structural diff. Remaining signals must be either
   `informational` or explicitly deferred with a recorded rationale.

### Mismatch report shape

```text
Upgrade mismatch report — detected v1.3.0, current v1.5.0

[REQUIRED · delete]
  - .github/agents/orchestrator.agent.md (deprecated-artifact, v1.3.0 playbook)
  - .claude/agents/orchestrator.md (deprecated-artifact, v1.3.0 playbook)

[REQUIRED · add]
  - .github/skills/task-handoff/SKILL.md (missing-skill, v1.5.0 playbook)
  - .codex/skills/task-handoff/SKILL.md (missing-skill, v1.5.0 playbook)
  - AGENTS.md › ## Build Gate (SDLC) (missing-section, v1.5.0 playbook, software-dev)
  - AGENTS.md › ## Instruction Memory Audit (missing-section, v1.5.0 playbook)
  - Roster: build-runner, change-bug-hunter, change-validator (missing-role, v1.5.0 playbook, software-dev)

[RECOMMENDED · patch]
  - .github/agents/reviewer.agent.md (stale-prose: task-handoff pointer missing, v1.5.0 playbook)
  - AGENTS.md skills table (stale-prose: "Codex → no native skills", v1.5.0 playbook)

[INFORMATIONAL]
  - CLAUDE.md (adapter-drift: hash differs from AGENTS.md; review via instruction-memory-audit)

Approve groups: [REQUIRED · delete] [REQUIRED · add] [RECOMMENDED · patch]
```

### Anti-patterns

- Applying upgrade deltas without showing the mismatch report to the user.
- Treating `informational` signals as actionable without explicit user
  approval (especially `adapter-drift` — `CLAUDE.md` / `GEMINI.md` are
  expected to be copies/symlinks).
- Skipping the per-version playbook in favor of jumping to the latest
  expected state — intermediate version deltas may have to handle data
  shapes the current code no longer produces.
- Deleting deprecated artifacts without backup. Always copy to
  `.agents-system-setup/migration-backup/<timestamp>/` first.
- Updating the manifest before all artifact writes succeed.

### Migration safety rules

- **Always backup before editing.** `cp <file> <file>.bak` before any in-place
  rewrite of a generated artifact.
- **Diff custom content first.** Compare the existing managed block against the
  stock template from the detected version. If any non-template prose lives
  inside the managed block, surface a `custom orchestration / handoff additions
  found, review required` report and require explicit user approval before
  replacement.
- **Preserve user content outside the managed block.** The plugin never edits
  content outside `<!-- agents-system-setup:managed:start -->` / `:end` markers.
- **Update the stamp atomically with content.** Never write a new stamp without
  also writing the corresponding content delta.
- **Manifest is updated last.** Write artifact changes first, verify, then
  rewrite `.agents-system-setup/generated.json` atomically (write-temp + rename).
- **Pre-stamp detection is conservative.** When no stamp or manifest exists,
  assume the most recent legacy version (`v1.3.0`) and prompt the user to
  confirm before applying any migration.

### Stamp anti-patterns

- Hand-editing a `generated-by` stamp — the plugin uses it as ground truth; manual
  edits desynchronize the manifest and the artifact.
- Committing `.agents-system-setup/generated.json` to git without the user's
  explicit opt-in via the artifact tracking question.
- Skipping the per-version delta for an intermediate version when running
  `improve` across two majors — always apply each version's delta in order.
- Writing the manifest before the artifact deltas — leaves the manifest
  claiming a state that does not exist on disk.
