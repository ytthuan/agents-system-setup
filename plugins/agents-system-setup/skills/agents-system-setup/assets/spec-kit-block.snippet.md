<!-- Conditionally inserted into AGENTS.md / CLAUDE.md / runtime-equivalent
     when Phase 1.7 records spec_kit_installed = true.
     Skip this entire block (do not emit the placeholder line) when false. -->

## Spec-Driven Workflow (via Spec-Kit)

This project uses [GitHub Spec-Kit](https://github.com/github/spec-kit) for the upstream "what to build" layer. Drive intent through Spec-Kit before fanning out to subagents:

1. `/specify` — capture what the user wants in plain language.
2. `/plan` — turn the spec into a checked plan with constraints.
3. `/tasks` — break the plan into atomic, parallel-safe tasks.
4. The orchestrator routes each task to the matching subagent per the **Capability × Agent Matrix** above.
5. `/implement` only after the orchestrator greenlights the wave.

Bootstrap (one-time): `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git`
Init (per project, already done): `specify init --here --ai {{RUNTIME}}`
