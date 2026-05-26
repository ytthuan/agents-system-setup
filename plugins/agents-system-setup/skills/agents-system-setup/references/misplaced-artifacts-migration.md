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
