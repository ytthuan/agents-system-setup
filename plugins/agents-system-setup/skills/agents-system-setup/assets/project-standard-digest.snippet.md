# Project Standard Digest Snippet

This snippet is the inline project-standard digest emitted into every specialist
subagent file. It is required for self-containment: a subagent must be able to
operate fail-closed without loading the full `AGENTS.md`. `upgrade` mode patches
only this managed block and preserves user prose outside the block.

## Managed-block schema

Render the digest after platform frontmatter and before role-specific long-form
instructions. The body between the markers is the hash input.

```markdown
<!-- subagent-digest:managed:start v=<sha256-first-12-chars-of-body> -->
**Project standard digest** (read-by: subagent self)
- Purpose: <auto-filled from AGENTS.md Project Snapshot>
- Security boundary: <auto-filled — least privilege, no secrets in code, MCP approval gate>
- Validator gate: bash scripts/validate.sh; markdownlint via npx --yes markdownlint-cli2
- Handoff: consult `task-handoff` skill when host packet says `task-handoff loaded=true`; never re-delegate
- Return-to-orchestrator if scope exceeds owned paths
<!-- subagent-digest:managed:end -->
```

Hash rule: the `v=` field is the first 12 characters of
`sha256(body_between_markers)`. The body starts after the start marker newline and
ends before the newline that precedes the end marker. The renderer (Phase 4
emission and `upgrade` mode migration) computes the hash at write time;
`upgrade` mode also recomputes it during the v1.5.0 → v1.6.0 migration step 5
validation pass and reports drift as WARNING. The static `scripts/_validate.py`
substring checks do NOT recompute the hash — they only verify the managed-block
markers and required body lines are present. Hash drift is enforced at upgrade
rendering time, not by the static validator.

## Required standard lines

The non-Codex digest contains exactly these five required bullet lines:

```text
- Purpose: <auto-filled from AGENTS.md Project Snapshot>
- Security boundary: <auto-filled — least privilege, no secrets in code, MCP approval gate>
- Validator gate: bash scripts/validate.sh; markdownlint via npx --yes markdownlint-cli2
- Handoff: consult `task-handoff` skill when host packet says `task-handoff loaded=true`; never re-delegate
- Return-to-orchestrator if scope exceeds owned paths
```

Keep the title line above the bullets unchanged unless the validator and upgrade
patcher are updated together. Do not add environment-specific secrets, personal
paths, or long policy prose.

## Codex variant

Codex `developer_instructions` has a 65-line soft target and a 75-line hard
target. For Codex, emit this smaller body inside the same managed markers within
the TOML `developer_instructions` string:

```text
Project standard digest (managed by agents-system-setup):
- Boundary: least privilege; no secrets in code; MCP approval gate.
- Handoff: consult `task-handoff` skill when host says loaded=true; never re-delegate.
- See `AGENTS.md` rows for project-wide context.
```

The Codex renderer should keep the managed block near the top of
`developer_instructions`, after any required role sentence and before detailed
boundaries. The same self-containment rule still applies: the Codex subagent must
inline owned paths,
handoff acceptance, safety boundaries, and a reporting skeleton elsewhere in the
same string.

## Validator expectations

The validator function `check_subagent_self_containment` verifies the digest
without treating normal drift as a release-blocking failure.

Expected checks:

1. Every subagent file has the managed-block markers.
2. The hash is recomputed; drift is reported with severity WARNING, not ERROR,
   because drift is expected when the project standard evolves.
3. The block contains exactly the five required lines listed above, or the
   three required Codex bullet lines for the Codex variant.
4. The block is not inside YAML frontmatter.
5. The block is not inside a fenced code block.

When the digest is stale, `upgrade` mode patches only the managed block. User
prose before and after the block remains untouched.

## Upgrade patching protocol

1. Locate the canonical start marker `subagent-digest:managed:start v=` and the
   matching `subagent-digest:managed:end` marker.
2. Validate that there is exactly one digest block per subagent artifact.
3. Create the normal file backup required by update/upgrade mode.
4. Replace only the body and start-marker hash.
5. Re-read the artifact and verify the new hash before moving to the next file.

If the markers are missing, malformed, duplicated, or inside a frontmatter/fenced
block, return the artifact to the orchestrator as a migration problem instead of
blindly appending a second digest.

## Anti-patterns

- Editing the block body without updating the `v=` hash. The validator catches
  stale managed-block drift.
- Removing the markers. The validator and upgrade patcher need them to find the
  managed block.
- Using `<!-- subagent-digest -->` without `:managed:start/end`. It must match
  the canonical pattern for upgrade mode to find it.
- Putting secrets, paths to private resources, or PII inside the digest.
