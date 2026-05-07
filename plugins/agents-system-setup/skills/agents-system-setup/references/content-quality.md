# Content Quality / Anti-Slop Guardrails

Use this reference to keep generated agent systems specific, grounded,
compact, and reviewable. The goal is not to add more prose; the goal is to
remove vague, unsupported, or overconfident output before users rely on it.

## Source-backed principles

| Principle | How generated agents apply it | Source family |
|---|---|---|
| Specificity | Descriptions start with "Use when..." and name concrete triggers, owned surfaces, and outputs. | Anthropic prompt engineering guidance; GitHub Copilot custom-agent guidance |
| Grounding | Claims come from repo files, user answers, runtime docs, or cited marketplace sources. Unsupported claims are marked as assumptions. | GitHub Copilot review guidance; Azure AI Foundry groundedness evaluation |
| Task adherence | Output maps back to the user's requested mode, platform scope, approvals, and quality gates. | Azure AI Foundry task adherence and task completion evaluation |
| Human ownership | User-facing approvals remain explicit; agents do not hide risk behind confident summaries. | GitHub Copilot responsible use guidance; OWASP LLM overreliance risk |
| Least agency | Curators review and report. They do not get broad write, MCP config, release, or final approval authority. | OWASP LLM excessive agency risk; MCP security least-privilege practice |
| Concision with evidence | Short output is preferred, but skipped gates, lossy mappings, and warnings stay visible. | Anthropic concise prompting guidance; OpenAI G-Eval coherence/relevance dimensions |

## Universal generated role

Use `agent-quality-curator` as the primary generated role name. Use
`anti-slop-reviewer` only as an alias or trigger phrase.

| Field | Value |
|---|---|
| Role | Review generated agent, skill, memory, recommendation, and output-contract prose for specificity, grounding, prompt hygiene, evidence quality, and context bloat. |
| Owned paths | None by default. The curator is read-only unless an explicit plan grants a narrow docs-only remediation path. |
| Tool profile | `read-only` or `research`; never edit-capable by default. |
| Runs before | Final setup/update/improve/replicate output when generated agent-system prose changed. |
| Reports | Content-quality status `ok`, `warn`, `fail`, or `n/a`; signal list; concrete fixes or escalation. |

The curator does not replace `reviewer`, `tester`, `security-auditor`,
`architecture-reviewer`, `design-pattern-reviewer`, or static validators. It
checks semantic quality and prompt hygiene for generated agent-system artifacts.

## Sizing rule

| Setup size | Decision |
|---|---|
| Normal, complex, cross-runtime, audit, improve, replication, MCP, release, skill-heavy, or multi-wave setup | Generate `agent-quality-curator` as a separate read-only subagent. |
| Tiny direct setup | Merge the responsibility into `reviewer` and record `content_quality_curator = merged`. |
| Explicit user opt-out or non-agent/prose-free task | Record `content_quality_curator = skipped` with rationale. |

## Review scope

The content-quality check applies to:

- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and root orchestrator memory.
- Runtime agents in `.github/agents/**`, `.claude/agents/**`,
  `.opencode/agents/**`, `.codex/agents/**`, and `.gemini/agents/**`.
- Runtime skills in `.github/skills/**`, `.claude/skills/**`, and
  `.opencode/skills/**`.
- Plugin, MCP, marketplace, and wrap-up recommendation prose.
- Setup, update, improve, and replicate output contracts.
- This plugin's templates and references when the plugin improves itself.

## Signal taxonomy

| Signal | Fail mode | Typical fix |
|---|---|---|
| `generic-description` | Agent or skill description does not clearly say when to use it. | Rewrite with specific triggers, scope, and expected output. |
| `empty-rationale` | Recommendation lacks why, tradeoffs, or evidence. | Add a concise rationale or drop the recommendation. |
| `padding-repetition` | Policy is repeated instead of linked. | Keep the rule once and link the canonical section. |
| `slop-completeness` | Output claims done without evidence or skipped-gate disclosure. | Add evidence, unresolved items, or explicit `n/a` rationale. |
| `invented-attribution` | Vendor, capability, version, or source claim is not supported. | Cite the source or downgrade to assumption/unknown. |
| `context-bloat` | Prompt duplicates full project memory or long reference text. | Summarize inline and link the detail file. |
| `vague-ownership` | Owner, writable paths, or approval boundaries are unclear. | Add Directory Architecture and owner/gate references. |
| `unsupported-assertion` | Advice is not grounded in files, user input, or cited source. | Add evidence or mark as assumption. |
| `silent-gate-gap` | Security, MCP, release, learning, or quality gate is omitted. | Surface the gate and owner in the plan/output contract. |
| `prompt-hygiene-risk` | Prompt grants broad authority, hides assumptions, or encourages unsafe delegation. | Narrow tools, require escalation, and add `question_request` flow. |

## Status rubric

| Status | Criteria |
|---|---|
| `ok` | No blocking signals. Any minor wording issues are fixed or explicitly deferred with low risk. |
| `warn` | One or more non-blocking signals remain, but generated artifacts are usable and gates are visible. |
| `fail` | A blocking signal could misroute work, hide an approval, overclaim support, or make an agent unsafe/ineffective. |
| `n/a` | No generated agent, skill, memory, recommendation, or output-contract prose changed. |

## Output markers

Final setup/update/improve/replicate summaries include:

```text
Content quality: <ok|warn|fail|n/a>; curator=<separate|merged|skipped>; signals=<list|none>
```

Every generated subagent reporting template includes:

```text
Content quality: ok | warn | fail | n/a; signals=<list|none>
```

## Quality ledger policy

Do not create `.agents-system-setup/quality-baseline.jsonl` by default. A
quality ledger is opt-in for Full profile, audit-heavy teams, or long-lived
agent programs that explicitly want trend tracking. When enabled, it is an
operational JSONL ledger, never Markdown inside runtime `agents/` directories.

## Anti-patterns

- Naming the generated role `anti-slop-agent` instead of the neutral
  `agent-quality-curator`.
- Giving the curator broad write, MCP config, runtime config, release metadata,
  or final approval ownership.
- Adding long anti-slop prose to every generated subagent.
- Treating a content-quality pass as a replacement for tests, security review,
  architecture review, or provider schema validation.
- Claiming a runtime, plugin, skill, or MCP capability without a source or an
  explicit uncertainty note.
