# Phase 8 — Final Wrap-Up Menu

Single consolidated prompt run **after** Phase 7 (Verify & Summarize) and **before** the skill exits. Purpose: surface high-value, well-known add-ons the user may want layered on top, gated by signals already captured in earlier phases. One ask, multi-select, source-cited, opt-in.

## Decision policy

- **Trigger:** always run, unless `mode == update` and no new agents/plugins were added.
- **Presentation:** single multi-select checklist via the runtime's ask-user tool.
- **Filtering:** filter the menu by signals from Phase 1.7 (domain) + Phase 3 (selected plugins) + Phase 3.5 (MCP). Never show an item the user already installed.
- **Execution:** for each selected item, prefer dispatching to an existing dedicated skill. If none, run the inline action documented below.
- **No silent installs.** Every item still carries its own confirmation if it writes files or edits config beyond `AGENTS.md` notes.

## Catalog (source-backed)

Every item below cites a vendor-official doc or a well-known curated catalog. Update URLs only when upstream renames a path — never invent.

### Software-development add-ons (gated by Phase 1.7 = software-dev)

1. **GitHub Spec-Kit** — spec-driven dev workflow.
   - Source: <https://github.com/github/spec-kit>
   - Action: dispatch to local `spec-kit` skill if present, else append a `## Spec-Kit` section to `AGENTS.md` with install instructions (`uvx --from git+https://github.com/github/spec-kit specify init`).
2. **CI guardrails for AGENTS.md & manifests** — lint AGENTS.md, validate plugin/MCP JSON.
   - Source (pattern): <https://github.com/ytthuan/agents-system-setup/blob/main/scripts/validate.sh>
   - Action: copy a minimal `validate.sh` + GH Actions workflow stub into the user repo's `scripts/` and `.github/workflows/`.

### Evals & quality

3. **Anthropic evals cookbook** — building an eval harness for prompts/agents.
   - Source: <https://github.com/anthropics/anthropic-cookbook/tree/main/misc> (see `building_evals.ipynb`)
   - Action: scaffold `evals/README.md` referencing the notebook + a stub `evals/cases.jsonl`.
4. **OpenAI Evals** — framework for systematic eval runs.
   - Source: <https://github.com/openai/evals>
   - Action: append a `## Evals` block to `AGENTS.md` with `pip install evals` and a 1-screen quickstart.

### Telemetry & observability

5. **OpenTelemetry GenAI semantic conventions** — vendor-neutral tracing schema for LLM calls.
   - Source: <https://opentelemetry.io/docs/specs/semconv/gen-ai/>
   - Action: add a `## Telemetry` section to `AGENTS.md` listing the env vars and span attributes the orchestrator/subagents should emit.
6. **Claude Code hooks** — pre/post-tool hooks for logging, redaction, policy.
   - Source: <https://docs.claude.com/en/docs/claude-code/hooks>
   - Action (Claude target only): scaffold `.claude/hooks/README.md` with a no-op `PreToolUse` example.

### Security

7. **OWASP LLM Top-10** — threat model checklist.
   - Source: <https://owasp.org/www-project-top-10-for-large-language-model-applications/>
   - Action: append a `## Security Review` checklist to `AGENTS.md` with the 10 categories and a column for "owner / status".
8. **MCP server security guidance** — auth, transports, secrets.
   - Source: <https://modelcontextprotocol.io/docs/concepts/architecture> and <https://modelcontextprotocol.io/specification/2025-06-18/basic/security>
   - Action (only if any MCP server selected in Phase 3.5): annotate each entry in `.mcp.json` with the recommended auth/transport from the spec.

### Additional well-known subagents

9. **awesome-copilot agent gallery** — curated GitHub-Copilot-CLI agents.
   - Source: <https://github.com/github/awesome-copilot> (subdir: `agents/`)
   - Action (Copilot target): present a sub-menu of agents not yet installed; replicate selections through the Canonical IR.
10. **wshobson/agents** — large multi-runtime subagent collection.
    - Source: <https://github.com/wshobson/agents>
    - Action: same flow as #9.
11. **VoltAgent/awesome-claude-code-subagents** — curated Claude Code subagents.
    - Source: <https://github.com/VoltAgent/awesome-claude-code-subagents>
    - Action (Claude target): same flow as #9.

### Operations

12. **Prompt versioning / changelog** — per-agent CHANGELOG for prompt drift.
    - Source (pattern): Anthropic prompt-engineering docs <https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview>; OpenAI prompt-engineering guide <https://platform.openai.com/docs/guides/prompt-engineering>.
    - Action: scaffold `prompts/CHANGELOG.md` and a `prompts/` dir mirror of each agent's instructions.
13. **Cost / usage budgeting** — per-provider usage caps.
    - Source: Anthropic <https://docs.claude.com/en/api/admin-api/usage-cost/get-usage-report>; OpenAI <https://platform.openai.com/docs/guides/production-best-practices/managing-rate-limits>.
    - Action: append a `## Budgets` section to `AGENTS.md` with target $/day per agent + alert hook.

## Filter matrix

| Signal from earlier phases     | Items shown                              |
|--------------------------------|------------------------------------------|
| domain == software-dev         | 1, 2 (always also: 3–8, 12, 13)          |
| domain != software-dev         | 3–8, 12, 13                              |
| any MCP server selected        | 8 (always)                               |
| Claude target included         | 6, 11                                    |
| Copilot target included        | 9                                        |
| Multi-runtime                  | 10                                       |

## Output addendum

After the wrap-up menu runs, append to the Phase 7 Output Contract:

```
✅ Wrap-up add-ons selected: <list with source URL>
✅ Wrap-up add-ons skipped: <list>
```

## Anti-patterns

- Asking the wrap-up question one item at a time (must be a single multi-select).
- Showing items already installed.
- Auto-installing without per-item confirmation when the action edits config beyond `AGENTS.md`.
- Citing unofficial third-party blog posts. Only vendor docs or the catalogs listed above.
