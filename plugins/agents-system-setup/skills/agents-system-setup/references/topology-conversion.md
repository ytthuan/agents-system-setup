# Topology Conversion (specialists ⇄ solo)

`migrate monolithic` converts an existing system to one working host with
on-demand skills (`agent_topology = solo`). Software projects retain the
approved read-only reviewer exception. `migrate specialists` selects the
reverse direction. This is an explicit migration, not a fresh setup.

## Command and aliases

Use the installed setup skill with these arguments:

| Runtime | Invocation |
|---|---|
| Copilot CLI | `/agents-system-setup migrate monolithic` |
| Claude Code | `/agents-system-setup:agents-system-setup migrate monolithic` |
| Codex CLI | `$agents-system-setup migrate monolithic` |
| OpenCode | `/agents-system-setup migrate monolithic` with the installed command wrapper; otherwise `@agents-system-setup migrate monolithic` |
| Gemini CLI | Confirm the installed setup skill in `/skills`, then ask `Use agents-system-setup to migrate monolithic` |

These are prompts to the setup skill, not standalone shell executables.
Gemini requires the setup skill to be installed explicitly; no plugin install
or per-skill slash command is assumed. For any host, the plain prompt
"Use agents-system-setup to migrate this project to monolithic style" also works
when the skill is available.

- `migrate monolithic`, `migrate mono`, `migrate solo`, and legacy `update solo`
  normalize to `mode=migrate`, `target_topology=solo`.
- `migrate specialists` and legacy `update specialists` normalize to
  `mode=migrate`, `target_topology=specialists`.
- `migrate` without a target asks only for the target. Unknown targets or
  switches require clarification before any write.
- `migrate monolithic --dry-run` (or `migrate specialists --dry-run`) renders the inventory, mapping, proposed
  diffs, and blockers only: no snapshots, config edits, initialization,
  self-update, ledgers, or source removals. Approval is still required on a
  later apply run; re-read preimages then.
- Natural language ("mono agent", "flatten my agents into skills", "convert
  agents to skills") or Q9 choosing a different topology enters the same flow.

Reuse the existing runtime scope, tracking, project purpose, and gates. Ask
only for missing decisions; do not rerun the entire setup interview. Support
hand-authored agents without a generated manifest as reviewed migration input.
If there is no source system, report that and offer `init`. If the requested
topology and coverage already match, report `already migrated` without writes.

## Conversion prompt (ask_user, shown before any write)

Read-only inventory and planning come first. Show one consolidated proposal:

```text
Target: monolithic (solo + on-demand skills)
Source: <runtimes, agent count, existing skills>

| Source responsibility | Decision | Destination | Skills used | Files retired |
|---|---|---|---|---|
| implementer / craft | reuse | code-quality | existing | <source agent> |
| API design + implementation | merge | api-work | code-quality, api-testing | <source agents> |
| test scenarios | extract + reference | test-workflow | api-testing | <source agent> |

Review: <retained read-only reviewer / same-context self-review when permitted>
Boundaries: per-role tool policies do not become host permission isolation;
working roles run in the host context. Required independent review is retained.
Backup: <planned snapshot location>; rollback restores the pre-migration state.
Unresolved dependencies/conflicts: <none or blockers>
```

- Q: "Apply this migration to monolithic style?"
- Choices: `["Apply migration (Recommended)", "Edit mapping", "Cancel"]`.
- `Edit mapping` accepts consolidated changes to reuse/reference/merge/extract
  decisions, then presents the revised proposal. Required responsibilities
  cannot be silently dropped.
- Retaining extra working subagents keeps the result `specialists` and marks
  the migration partial; never label it `solo`. The only permitted solo worker
  is the reviewer described in [topology](./topology.md#reviewer-exception-software-dev-default).
- Software-dev keeps the reviewer even if the Build Gate is skipped. Required
  independence cannot be replaced by self-review. For non-dev without an
  independent gate, zero workers is valid and self-review is labeled honestly.
- Cancel or unresolved blockers leave files untouched. Runtime-config changes
  retain their existing separate approval gates.

For the reverse direction, render the actual target `specialists` in the
proposal and question. Applying the reviewed mapping approves its listed
per-item decisions; `Edit mapping` can change any item without repeating the
entire interview.

## Procedure (specialists → solo)

1. **Inventory & parse** — inspect source agents, root instructions, runtime
   registrations, and their skill lists/body references. Build AgentIR/SkillIR
   from [replication](./replication.md). Record preimage hashes, source ownership,
   and paths without changing files. Keep the complete native configuration as
   source evidence; the portable IR must not discard unsupported fields. Include
   project/user/plugin definitions and active-session overrides in the effective
   roster; their removal or disabling requires the corresponding scope approval.
   Count enabled dispatch targets: shared/global or built-in definitions may
   remain installed when unavailable to this solo host. A project migration
   does not authorize deleting another project's or a user's shared agents.
2. **Compose capabilities** — apply [skill composition](./skill-composition.md):
   reuse → reference → merge compatible procedures → extract missing knowledge.
   Resolve exact skill IDs, prerequisites, duplicate names, missing skills,
   cycles, scripts/assets, and user-owned bodies. Preserve unique instructions;
   do not copy agent frontmatter or delegation boilerplate into skills.
3. **Plan and approve** — show the coverage table, before/after files, owner and
   gate mapping, and the conversion prompt above. Include root/adapters, skills,
   agent removals, config registrations, command pointers, and `generated.json`.
   Any rule that cannot be preserved blocks its conversion pending a decision.
   `--dry-run` ends here before approval or writes.
4. **Snapshot first** — after approval and before the first write, capture and
   verify the complete write set per [backup & rollback](./backup-rollback.md).
   Include overwritten/deleted agents, absent destinations, scripts/assets,
   config, manifest, and approval sidecars. A failed backup blocks migration.
5. **Emit skills first** — create approved skills and supporting files; reused
   skills stay in place. Check folder/ID, frontmatter, every dependency/path,
   source-rule coverage, and load permissions. Record actual loader observations
   when available; file existence alone is not proof of activation.
6. **Switch routing** — update the root Skills index and Directory Architecture,
   capability/gate owners, task-delegation policy, and every live consumer of
   retired agent names. Render the solo stance instead of retaining a parallel
   delegation instruction. Keep the root within 150 lines AND 12,288 bytes.
   OpenCode V2 uses `agents.<root>.permissions` with `subagent` and `skill`
   actions; old `permission.task`/`permission.skill` maps are migration input.
   Approve exact config changes; preserve unrelated settings and stricter rules.
   Evaluate the effective last-match policy, not just the newly appended rules.
   Use the installed runtime's documented schema for retained/new reviewers;
   older platform examples are not a V2 permission template.
7. **Retire agents** — remove only approved source files/registrations after
   replacement coverage and dependency checks pass. Preserve shared skills and
   supporting resources still in use. Remove `AGENT-TEAMS.md` only when owned
   by this setup and now inapplicable. No placeholder stubs in runtime folders.
8. **Verify and publish** — check for dangling names/paths, extra live workers,
   required reviewer restrictions, native discovery, and root budgets. Publish
   the new manifest with `agent_topology`, composition mapping, and checksums
   last; run the read-only doctor. Append `prepared` before target writes,
   per-item `applied` after each change, and `verified` after final checks in the
   existing migration ledger; capture postimages in the backup run record.
9. **Report** — show reused/referenced/merged/created skills, retired agents,
   reviewer, verification evidence or unavailable loader observations, backup
   ID, and the runtime-correct `rollback` invocation. Never claim completion
   while dependencies or required gates remain unresolved.

Multi-file changes are not globally atomic. On interruption, retain the backup
and recorded per-file state, compare live files with pre/postimages, and offer
resume or rollback. Never delete a working source merely because a replacement
was planned. Re-running resumes the existing mapping or reports no-op; it must
not create duplicate skills or invent alternate names to evade collisions.

If this is a hand-authored system without a manifest/doctor, propose the minimal
managed manifest and doctor files as part of the same approved write set. Record
reused external skills as dependencies without claiming ownership or stamping
them. Inspect native discovery separately: the doctor checks local memory and
manifest consistency, not the runtime's active worker registry or dependency
execution. Require reload/new-session evidence when old workers remain active;
report the disk conversion and pending activation separately.

## Procedure (solo → specialists)

Use the same inspect → compose → approve → snapshot → emit → switch → verify
sequence. New specialist files reference the existing reusable skills; preserve
shared skills instead of deleting them. Reuse the reviewer rather than creating
a duplicate. Restore machine-enforced permissions from reviewed native source
configuration or explicit approval, never from advisory skill prose alone.

For an exact return to a pre-migration version, use `rollback` instead. Migration
synthesizes a new topology; rollback restores recorded bytes.

## Anti-patterns

- Snapshotting before the user approves, or writing before a verified snapshot.
- Deleting agent files before replacement coverage is verified.
- Copying shared skills into each role, blanket bans on useful merging, or
  concatenating every prompt into a resident god-prompt.
- Allowing extra working subagents while claiming a completed solo migration.
- Claiming a skill link auto-loads content or grants independent permissions.
- Forced conversion during `improve` / `upgrade`; they may only propose it.

OpenCode V2 sources: <https://opencode.ai/v2/docs/commands>,
<https://opencode.ai/v2/docs/skills>, <https://opencode.ai/v2/docs/permissions>.
