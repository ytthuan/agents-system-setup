# Agents Doctor — generated-system health check

`agents-doctor` is the re-runnable, **read-only** reconciliation tool for a
generated agent system. It answers one question the one-shot Phase 7 verify
cannot: *is the system on disk still consistent with what the plugin generated?*

It exists because Phase 7 verification runs once, inside the generating session,
as prose. Nothing afterward catches a session that hand-writes a stray
`orchestrator.agent.md` (which violates the host-session-is-orchestrator rule
and is unresolvable by any runtime), an agent deleted by accident, or a manifest
left behind by a partial run. The doctor turns that one-shot check into a
durable guardrail a human, CI, or the host session can run anytime.

## What it reconciles

The authoritative source of truth is the central manifest
`.agents-system-setup/generated.json` (schema in
[misplaced-artifacts-migration](./misplaced-artifacts-migration.md#central-manifest-agents-system-setupgeneratedjson)).
The doctor compares the manifest's `artifacts[]` against the agent files present
in the runtime agent directories:

- `.github/agents/` (Copilot CLI)
- `.claude/agents/` (Claude Code)
- `.opencode/agents/` (OpenCode)
- `.codex/agents/` (OpenAI Codex)
- `.gemini/agents/` (Gemini CLI)

## Signal catalog

| Signal | Severity | Detection rule | Suggested action |
|---|---|---|---|
| `orchestrator-subagent-file` | error | Agent file whose logical name is `orchestrator` in any runtime agents dir. | Delete via upgrade-mode migration; the orchestrator is the host session reading `AGENTS.md`. |
| `stray-agent` | error | Agent file on disk whose path is not in manifest `artifacts[]`. | Remove it or re-run the plugin (update/improve) so it is tracked. |
| `missing-artifact` | error | Manifest `subagent`/`agents-md` path missing on disk. | Restore from VCS or regenerate. |
| `checksum-drift` | warn | File sha256 differs from manifest `checksum`. | Expected if intentionally edited; otherwise refresh the manifest. |
| `missing-stamp` | warn | Agent file lacks the `generated-by` stamp. | Re-run the plugin to stamp it, or confirm it is hand-authored. |
| `operational-state-artifact` | error | Forbidden subtree (`agents`/`skills`/`hooks`/`commands`/`prompts`/`plugins`) under `.agents-system-setup/`. | Move to the platform-standard path; log in `migration.jsonl`. |
| `manifest-version-drift` | warn | Manifest `plugin_version` != `AGENTS.md` stamp. | Run upgrade mode to reconcile versions. |

## Reconciliation algorithm

1. Discover agent files across all five runtime agent directories (deduplicated).
2. Always run the manifest-independent checks: `orchestrator-subagent-file` and
   `operational-state-artifact`.
3. Load `.agents-system-setup/generated.json`. If absent, stop here and exit `2`
   (only the two checks above ran) — prompt to (re-)run the plugin.
4. With a manifest present, run: `stray-agent`, `missing-artifact`,
   `checksum-drift`, `missing-stamp`, and `manifest-version-drift`.
5. Sort findings by severity, then signal, then path.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Clean — no error-severity findings (warnings allowed unless `--strict`). |
| `1` | One or more error-severity findings, or warnings under `--strict`. |
| `2` | No manifest found; only the manifest-independent checks ran. |

## Placement and emission

- The engine is emitted to `.agents-system-setup/agents-doctor.py` — co-located
  with the manifest it reads. It is the **one sanctioned read-only tool** inside
  the operational-state directory; it writes nothing. The directory's
  forbidden-subtree rule targets runtime artifact directories, not flat tools.
- The host-side skill is emitted at every selected runtime's skills path
  (`.github/skills/agents-doctor/SKILL.md`, `.claude/skills/...`,
  `.opencode/skills/...`, `.codex/skills/...`, `.gemini/skills/...`), like the
  other host-side skills (`task-handoff`, `tool-catalog-audit`,
  `code-change-build-gate`).
- Both the script and the skill carry the `generated-by` stamp and appear in the
  manifest (`kind: other` for the script, `kind: skill` for the skill), so the
  doctor never flags its own files as strays.

## CI usage

For git-tracked agent systems, run the doctor in CI to fail PRs that introduce
strays or drift (this is the P2 follow-up to the doctor itself):

```yaml
- name: Validate agent system
  run: python3 .agents-system-setup/agents-doctor.py --strict
```

`--strict` makes `checksum-drift` and other warnings fail the job, which is
usually what a team wants once the system is stable.

## Boundary rules

1. **Read-only.** The doctor never edits, deletes, or moves files. It reports.
2. **Host-only.** Subagents never invoke the skill; they `return-to-orchestrator`
   on drift in their owned files.
3. **Fixes are gated.** Removing a stray (including a hand-written `orchestrator`)
   goes through the upgrade-mode migration ledger in
   [misplaced-artifacts-migration](./misplaced-artifacts-migration.md#deprecated-orchestrator-subagent-files),
   never a silent delete.
4. **Clean is scoped.** A clean result covers the scanned surfaces only and is
   not approval for any write.

## Anti-patterns

- Auto-deleting flagged files instead of routing through the migration ledger.
- Running the doctor from inside a subagent.
- Committing `.agents-system-setup/generated.json` (or the doctor script) without
  the user's artifact-tracking opt-in.
- Treating `checksum-drift` as an error in normal (non-`--strict`) runs.
