<!-- agents-system-setup:code-quality-standards:start -->

> **Coding agents apply these standards while writing code — not only at review.**
> The Build Gate verifies a change; this is the craft applied during authoring.
> Full procedure: the host-loaded `code-quality` skill. Reference:
> [code-quality](https://github.com/ytthuan/agents-system-setup/blob/main/plugins/agents-system-setup/skills/agents-system-setup/references/code-quality.md).

**Strictness:** {{CODE_QUALITY_STRICTNESS}}  <!-- standard | strict | light | advisory | skipped | n/a -->

### Rule 0 — Conform to existing conventions first

Before writing, **detect and obey the project's configured tooling** —
`.editorconfig`, ESLint/Prettier, Ruff/Black, `gofmt`/golangci-lint,
rustfmt/Clippy, Checkstyle, SwiftLint, ktlint, RuboCop, `pre-commit`, etc. —
and match the naming, layout, error-handling, and test patterns already used in
neighbouring files. Do not introduce a new style, formatter, or framework unless
the task requires it and the plan approved it.

### Authoring standards

- **Naming** reveals intent; searchable, pronounceable; language casing.
- **Units** do one thing, stay short and shallow; early returns over deep
  nesting; keep branching/complexity bounded.
- **DRY** — one authoritative representation; extract real duplication only
  (no speculative generality / YAGNI).
- **Errors** fail fast and explicitly; validate at boundaries; never swallow a
  failure or fake success.
- **Comments** explain the non-obvious *why*, not the *what*; delete dead code
  and commented-out blocks; name magic values.
- **Tests** ship with new behaviour; bug fixes ship with a regression test;
  cover edge and failure paths; never weaken tests to pass.
- **Formatting** defers to the project's formatter; do not reformat unrelated
  lines.

### Verdict

`code-quality-reviewer` (or `@reviewer` when merged) reports code smells —
`convention-drift`, `poor-naming`, `long-unit`, `deep-nesting`, `duplication`,
`swallowed-error`, `magic-value`, `dead-code`, `weak-tests`, `over-engineering`,
`tight-coupling`, `stale-comment` — and `@change-validator` folds the verdict
into the Build Gate review evidence.

**Output marker:** `Code quality: <ok|warn|fail|n/a>; reviewer=<separate|merged|skipped>; signals=<list|none>`

<!-- agents-system-setup:code-quality-standards:end -->
