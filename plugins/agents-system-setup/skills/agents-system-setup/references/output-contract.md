# Output Contract

Use this contract at the end of `init`, `update`, `improve`, and `replicate` flows. Keep the user-facing summary concise; include full detail only when useful or requested. For `Compact` and `Balanced`, lead with an 8-line summary, then warnings/approvals, then detail-on-request.

```text
✅ Mode/platforms: <mode> · <selected platforms only>
✅ Footprint: <pre-existing artifacts summary>
✅ Files: created=<n>, updated=<n with .bak>, platform breakdown=<compact>
✅ Agents: subagents=<n>, skills=<n>, waves=<n>
✅ Gates: security/audit=<present|n/a>, threat model=<present|n/a>, architecture=<count|n/a>, quality gates=<summary>
✅ Context profile: <balanced|compact|full>; Context split: <inline + overflow refs>; budget=<largest surfaces>
✅ Plan handoff: <present|n/a>, task assignment quality=<short|full, required minimum filled, clarification count>
✅ Learning memory: <disabled|project-tracked|project-local|personal-global>, Learning check=<checked>/<total>, updates=<ids|none>

Warnings / approvals:
- MCP servers: <selected list> (approval: <approve-all | selective | skipped>; marker: <present|n/a>)
- Runtime format targets: <copilot .agent.md | claude .md | opencode .md | codex .toml | gemini .md | n/a>
- Artifact tracking: <project-tracked | project-local | personal-global>; Local exclude: <.git/info/exclude updated | n/a>
- Model overrides: <none — runtime defaults | scoped overrides set>
- Copilot CLI tools profile: <standard | read-only | runner | research | inherit | minimal | custom>
- Runtime drift notes: <only notes relevant to selected platforms>
- Learning updates: <new ids | updated ids | superseded ids | deferred ids | none>
- Git: <initialized | left untouched | already present>
- Wrap-up add-ons: selected=<list or none>, skipped=<list or none>

Details on request:
- Full file list by platform
- Full subagent and skill list
- Full plugin/MCP recommendation table with [Tier · Vendor]
- Full governance matrices and ADR refs
- Codex subagent files: <selected-platform only list of .codex/agents/*.toml; CLI + App compatible artifacts>
- Gemini subagent files: <selected-platform only list of .gemini/agents/*.md; non-recursive local subagents>

# replicate mode adds:
✅ Source runtime: <copilot-cli | claude-code | opencode | codex-cli | gemini-cli>
✅ Target runtimes: <list>
✅ Lossy field drops: <list per target>
✅ Round-trip verify: <pass | drift on <fields>>
✅ Replication ledger: <path>

# improve mode adds:
✅ Audit findings: <ok / warn / fail counts>
✅ Security findings: <ok / warn / fail / requires-human counts>
✅ Architecture findings: <ok / warn / fail / requires-human counts>
✅ Deltas applied: <count>
✅ Deltas skipped: <count>
✅ Requires-human: <count>

Try it:
  <render selected runtimes only; omit every unselected runtime>
  - If `copilot` selected: `copilot` then `@orchestrator <task>`; optional `copilot /fleet` for the wave plan
  - If `claude` selected: `claude` then invoke a subagent
  - If `opencode` selected: `opencode` then pick a primary or `@mention` a subagent; inspect child sessions
  - If `codex-cli` selected: `codex`; CLI can use `/agent`; CLI + App artifacts are `AGENTS.md` plus `.codex/agents/*.toml`
  - If `gemini-cli` selected: `gemini` then `@<agent-name> <task>` or rely on description-based delegation

Suggested next customizations:
  - <suggestion 1>
  - <suggestion 2>
```

## Compact summary rule

For `Compact` and `Balanced` output profiles, summarize counts and paths first. Expand full lists only when the user asked for detail or when a warning/failure needs evidence.

Always include plan handoff status when a generated system used or produced a plan. If there was no upstream plan, write `n/a — direct user request`.

Always include a `Context budget` line summarizing the largest generated context surfaces:

```text
✅ Context budget: AGENTS.md=<N> lines · largest subagent=<path>:<N> lines · skill description=<N> chars · Codex developer_instructions max=<N> lines
✅ Task assignment quality: <short-form | full-form, required minimum filled, expansion blocks: <list or "none">>
✅ Clarifications requested: <count>
```

Use the values measured at write time. If a surface is not generated for this run, use `n/a` for that field.

For Codex targets, keep `codex-cli` as the machine-readable runtime key, but label generated artifacts as **OpenAI Codex CLI + App compatible** when they are shared repo artifacts. Keep plugin install and slash-command examples explicitly CLI-only.

For Gemini targets, keep `gemini-cli` as the machine-readable runtime key. Label generated agents as **Gemini CLI local subagents**, note that `mcp_servers:` was approval-gated if present, and surface any recursive-delegation lossiness.
