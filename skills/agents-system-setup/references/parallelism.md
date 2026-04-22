# Parallel Subagents & Claude Code Agent Teams

Generated agent systems must exploit parallelism wherever the work is independent. This is not optional — sequential-only topologies waste wall-clock and burn the user's context.

## Two distinct primitives

| Primitive | What it is | Where it lives | Coordination model |
|---|---|---|---|
| **Parallel subagents** | Multiple `Task`-tool invocations in **one orchestrator turn**, each in its own context window | Copilot CLI, Claude Code, OpenCode, Codex CLI (any runtime with a Task-equivalent tool) | Fan-out from one orchestrator; results return to the orchestrator only |
| **Agent teams** (Claude Code only, experimental) | Independent Claude instances that **message each other directly**, with a shared task list | Claude Code only — requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | Lead + teammates; teammates communicate peer-to-peer |

Source: https://docs.anthropic.com/en/docs/claude-code/sub-agents · https://docs.anthropic.com/en/docs/claude-code/agent-teams

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

## Orchestrator prompt patterns (per runtime)

### Copilot CLI / OpenCode / Codex (parallel subagents)

```markdown
## Coordination protocol

For independent work, **fan out**: invoke all parallel-safe subagents in a
single turn using multiple Task-tool calls in one response. Wait for all
results. Synthesize. Then start the next wave.

Sequential is the default ONLY when:
- A subagent's owns_paths overlap another's
- A subagent's input is the previous subagent's output
- A subagent must touch shared state (the AGENTS.md or release notes)

Never serialize parallel-safe work.
```

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

## Generator obligations

When emitting subagents and orchestrator, the skill MUST:

1. **Compute waves** from the Directory Architecture and emit the wave table in `AGENTS.md`.
2. **Render the parallel-execution clause** in the orchestrator prompt for every runtime.
3. **For Claude Code projects**, also emit an `AGENT-TEAMS.md` snippet documenting:
   - When to enable agent teams (3+ independent concerns + peer challenge value)
   - The env var (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) plus a settings.json snippet
   - Suggested teammate roster (drawn from the Agent Roster, marked `team-suitable`)
4. **Token-cost warning**: agent teams cost N× tokens (one Claude instance per teammate). Surface this in the AGENT-TEAMS.md so users opt in knowingly.

## Anti-patterns

- **Sequential-only orchestrator** — burns wall-clock when the work is independent. The default must be fan-out for parallel-safe subagents.
- **Parallel writes to overlapping paths** — race condition on disk; one subagent's write is overwritten silently. The Directory Architecture is the lock.
- **Agent teams for trivial tasks** — coordination overhead and token cost outweigh benefit. Use parallel subagents instead.
- **Agent teams without the env var** — silently falls back to single-session behavior.
- **Forgetting wave 2+ depends on wave 1** — orchestrator must `await` wave N before starting wave N+1.
