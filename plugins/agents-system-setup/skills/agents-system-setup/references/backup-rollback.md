# Backup & Rollback

Capture a verified restore point before every approved write run. This is an
agent-executed file procedure, not a separate automatic backup service. Report
the actual backup and verification result; a planned snapshot is not a backup.
Two layers, different granularity:

1. **Run-level snapshot** — full preimages of every file the run will touch,
   taken before the first approved write, restorable as a set by `rollback`
   mode. This is the "undo that run" net.
2. **Per-file `.bak`** — the intra-run safety net for managed-block merges
   (Phase 5), unchanged from before.

Snapshots complement git, they do not replace it: they exist for no-git
checkouts, dirty trees, `project-local`/untracked artifacts, and runs whose
files were never committed. For `project-tracked` files, git history remains
the team-visible restore point; snapshots are the always-present local one.

## Snapshot policy (when, what, where)

| Question | Contract |
|---|---|
| When | Before the first approved write of every `init` / `update` / `improve` / `upgrade` / `replicate` / `migrate` run, including native initialization and MCP/runtime config. Record every created path as `absent`; retain full preimages for any existing files, even during init. Read-only previews create no snapshots. |
| What | Every modified/deleted file and every created path (`absent` pre-write), including supporting scripts/assets, `generated.json`, and approval sidecars. No recursive `.git/` backup; only the exact `.git/info/exclude` file may be included when the approved tracking plan edits it. Personal-global writes use explicit approved absolute roots and `scope: personal-global`. |
| Where | `.agents-system-setup/backups/<run-id>/` with `backup.json` and **content-addressed** blobs at `files/<sha256>`. `run-id = <UTC compact timestamp>-<mode>-<random suffix>`; create exclusively and never reuse an existing ID. For personal-global scope, select an approved state root outside the repo. |
| Ledger | `.agents-system-setup/backups.jsonl` is an append-only run/event index: `run_id`, time, operation/status, plugin version, topology, plan and snapshot path. Gated runs carry `approvals`, `artifact_tracking`, and `overwrites` references; config/sidecar evidence remains authoritative. `backup.json` holds the file table and before-state metadata. Append postimage/state events as writes complete; never overwrite the verified preimage inventory. |
| Retention | **Never auto-deleted.** Cleanup is an explicit approved action; report snapshot count and total bytes in the output contract so bloat is visible. |

Blob naming is deliberate: hash-named preimages create no `agents/`, `skills/`,
or `prompts/` subtrees inside the operational-state directory, so `agents-doctor`
and the misplaced-artifact migration never misread a backup as a live (or
misrouted) artifact. A blob's name supplies its integrity check — restore
re-hashes and compares before writing.

A snapshot is evidence, not approval: taking one never authorizes the write
itself, and the normal plan / MCP / tracking gates still run in order.

## File-state contract

For each approved path, record `before`, intended `after`, and observed `after`
with `exists`, SHA-256 (or null for absent), byte size, and file mode where
supported. Keep preimage blobs byte-exact, including line endings. Record
`before_version`/`before_topology` separately from the plugin version executing
the run and the target state. The pre-migration manifest is a preimage too.

1. Inspect and approve the complete write set before creating the snapshot.
   Resolve source/destination collisions and reject symlinks, path traversal,
   out-of-scope roots, and unsupported non-regular files before writes.
2. Write blobs and inventory to a new run directory, flush them, and re-hash
   every stored blob. Record `prepared` only after all preimages verify. Backup
   failure blocks the first target write. Never recursively back up backups.
3. Re-check each live preimage just before replacement. Record intended bytes
   before a write and observed postimage/state after it. Stop on concurrent
   edits; do not stamp a partly applied run as verified.
4. Publish the generated manifest last and record `verified` after validation.
   Keep partial-run events for resume/rollback. Do not infer successful writes
   from intended postimages alone.

The blob hash detects corruption relative to the inventory; it is not proof
that an untrusted or edited inventory is authentic. Review scope and paths on
restore as well as checking hashes.

## Rollback procedure (the `rollback` mode)

Triggers: `agents-system-setup rollback`, `/agents-system-setup rollback`,
`$agents-system-setup rollback`, or natural language ("rollback my agents",
"restore the backup", "undo the last change"). Entered from the Phase 0/1.5
mode choice whenever `.agents-system-setup/backups.jsonl` or
`.agents-system-setup/backups/` exists; skip Phases 2–4 and the Phase 5 write
path.

1. **Enumerate** — group `backups.jsonl` events by run ID; also inspect
   `backups/<run-id>/backup.json` if the index is absent/incomplete. Show the
   before-version/topology that each run restores and its completion state.
   No verified inventory → never invent snapshots. Orphaned `.bak` files may
   be offered as clearly labeled single-file restores.
2. **Choose** — `ask_user` single-select of snapshots (newest first) or
   `Cancel`. Show the exact restore plan and obtain any separate runtime/MCP
   config approvals before the safety snapshot or target writes.
3. **Verify integrity** — re-hash every blob against `backup.json`'s recorded SHA-256; any
   mismatch or missing blob blocks that snapshot with the reason. Integrity
   failure of one snapshot never blocks restoring a different one.
4. **Fresher-work check** — compare current files against recorded observed
   **postimages**, not preimages (the run itself changed the preimages).
   Matching postimages are eligible for approved restoration; matching
   preimages are already restored. Other states, including missing after-state
   evidence, require a diff and explicit `restore preimage` / `keep current`
   decision. Never silently clobber newer user work. Check newly created files
   too: an `absent` preimage is not permission to delete a subsequently edited
   file. Re-check chosen current hashes immediately before restoration.
5. **Safety snapshot** — before restoring, snapshot the *current* state as a
   new `rollback`-mode run, so a rollback is itself reversible.
6. **Restore** — write preimages byte-exact, including their original
   `agents-system-setup:generated-by` stamps (rollback restores history, not
   the current plugin version); re-delete files the undone run created
   (`absent` entries); restore `generated.json` last. MCP / runtime config
   restores render their own approval gate with the exact before/after —
   rollback never bypasses the MCP gate. Clean up only empty directories
   created by the undone run. Never restore an old manifest wholesale over a
   partial restore: if the user keeps conflicting files, preserve its current
   bytes pending an approved reconciliation and report `partial rollback`.
7. **Verify** — compare restored bytes/modes with the snapshot first. Run the
   compatible doctor when available and report its findings separately. Old
   valid state may predate the current memory budget or manifest; do not
   rewrite it to pass today's checks. A baseline with no manifest is valid
   rollback output. Append `rolled_back` only for a complete restore, otherwise
   `partial`/`failed`, to the backup index and the existing migration ledger.
8. **Never** — re-run native initialization, write MCP/runtime config outside
   its gate, alter Git history, or "upgrade" restored files to current plugin
   semantics. Rollback restores bytes, not intentions; migrating forward again
   is a separate, explicit `upgrade` decision.

## Rollback to an older plugin version

Snapshots are **before-state**: the snapshot taken by the vX → vY upgrade
restores vX, not vY. Select the displayed `before_version` and topology, not
the executing plugin version. To undo several runs, restore newest first back
to the desired boundary; one older run snapshot covers only that run's write
set and cannot remove all files introduced later.

Restored stamps and contracts remain unchanged until an explicit future
`upgrade`. The plugin itself rolls back by installing a pinned release
(README › Install a specific release). A newer plugin may perform a rollback
without immediately migrating the restored system forward again.
