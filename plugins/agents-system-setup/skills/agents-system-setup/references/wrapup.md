# Phase 8 — Final Wrap-Up Menu

Single consolidated prompt run **after** Phase 7 (Verify & Summarize) and **before** the skill exits. Purpose: surface high-value, well-known add-ons the user may want layered on top, gated by signals already captured in earlier phases. One ask, multi-select, source-cited, opt-in.

## Decision policy

- **Trigger:** always run, unless `mode == update` and no new agents/plugins were added.
- **Presentation:** single multi-select checklist via the runtime's ask-user tool.
- **Context budget:** show only item name, source, and one-line action in the prompt. Keep extended rationale in this reference.
- **Filtering:** filter the menu by signals from Phase 1.7 (domain) + Phase 3 (selected plugins) + Phase 3.5 (MCP). Never show an item the user already installed.
- **Learning / hook de-duplication:** if Phase 1.9/1.10 already selected a Memory & Learning profile, native memory behavior, or optional hooks, do not ask for the same setup again. Only show a follow-up when the plan explicitly deferred it with a `question_request`.
- **Update de-duplication:** if Phase -1 self-update preflight already checked or updated the plugin, do not show a generic plugin update item. If preflight returned `requires-human`, include that unresolved `question_request` in the final output instead of asking again.
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
   - Source: <https://modelcontextprotocol.io/docs/concepts/architecture> and <https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices>
   - Action (only if any MCP server selected in Phase 3.5): annotate each entry in `.mcp.json` with the recommended auth/transport from the spec.
9. **NIST SSDF mapping** — secure development practice checklist.
   - Source: <https://csrc.nist.gov/Projects/ssdf>
   - Action: add an SSDF crosswalk to `AGENTS.md` Quality Gates (PO/PS/PW/RV groups) with owner and evidence columns.
10. **GitHub Code Security baseline** — secret scanning, code scanning, dependency review, Dependabot.
    - Source: <https://docs.github.com/en/code-security>
    - Action (GitHub repos): add a `## GitHub Code Security` checklist to `AGENTS.md`; optionally scaffold a CodeQL workflow only after explicit approval.
11. **SLSA provenance review** — build/release supply-chain integrity.
    - Source: <https://slsa.dev/spec/v1.1/>
    - Action (release-producing projects): append SLSA provenance / artifact verification notes to Quality Gates.
12. **OPA policy-as-code** — explicit, testable policy decisions.
    - Source: <https://www.openpolicyagent.org/docs/latest/>
    - Action (infra/platform/API gateway projects): add a policy-as-code section with candidate policy boundaries and test evidence.

### Architecture & design patterns

13. **C4 architecture views** — context/container/component views.
    - Source: <https://c4model.com/>
    - Action: add a C4 view plan to `AGENTS.md` Architecture section; scaffold docs only after approval.
14. **ADR index** — architecture decisions with status.
    - Source (pattern): C4 / architecture documentation conventions; enterprise option: <https://www.opengroup.org/togaf>
    - Action: add `docs/adr/` plan and ADR index rows; create files only after approval.
15. **Azure Well-Architected review** — cloud quality pillars.
    - Source: <https://learn.microsoft.com/en-us/azure/well-architected/>
    - Action (Azure/cloud target): add reliability/security/cost/operational/performance review gates.

### Additional well-known subagents

16. **awesome-copilot agent gallery** — curated GitHub-Copilot-CLI agents.
    - Source: <https://github.com/github/awesome-copilot> (subdir: `agents/`)
    - Action (Copilot target): present a sub-menu of agents not yet installed; replicate selections through the Canonical IR.
17. **wshobson/agents** — large multi-runtime subagent collection.
     - Source: <https://github.com/wshobson/agents>
     - Action: same flow as #16.
18. **VoltAgent/awesome-claude-code-subagents** — curated Claude Code subagents.
     - Source: <https://github.com/VoltAgent/awesome-claude-code-subagents>
     - Action (Claude target): same flow as #16.
19. **Gemini CLI extension gallery** — discover Gemini extensions that can bundle subagents, MCP servers, commands, hooks, and skills.
     - Source: <https://geminicli.com/extensions/browse/> and <https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/index.md>
     - Action (Gemini target): present a source-inspected extension submenu; never install or write MCP config without the approval gate.

### Operations

20. **Prompt versioning / changelog** — per-agent CHANGELOG for prompt drift.
     - Source (pattern): Anthropic prompt-engineering docs <https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview>; OpenAI prompt-engineering guide <https://platform.openai.com/docs/guides/prompt-engineering>.
     - Action: scaffold `prompts/CHANGELOG.md` and a `prompts/` dir mirror of each agent's instructions.
21. **Cost / usage budgeting** — per-provider usage caps.
     - Source: Anthropic <https://docs.claude.com/en/api/admin-api/usage-cost/get-usage-report>; OpenAI <https://platform.openai.com/docs/guides/production-best-practices/managing-rate-limits>.
     - Action: append a `## Budgets` section to `AGENTS.md` with target $/day per agent + alert hook.

## Filter matrix

| Signal from earlier phases     | Items shown                              |
|--------------------------------|------------------------------------------|
| domain == software-dev         | 1, 2 (always also: 3–15, 20, 21)         |
| domain != software-dev         | 3–8, 13, 14, 20, 21                      |
| any MCP server selected        | 8 (always)                               |
| GitHub repo detected           | 10                                       |
| release/package/CI detected    | 11                                       |
| infra/platform/API gateway     | 12                                       |
| cloud/Azure target             | 15                                       |
| Claude target included         | 6, 18                                    |
| Copilot target included        | 16                                       |
| Multi-runtime                  | 17                                       |
| Gemini target included         | 19                                       |

## Output addendum

After the wrap-up menu runs, append to the Phase 7 Output Contract:

```
✅ Wrap-up add-ons selected: <list with source URL>
✅ Wrap-up add-ons skipped: <list>
```

## Anti-patterns

- Asking the wrap-up question one item at a time (must be a single multi-select).
- Dumping the full catalog into the final response; show the filtered compact menu only.
- Showing items already installed.
- Auto-installing without per-item confirmation when the action edits config beyond `AGENTS.md`.
- Citing unofficial third-party blog posts. Only vendor docs or the catalogs listed above.
