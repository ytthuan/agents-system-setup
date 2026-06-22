# Parallel Subagents & Claude Code Agent Teams

Generated agent systems must exploit parallelism wherever the work is independent. This is not optional — sequential-only topologies waste wall-clock and burn the user's context.

## Three distinct primitives

| Primitive | What it is | Where it lives | Coordination model |
|---|---|---|---|
| **Parallel subagents** | Multiple subagent invocations in **one orchestrator turn**, each in its own context window or child session | Copilot CLI (`Task`/`agent` tools and optional `/fleet`), Claude Code (tool-based subagents), OpenCode (`task` + `@agent`), OpenAI Codex (child agent threads), Gemini CLI (root agent calls subagent tools / `@agent`) | Fan-out from one orchestrator; results return to the orchestrator only |
| **Agent teams** (Claude Code only, experimental) | Independent Claude instances that **message each other directly**, with a shared task list | Claude Code only — requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | Lead + teammates; teammates communicate peer-to-peer |
| **Cross-session orchestration** (GitHub Copilot app only) | Each unit of work runs in its **own session = worktree + branch + PR**; sessions can message each other and nest under the spawner | GitHub Copilot app host via `/orchestrate` + `create_session` (wraps a Copilot CLI session) | Host orchestrator promotes parallel-safe units to child sessions/PRs; advisory, never a generated-file dependency |

Sources: https://docs.github.com/en/copilot/concepts/agents/copilot-cli/fleet · https://docs.anthropic.com/en/docs/claude-code/sub-agents · https://docs.anthropic.com/en/docs/claude-code/agent-teams · https://opencode.ai/docs/agents/ · https://developers.openai.com/codex/subagents · https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md · GitHub Copilot app v0.2.33 release notes: https://github.com/github/app/releases/tag/v0.2.33

## When to use which (decision flow)

```
Is the work independent across N domains?
├─ No  → single subagent (or sequential chain)
└─ Yes → does the user want results synthesized centrally?
         ├─ Yes → PARALLEL SUBAGENTS (fan-out + collect)
         └─ No, teammates need to challenge each other
                / share findings as they go
                → AGENT TEAM (Claude Code only;
                  fall back to parallel subagents on other runtimes)
```

## Parallel-readiness derived from Directory Architecture

A subagent is **parallel-safe** when:
1. Its `owns_paths` glob doesn't overlap any other subagent's `owns_paths`.
2. It doesn't write outside its owned paths.
3. It doesn't depend on the output of another subagent in the same wave.

The generator computes parallel-safety automatically from the Directory Architecture and tags each subagent in the Agent Roster:

| name | role | owns | parallel-safe | wave |
|---|---|---|---|---|
| `frontend-dev` | UI work | `web/**` | ✅ | 1 |
| `backend-dev` | API work | `server/**` | ✅ | 1 |
| `db-migrations` | schema | `db/**` | ✅ | 1 |
| `integration-tester` | end-to-end | `tests/integration/**` | ⚠️ depends on wave 1 | 2 |
| `release-notes` | docs | `CHANGELOG.md` | ⚠️ depends on wave 2 | 3 |

The orchestrator prompt (Phase 4) is rendered with explicit fan-out instructions per wave.

## Cross-session orchestration (GitHub Copilot app)

The third primitive promotes a unit of work to its **own session = own worktree + branch + PR** (one session per branch/PR), driven by the GitHub Copilot app's `/orchestrate` command and `create_session`. Sessions can message each other and nest under the session that spawned them. It is **host-app-specific and advisory**: generated files never depend on it, and non-Copilot runtimes — and Copilot CLI run outside the app — simply ignore this section.

This is the highest-value axis for a single generated agent system: most systems live in one repo, and splitting a large change into a reviewable fan-out (or stack) of per-owner PRs maps directly onto the roster's ownership zones (1 session ≈ 1 branch ≈ 1 PR ≈ 1 owner slice).

### From waves to sessions — decision procedure

The parallel-safety predicate above (non-overlapping `owns`, no cross-deps, no shared-state writes) is a **first-pass candidate filter** for which roster units could become independent child sessions / parallel PRs — necessary but **not sufficient**. Before promoting a wave unit to its own session, layer these cross-session caveats:

1. **Path-disjoint is not integration-safe.** `server/**` and `web/**` are parallel-safe on disk, but an API-contract change in one PR and its client change in another are a *logical* merge/build conflict. Treat the predicate as "low merge-conflict risk," not a guarantee.
2. **Wave N to N+1 is not a free stacked PR.** Cross-session, "wave N done" means **PR N merged** — gated by human review and CI, possibly out of order, and a squash-merge can orphan a child branched off it (`base_branch` = layer N's branch inherits the full stacked-PR rebase burden).
3. **High-churn shared files get worse, not handled.** N independent PRs each appending to `CHANGELOG`, lockfiles, i18n catalogs, or generated manifests are guaranteed conflict magnets. Exclude high-churn shared files from per-session scope and **integrate them last in one session**.
4. **Name the integration gate.** No session sees the fully integrated tree before merge, so "never weaken gates" requires specifying *where* the integration gate runs — base-branch post-merge CI, or a dedicated integration session — not just per-PR CI.

### Constraints

- Only the **host orchestrator session** spawns and steers sessions. **Subagents never orchestrate sessions**; if a subagent needs cross-session fan-out it `return-to-orchestrator`.
- Every child session still obeys the Directory Architecture, Build Gate ownership, and the MCP approval gate — a session is a different *container* for the same governed unit, never a way around a gate.
- **Out of scope here:** cloud sessions and cross-repo / multi-workspace fan-out. This section is intra-repo multi-session.

## Orchestrator prompt patterns (per runtime)

### Copilot CLI / OpenCode / OpenAI Codex / Gemini CLI (parallel subagents)

```markdown
## Wave Execution

<!-- agents-system-setup:wave-execution -->

For independent work, **fan out**: invoke all parallel-safe subagents in a
single turn using the runtime's native subagent call surface (Task/agent tool,
@agent, or child agent threads). Wait for all results. Synthesize. Then start
the next wave.

Sequential is the default ONLY when:
- A subagent's owns_paths overlap another's
- A subagent's input is the previous subagent's output
- A subagent must touch shared state (the AGENTS.md or release notes)

Never serialize parallel-safe work.
```

Runtime-specific notes:
- **Copilot CLI:** use Task/agent calls when the orchestrator must synthesize results. `/fleet` is optional CLI UX for independent batches that do not need provider-agnostic generated files to depend on it. Under the **GitHub Copilot app**, `/orchestrate` additionally promotes parallel-safe units to child sessions/PRs — see [Cross-session orchestration](#cross-session-orchestration-github-copilot-app).
- **OpenCode:** primary agents can invoke subagents automatically or via `@<agent-name>`; gate this with `permission.task` wildcard deny/ask plus named roster allows.
- **Codex:** child agent threads are explicitly requested and visible in the CLI/App. Use `.codex/config.toml` `[agents] max_threads = 6`, `max_depth = 1` as safe defaults. Keep `/agent` and `codex exec` as optional CLI usage notes only.
- **Gemini CLI:** subagents cannot recursively call other subagents. Keep all parallel fan-out in the root/orchestrator session and tell workers to return cross-boundary work rather than delegating.

### Claude Code (agent team option)

```markdown
## Coordination protocol

When the user's task spans 3+ independent concerns AND benefits from
peer-to-peer challenge (architecture vs UX vs devil's advocate;
competing debug hypotheses; cross-layer refactors):

1. Confirm `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is set.
2. Spawn an agent team with one teammate per concern.
3. Provide the shared task list; teammates self-coordinate.
4. For risky tasks, require plan approval before implementation.

Otherwise, default to parallel subagents (fan-out / collect).
```

Claude decision rule: use **subagents** when workers only need to return results to the main session; use the **Agent tool** as the invocation mechanism for those subagents; use **agent teams** only when independent Claude instances need to discuss, challenge findings, claim tasks, or coordinate without routing every message through the lead.

## Generator obligations

When emitting subagents and orchestrator, the skill MUST:

1. **Compute waves** from the Directory Architecture and emit the wave table in `AGENTS.md`.
2. **Render the parallel-execution clause** in the orchestrator prompt for every runtime.
3. **For Claude Code projects**, also emit an `AGENT-TEAMS.md` snippet documenting:
   - When to enable agent teams (3+ independent concerns + peer challenge value)
   - The env var (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) plus a settings.json snippet
   - Suggested teammate roster (drawn from the Agent Roster, marked `team-suitable`)
4. **Token-cost warning**: agent teams cost N× tokens (one Claude instance per teammate). Surface this in the AGENT-TEAMS.md so users opt in knowingly.
5. **When Copilot CLI/app is a selected runtime**, render the Copilot-app cross-session advisory: a note in the `AGENTS.md` › Platform-native delegation Copilot row plus a Wave Execution bullet, both pointing at the [Cross-session orchestration](#cross-session-orchestration-github-copilot-app) section. **Advisory only** — never emit a first-class app-specific block into the shared `AGENTS.md` (it is copied to `CLAUDE.md`/`GEMINI.md` and read natively by Codex/OpenCode, so an app-only primitive there would leak into every runtime's context).

## Anti-patterns

- **Sequential-only orchestrator** — burns wall-clock when the work is independent. The default must be fan-out for parallel-safe subagents.
- **Parallel writes to overlapping paths** — race condition on disk; one subagent's write is overwritten silently. The Directory Architecture is the lock.
- **Agent teams for trivial tasks** — coordination overhead and token cost outweigh benefit. Use parallel subagents instead.
- **Agent teams without the env var** — silently falls back to single-session behavior.
- **Forgetting wave 2+ depends on wave 1** — orchestrator must `await` wave N before starting wave N+1.
- **A first-class cross-session block in the shared `AGENTS.md`** — leaks a Copilot-app-only primitive into `CLAUDE.md`/`GEMINI.md`/Codex/OpenCode. Keep cross-session orchestration advisory, in the Copilot delegation cell and a Wave Execution note.
- **Subagents spawning sessions** — cross-session orchestration is host-orchestrator-only; subagents `return-to-orchestrator` when work exceeds their owned surface.
- **Treating parallel-safe as merge-safe** — path-disjoint PRs can still be a logical/integration conflict; the predicate is a candidate filter, not a guarantee.
