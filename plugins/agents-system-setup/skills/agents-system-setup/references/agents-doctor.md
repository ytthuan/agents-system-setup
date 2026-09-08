# Agents Doctor — generated-system and memory health check

`agents-doctor` is the re-runnable, **read-only** reconciliation and memory
audit tool for a generated agent system. It answers two questions that a
one-shot generation verify cannot:

1. Is the generated system on disk still consistent with its manifest?
2. Is the complete canonical project memory compact, valid, and connected to
   the local references and native skill paths it declares?

The executable is standard-library-only Python and is emitted at
`.agents-system-setup/agents-doctor.py`. It never edits, deletes, truncates,
repairs, or publishes files.

## Contents

- [Commands and exit codes](#commands-and-exit-codes)
- [Canonical memory](#canonical-memory-contract)
- [Adapters and imports](#controlled-adapters-and-imports)
- [References and skills](#references-and-native-skills)
- [Manifest reconciliation](#manifest-reconciliation)
- [Read-only boundary](#read-only-boundary)
- [Completion gate](#ci-and-generation-completion)

## Commands and exit codes

```bash
python3 .agents-system-setup/agents-doctor.py
python3 .agents-system-setup/agents-doctor.py --json
python3 .agents-system-setup/agents-doctor.py --strict
python3 .agents-system-setup/agents-doctor.py --memory-only
python3 .agents-system-setup/agents-doctor.py --root /path/to/repository
```

Normal mode reconciles `.agents-system-setup/generated.json`; it returns `2`
when that manifest is absent. Invalid, unreadable or malformed manifests instead
produce a structured `invalid-manifest` error and exit `1`, including in
`--memory-only` mode. Pre-manifest drafts may omit the manifest, not corrupt it.

| Code | Meaning |
|---|---|
| `0` | No error findings; warnings are allowed unless `--strict`. |
| `1` | Error finding, or warning under `--strict`. |
| `2` | Manifest is absent in normal mode. |

The default root is the parent of `.agents-system-setup/`. `--json` exposes the
same findings and exact metrics used by the human summary and validator
fixtures.

## Canonical memory contract

The authoritative memory path is the **complete root `AGENTS.md`**. A managed
block, generated template, native adapter, or copied excerpt is not an
acceptable proxy for the memory budget. The doctor:

- decodes `AGENTS.md` as strict UTF-8;
- counts physical LF-delimited lines, including a final unterminated segment;
- counts CRLF as one physical line while retaining both raw bytes;
- measures raw UTF-8 bytes before newline normalization;
- enforces hard limits of **150 lines** and **12,288 bytes**;
- reports the advisory target of **80-120 lines**;
- never truncates or drops a user-preserved tail;
- reports token count as `unavailable` because it uses no tokenizer dependency
  or provider API.

Long single lines, Unicode, CRLF, and missing final newlines therefore cannot
evade the byte or line limits. Missing `AGENTS.md`, invalid UTF-8, and hard
budget violations are errors. A complete file shorter than 80 lines is valid
without padding, including under `--strict`; exceeding the 120-line advisory
target is a warning. Namespaced managed markers trigger draft diagnostics even
without a manifest/stamp, but never prove ownership or authorize a rewrite.

The JSON memory report keeps controlled adapter/import overhead separate from
the canonical root metrics:

```json
{
  "canonical_path": "AGENTS.md",
  "lines": 101,
  "bytes": 8420,
  "hard_limits": {"max_lines": 150, "max_bytes": 12288},
  "target_lines": {"min": 80, "max": 120},
  "token_count": {"status": "unavailable"},
  "controlled_adapter_overhead": {"lines": 0, "bytes": 0, "files": []},
  "effective_context": {
    "status": "unknown",
    "reason": "Personal, global, nested, and runtime-loaded context was not observed."
  }
}
```

Overhead counts adapter file bytes, not a claim about runtime import expansion
or deduplication. Unknown personal/global/nested context is not treated as zero. No unrelated
personal directories or arbitrary out-of-root paths are scanned.

## Controlled adapters and imports

The doctor checks only adapters under the repository root and does not infer a
runtime's global loader state. Generated Claude/Gemini adapters must import the
canonical root (`@AGENTS.md`) or be an approved in-root symlink. Existing
custom copies and drift are reported for review, not automatically repaired.
Controlled import checks report cycles and eager imports of workflow/reference
detail where those imports are represented explicitly.

`adapter-missing-canonical-import`, `adapter-cycle`, and
`adapter-eager-workflow-import` are errors for generated output. A
`legacy-memory-copy` or `adapter-drift` finding is a warning. Adapter-file
bytes and lines are reported separately from the root memory budget; effective
import expansion remains unknown without runtime observations.

## References and native skills

Root-declared project-policy/reference paths are checked for **in-root
existence**. A Markdown link proves only that a file exists; it does not prove
that a skill loaded. The doctor reports native load state as unknown unless
directly observed.

Current project skill roots are:

- `.github/skills` — Copilot CLI
- `.claude/skills` — Claude Code
- `.opencode/skills` — OpenCode
- `.agents/skills` — Codex current project discovery
- `.gemini/skills` — Gemini CLI

Active generated `.codex/skills` declarations are errors; explicit legacy
migration/history mentions are not current declarations. Every declared local
SKILL.md path is inspected, including invalid prefixes and traversal out of a
native root. Overlapping
`.agents/skills` and `.claude/skills` declarations are reported for review;
the doctor does not silently deduplicate them. It does not scan user/global
skill directories.

Important findings include:

| Signal | Severity | Detection rule |
|---|---|---|
| `missing-canonical-memory` | error | Root `AGENTS.md` is absent. |
| `memory-invalid-utf8` | error | Canonical memory is not strict UTF-8. |
| `memory-budget-lines` / `memory-budget-bytes` | error | Complete memory exceeds 150 lines or 12,288 raw bytes. |
| `memory-target-lines` | warn | Complete memory exceeds the 120-line advisory target; there is no required minimum length. |
| `malformed-managed-markers` | error/warn | Generated managed markers are missing, duplicated, or out of order. |
| `unresolved-placeholder` | error | A generated output still contains `{{...}}`. |
| `invalid-generation-stamp` | error | Generated-style root memory requires exactly one valid generation stamp. |
| `invalid-manifest` | error | Existing manifest is unreadable, invalid JSON or has invalid artifact field types. |
| `declared-skill-missing` | error | A declared local skill path does not exist in-root. |
| `declared-skill-mislocated` | error | A declared skill path is outside a current native root. |
| `declared-skill-legacy-location` | error | An active generated declaration uses a retired Codex skill root. |
| `skill-overlap` | warn | Declarations resolve to overlapping native roots. |
| `skill-load-state-unknown` | info | Existence was checked, but native loader state is unknown. |
| `stale-task-handoff-name` | error | Generated output uses retired active handoff names outside explicit migration/history text. |

Explicit migration/history text may retain legacy names for recognition; active
generated paths and declarations use `task-delegation` and
`host-delegation`.

## Manifest reconciliation

The authoritative generated artifact inventory is
`.agents-system-setup/generated.json` (schema in
[misplaced-artifacts-migration](./misplaced-artifacts-migration.md#central-manifest-agents-system-setupgeneratedjson)).
The doctor compares `artifacts[]` with controlled runtime directories:

- `.github/agents/` (Copilot CLI)
- `.claude/agents/` (Claude Code)
- `.opencode/agents/` (OpenCode)
- `.codex/agents/` (legacy/current Codex agent artifacts)
- `.gemini/agents/` (Gemini CLI)

Require `schema: 1`, a nonempty `plugin_version`, and a
`sha256:<64 lowercase hex digits>` checksum for every artifact. A missing or
invalid checksum is not an opt-out. Failed reads are errors; readable intentional
edits retain the existing `checksum-drift` warning.

Controlled generated-style outputs must be inventoried, including root memory,
adapters, native skills, linked/local project policy, known project configuration,
top-level hook files and the emitted doctor itself. Markers trigger diagnostics,
not permission to adopt or delete user content. Rejected runtime-directory and
agent-entry symlinks are reported without opening or traversing external targets.

Manifest findings include:

| Signal | Severity | Detection rule |
|---|---|---|
| `orchestrator-subagent-file` | error | An agent file named `orchestrator` exists; the host session is the orchestrator. |
| `stray-agent` | error | An agent file is not listed in manifest `artifacts[]`. |
| `stray-artifact` | error | A controlled generated-style non-agent artifact is missing from the manifest. |
| `missing-artifact` | error | A manifest artifact path is missing. |
| `checksum-drift` | warn | File sha256 differs from its manifest checksum. |
| `artifact-read-error` | error | An existing listed artifact could not be hashed safely. |
| `runtime-surface-out-of-root` | error | A controlled runtime entry resolves outside the assessed root; its target is not read. |
| `missing-stamp` | warn | A generated agent file lacks its generation stamp. |
| `operational-state-artifact` | error | Forbidden runtime subtree exists under `.agents-system-setup/`. |
| `manifest-version-drift` | warn | Manifest and generation stamps use different plugin versions. |

Normal mode always checks orchestrator files and operational-state subtrees.
Memory checks run when a manifest is present or `--memory-only` is selected;
reconciliation requires a valid manifest. Normal-mode absence returns exit
`2`; pre-manifest memory mode instead assesses the draft without requiring one.

## Read-only boundary

1. The doctor reports findings and never modifies files.
2. It is host-only; generated subagents do not invoke it.
3. Fixes require host orchestration and user approval. Removing a stray file,
   including an `orchestrator` file, goes through the migration ledger rather
   than an automatic delete.
4. A clean result is scoped to controlled surfaces and is not approval for a
   write.
5. Existing/custom memory and adapters may be assessed but are never rewritten.

## CI and generation completion

For a tracked agent system, CI can run:

```yaml
- name: Validate agent system memory and artifacts
  run: python3 .agents-system-setup/agents-doctor.py --strict
```

The generation-completion procedure runs the same executable checker before
publishing its completion result:

```bash
python3 .agents-system-setup/agents-doctor.py --memory-only
```

The repository validator also invokes this executable in isolated fixtures.
It must not duplicate the line/byte algorithm; fixture assertions consume the
doctor's JSON output and exit code.
