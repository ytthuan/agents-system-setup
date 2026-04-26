# Output Contract

Use this contract at the end of `init`, `update`, `improve`, and `replicate` flows. Keep the user-facing summary concise; include full detail only when useful or requested.

```text
✅ Mode: <init|update|improve|replicate>
✅ Platforms: <copilot-cli, claude-code, opencode, codex-cli>
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
✅ Runtime format targets: <copilot .agent.md | claude .md | opencode .md | codex .toml | n/a>
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
✅ Codex subagent files (if codex-cli target): <list of .codex/agents/*.toml, or "none">

# replicate mode adds:
✅ Source runtime: <copilot-cli | claude-code | opencode | codex-cli>
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
  claude           # then: invoke a subagent
  opencode         # then: pick an agent
  codex            # then: /agent to switch threads; orchestrator + rules in AGENTS.md, subagents in .codex/agents/*.toml

Suggested next customizations:
  - <suggestion 1>
  - <suggestion 2>
```

## Compact summary rule

For `Compact` and `Balanced` output profiles, summarize counts and paths first. Expand full lists only when the user asked for detail or when a warning/failure needs evidence.

Always include plan handoff status when a generated system used or produced a plan. If there was no upstream plan, write `n/a — direct user request`.
