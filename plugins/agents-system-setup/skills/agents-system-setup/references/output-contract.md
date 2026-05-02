# Output Contract

Use this contract at the end of `init`, `update`, `improve`, and `replicate` flows. Keep the user-facing summary concise; include full detail only when useful or requested.

```text
✅ Mode: <init|update|improve|replicate>
✅ Platforms: <copilot-cli, claude-code, opencode, codex-cli (OpenAI Codex CLI + App artifacts), gemini-cli>
✅ Detected footprint: <list of pre-existing artifacts, or "none">
✅ Files created: <count>     (per platform: <breakdown>)
✅ Files updated (with .bak): <count>
✅ Subagents: <list>
✅ Skills: <list>
✅ Plugins selected: <list with [Tier · Vendor] and /plugin install (or platform-equivalent)>
✅ Plugins skipped: <list>
✅ MCP servers: <selected list> (approval: <approve-all | selective | skipped>)
✅ Context profile: <balanced | compact | full>
✅ Context split: <inline sections + overflow reference paths>
✅ Largest memory file: <path + approximate line count>
✅ Plan handoff: <present | n/a with rationale> (source: <VS Code plan prompt | Spec-Kit /plan | user plan | none>)
✅ Runtime format targets: <copilot .agent.md | claude .md | opencode .md | codex .toml (CLI + App compatible artifacts) | gemini .md | n/a>
✅ Model overrides: <none — runtime defaults | per-agent overrides set: <agent → id list>>
✅ Copilot CLI tools profile: <standard | read-only | runner | research | inherit | minimal | custom> (per Q9c; standard renders as `tools: [vscode, execute, read, agent, edit, search, todo]` for orchestrator + edit-capable, narrows to `[read, search]` for reviewers/auditors)
✅ Runtime drift notes: <none | Copilot .agent.md/.md docs drift + tool aliases + standard tool profile | Claude plugin/project schema split + agent teams | OpenCode permission migration + child sessions | Codex additive schema + CSV/plugin config | Gemini promoted + mcp_servers normalization>
✅ Artifact tracking: <project-tracked | project-local | personal-global>
✅ Local exclude: <.git/info/exclude updated | n/a>
✅ Security & audit baseline: <present | n/a with rationale>
✅ Threat model: <present | n/a with rationale>
✅ Architecture decisions: <count + ADR refs, or n/a with rationale>
✅ Quality gates: <build/test/lint/security/supply-chain/architecture evidence>
✅ Project memory link: <symlink | copy | n/a>
✅ Git: <initialized | left untouched | already present>
✅ Wrap-up add-ons selected: <list with source URL, or "none">
✅ Wrap-up add-ons skipped: <list, or "none">
✅ Codex subagent files (if codex-cli target): <list of .codex/agents/*.toml, or "none"; generated as CLI + App compatible artifacts>
✅ Gemini subagent files (if gemini-cli target): <list of .gemini/agents/*.md, or "none"; non-recursive local subagents>

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
  copilot          # then: "@orchestrator <task>"
  copilot /fleet   # optional: ask Copilot to parallelize the wave plan
  claude           # then: invoke a subagent
  opencode         # then: pick a primary or @mention a subagent; inspect child sessions
  codex            # CLI: /agent to switch threads; CLI + App artifacts: AGENTS.md plus .codex/agents/*.toml
  gemini           # then: "@<agent-name> <task>" or rely on description-based delegation

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
