<!-- Conditionally inserted into local project policy, with a root load trigger,
     when Phase 1.7 records spec_kit_installed = true.
     Skip this entire block (do not emit the placeholder line) when false. -->

## Spec-Driven Workflow (via Spec-Kit)

This project uses [GitHub Spec-Kit](https://github.com/github/spec-kit) for the
upstream "what to build" layer. Use the installed integration's advertised
commands for these steps; do not assume every version uses the same spelling:

1. `/specify` — capture what the user wants in plain language.
2. `/plan` — turn the spec into a checked plan with constraints.
3. Normalize delegated assignments through the indexed `task-delegation` skill.
4. `/tasks` — break the plan into atomic, parallel-safe tasks.
5. The host assigns actual owners from the Capability Matrix, executing directly
   or delegating when justified.
6. `/implement` only after the host approves the applicable plan and gates.

Tool detection does not prove project initialization. Installation and
`specify init` remain separate approved actions, never implied by this policy.
