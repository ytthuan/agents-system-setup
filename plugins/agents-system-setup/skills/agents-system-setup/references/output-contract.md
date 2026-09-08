# Output Contract

Use this contract at the end of `init`, `update`, `improve`, and `replicate` flows. Keep the user-facing summary concise; include full detail only when useful or requested. For `Compact` and `Balanced`, lead with a compact summary, then warnings/approvals, then detail-on-request.

```text
✅ Mode/platforms: <mode> · <selected platforms only>
✅ Footprint: <pre-existing artifacts summary>
✅ Native initialization: runtime=<active>; source=<native|existing|fallback>; requested=<path>; observed=<paths|none>; reason=<when unavailable/conflicting>
✅ Purpose: <headline | exploring>
✅ Recon: <signals|n/a|skipped>; redactions=<count|none>
✅ Path migration: <none|moved=N copied=N skipped=N manual=N failed=N>
✅ Files: created=<n>, updated=<n with .bak>, platform breakdown=<compact>
✅ Agents: subagents=<n>, skills=<n>, waves=<n>
✅ Requirements triage: <separate|merged|skipped>; ambiguities=<n>; triage_question_requests=<count|none>; routing=<wave_0 summary|n/a>
✅ Gates: security/audit=<present|n/a>, threat model=<present|n/a>, architecture=<count|n/a>, quality gates=<summary>
✅ Update preflight: <checked|already-current|ff-updated|requires-human|skipped>; source=<path-or-manager>; evidence=<git range|question_request id|n/a>
✅ Human input: <native matrix rendered|question_request fallback|disabled>; unresolved=<count|none>
✅ Context profile: <balanced|compact|full>; Context split: <inline + overflow refs>; budget=<largest surfaces>
✅ Plan handoff: <present|n/a>, task assignment quality=<ok|warn|fail; form=<short|full>; missing=<fields|none>; questions=<count>>
✅ Task assignment quality: <ok|warn|fail; form=<short|full>; missing=<fields|none>; questions=<count>>
✅ Content quality: <ok|warn|fail|n/a>; curator=<separate|merged|skipped>; signals=<list|none>
✅ Security team: <baseline|dedicated|expanded|n/a>; roles=<count|n/a>; scope=<diff|repository|report|remediation|program|n/a>; authorization=<owned-code|approved-target|requires-human|n/a>
✅ Learning memory: <disabled|project-tracked|project-local|personal-global>, native=<documented|enabled|disabled>, Learning check=<checked>/<total>, updates=<ids|none>

Warnings / approvals:
- MCP servers: <selected list> (approval: <approve-all | selective | skipped>; marker: <present|n/a>)
- Runtime format targets: <copilot .agent.md | claude .md | opencode .md | codex .toml | gemini .md | n/a>
- Artifact tracking: <project-tracked | project-local | personal-global>; Local exclude: <.git/info/exclude updated | n/a>
- Path migration ledger: `.agents-system-setup/migration.jsonl` (operational state; never inside any agents/skills/hooks/commands/prompts/plugins tree)
- Model policy: <adaptive-balanced|explicit pins>; runtime controls=<available|inherit-only>; provider/budget constraints=<recorded|unknown>; cost claims=<measured|estimated|unavailable>
- Model overrides: <none — static fields omitted | scoped pins preserved>
- Memory repair: <not-needed|approved|declined|requires-human>; retained rules=<summary>; relocations=<local paths>; conflicts=<none|unresolved>
- Native loading: <observed evidence per runtime|unavailable>; next-session/reload requirement=<runtime-specific|none>
- Copilot CLI tools profile: <standard | read-only | runner | research | inherit | minimal | custom>
- Runtime drift notes: <only notes relevant to selected platforms>
- Human-input approvals: <native tool used | question_request ids | none>
- Task assignment quality: <ok | warn | fail; form=<short | full>; missing=<fields | none>; questions=<count>>
- Requirements triage: <intake brief used | merged into planner | skipped with rationale>
- Content-quality review: <curator report | merged reviewer check | skipped with rationale>
- Security-team evidence: <authorization scope | candidate count | confirmed/suppressed/deferred counts | proof gaps | n/a>
- Learning updates: <new ids | updated ids | superseded ids | deferred ids | none>
- Git: <initialized | left untouched | already present>
- Wrap-up add-ons: selected=<list or none>, skipped=<list or none>

Details on request:
- Full file list by platform
- Full subagent and skill list
- Full plugin/MCP recommendation table with [Tier · Vendor]
- Full update-preflight and human-input evidence
- Full requirements-triage intake brief and routing rationale
- Full Task Assignment / Prompt Contract quality findings
- Full content-quality signal list and curator rationale
- Full security-team operating model, evidence/counterevidence, severity rationale, and proof gaps
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
✅ Task-assignment findings: <ok / warn / fail counts>
✅ Content-quality findings: <ok / warn / fail / n/a counts>
✅ Security-team findings: <confirmed / likely / needs-info / duplicate / not-reproducible / out-of-scope / mitigated / deferred counts>
✅ Deltas applied: <count>
✅ Deltas skipped: <count>
✅ Requires-human: <count>

Try it:
  <render selected runtimes only; omit every unselected runtime>
  - If `copilot` selected: run `copilot`, then describe the task directly; use a justified specialist only when needed. No emitted `@orchestrator` agent; `/fleet` is optional native CLI UX, not required.
  - If `claude` selected: `claude` then describe the task; invoke a specialist only when justified
  - If `opencode` selected: `opencode` then describe the task to the primary; permission-gated specialists are optional
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
✅ Context budget: AGENTS.md=<N>/150 physical lines · <N>/12288 UTF-8 bytes · compliant=<yes|no> · tokens=<tokenizer-qualified count|estimate|unavailable>
✅ Context scope: controlled adapters/imports=<bytes and paths> · effective runtime context=<observed scope|unknown>
✅ Skill loading: <name + native path>; discovery=<observed|unobserved>; host-loaded=<evidence|no>; child-context=<passed excerpts|child-loaded|missing|n/a>
✅ Task assignment quality: <ok | warn | fail; form=<short | full>; missing=<fields | none>; questions=<count>; expansion blocks=<list | none>>
✅ Clarifications requested: <count>
✅ Triage status: <separate | merged | skipped>; intake brief=<present|n/a>
✅ Content quality: <ok | warn | fail | n/a>; curator=<separate | merged | skipped>; signals=<list | none>
✅ Security team: <baseline | dedicated | expanded | n/a>; authorization=<owned-code | approved-target | requires-human | n/a>; proof gaps=<count | none>
```

Use the values measured at write time. If a surface is not generated for this run, use `n/a` for that field.

The memory budget applies to the entire merged file in every profile, including
user-authored tails. A hard failure cannot produce a compliant completion or
clean repair stamp. Declined changes remain untouched and nonconforming.
Use the read-only doctor's `--memory-only` mode before publishing the manifest;
normal doctor invocation retains missing-manifest exit 2.

Keep exact lines/bytes separate from tokenizer-qualified counts or estimates.
Do not claim that imports, audience labels, or parent skill loading reduce the
child's effective context without evidence. File existence proves neither native
skill discovery nor loading in an already-running session. Record unavailable
surfaces honestly; do not install or modify global runtimes just to fill a row.

For Codex targets, keep `codex-cli` as the machine-readable runtime key, but label generated artifacts as **OpenAI Codex CLI + App compatible** when they are shared repo artifacts. Keep plugin install and slash-command examples explicitly CLI-only.

For Gemini targets, keep `gemini-cli` as the machine-readable runtime key. Label generated agents as **Gemini CLI local subagents**, note that `mcp_servers:` was approval-gated if present, and surface any recursive-delegation lossiness.
