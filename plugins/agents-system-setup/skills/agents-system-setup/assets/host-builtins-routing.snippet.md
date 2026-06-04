<!-- markdownlint-disable MD024 -->
<!-- This snippet renders the `### Native Runtime Agents` subsection inside `## Orchestration Operating Model` of generated AGENTS.md. -->
<!-- Profile-aware emission: Balanced/Full → full block. Compact → 1-2 line summary variant. Single-agent → omit. -->
<!-- Anchor literal `<!-- agents-system-setup:host-builtins-routing -->` MUST be preserved for validator. -->

<!-- Full variant: Balanced/Full, subagent_count >= 2. -->

<!-- agents-system-setup:host-builtins-routing -->

### Native Runtime Agents

**Audience:** host-orchestrator

The host orchestrator (this CLI session) MAY route work to native runtime
built-in agents instead of (or in addition to) the custom subagent roster.
Native built-ins are the host runtime's own subagents — they keep the main
conversation context lean by handling verbose work in their own context window.

| Runtime | Explore-class (broad recon) | Task-class (verbose command execution) |
|---|---|---|
| GitHub Copilot CLI | `task` tool, `agent_type: "explore"` | `task` tool, `agent_type: "task"` (brief on success / full on failure) |
| Claude Code | `Explore` built-in subagent | `general-purpose` built-in subagent |
| OpenCode | `@explore` subagent | `@general` subagent |
| OpenAI Codex (CLI + App) | `explorer` built-in | **No task-class built-in.** Spawn a custom worker subagent, route to `@build-runner`, or run in root session |
| Gemini CLI | `@codebase_investigator` | **No task-class built-in.** Root session runs commands directly or delegates to `@build-runner`; subagents cannot recurse |

**When to route to explore-class:** broad recon where parallel reading would
otherwise consume the main context (`source_files > 50` OR `top_level_dirs > 8`
OR `frameworks_detected > 3` OR `recon_threads_requested > 2`).

**When to route to task-class:** verbose one-off command execution where only
success/failure matters (smoke build, single test run, lint check, dependency
install verification).

**Ownership boundary (fail-closed):** Build Gate evidence stays with
`@build-runner`, `@tester`, `@playwright-e2e`, `@change-bug-hunter`,
`@reviewer`, and `@change-validator`. Native task-class built-ins are the
execution substrate for **ad-hoc non-gate checks only**; their output is labelled
`non-gate evidence` and does NOT satisfy Build Gate evidence requirements (see
[sdlc-build-gate](https://github.com/ytthuan/agents-system-setup/blob/main/plugins/agents-system-setup/skills/agents-system-setup/references/sdlc-build-gate.md)).

**Subagent rule:** Subagents never re-delegate to native built-ins (hard rule #36).
If a subagent needs host-level command execution outside its allowed surface, it
returns `return-to-orchestrator` with the command and required evidence shape;
the orchestrator then chooses between the custom subagent and the native
built-in.

**OpenCode gate:** When this section is emitted for an OpenCode target,
`opencode.json` `permission.task` MUST allow `explore` and `general` (allow
entries proposed during Phase 4). If declined, this section becomes advisory and
the output contract records `host_builtins_routing: declined`.

<!-- Compact variant: profile=Compact AND subagent_count >= 2. -->

<!-- agents-system-setup:host-builtins-routing -->

### Native Runtime Agents

**Audience:** host-orchestrator

Host orchestrator MAY route broad recon to the runtime's `explore`-class
built-in (Copilot `explore` / Claude `Explore` / OpenCode `explore` / Codex
`explorer` / Gemini `codebase_investigator`) and verbose ad-hoc command
execution to its `task`-class built-in (Copilot `task` / Claude
`general-purpose` / OpenCode `general`; Codex & Gemini have no task-class
built-in — use custom worker / `@build-runner` / root session). Build Gate
evidence stays with named owners. See
[host-builtins-routing](https://github.com/ytthuan/agents-system-setup/blob/main/plugins/agents-system-setup/skills/agents-system-setup/references/host-builtins-routing.md).

<!-- Renderer:
     - subagent_count < 2 → emit empty string, skip section
     - profile == "compact" AND subagent_count >= 2 → emit Compact variant
     - profile in ("balanced","full") AND subagent_count >= 2 → emit Full variant
     - For OpenCode targets, ALSO emit `permission.task` allow entries for `explore` and `general` in opencode.json proposal (Phase 4 OpenCode root-session task gate).
     - Preserve the `<!-- agents-system-setup:host-builtins-routing -->` anchor exactly in every non-empty variant.
     - Insert only into generated `AGENTS.md` host-orchestrator context.
     - Do not insert this block into subagent templates.
     - Label native task-class output as `non-gate evidence`.
     - Keep Build Gate evidence with generated named owners.
-->
