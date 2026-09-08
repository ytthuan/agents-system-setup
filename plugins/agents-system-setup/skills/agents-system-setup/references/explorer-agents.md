# Explorer Agents

Use this reference when the plugin's own Phase 0/1 recon needs to decide whether
to delegate codebase exploration to a host runtime's native explorer instead of
running sequential `view`, `glob`, and `grep` passes. This is the plugin using
explorers on the user's checkout; it is not guidance for generating an explorer
subagent in the user's roster.

## Source citations table

| Runtime | Native explorer | Invocation | Model/profile | Documentation URL |
|---|---|---|---|---|
| GitHub Copilot CLI | `task` tool, `agent_type: "explore"` | Tool call from host session | Runtime-advertised model; no fixed cheap-model assumption | Copilot CLI tool definition (no canonical public URL; defined by Copilot CLI runtime) |
| Claude Code | `Explore` built-in subagent | Native read-only exploration; supply required scoped context | Inspect current native model/controls | `https://code.claude.com/docs/en/sub-agents` |
| OpenCode | `explore` built-in subagent | `@explore` mention OR auto-invoked by Build/Plan primary | Read-only; cannot modify files | `https://opencode.ai/docs/agents/` |
| OpenAI Codex (CLI + App) | `explorer` built-in agent | Advertised spawn controls and configured concurrency/recursion limits | Read-heavy; model/effort chosen within pins and budget | `https://learn.chatgpt.com/docs/agent-configuration/subagents` |
| Gemini CLI | `codebase_investigator` built-in subagent | `@codebase_investigator` mention OR auto for complex code questions | Default-enabled in 0.10.0-preview+; runs in own context window | `https://geminicli.com/docs/core/subagents/` |

## When to delegate to native explorer

Delegate when broad reconnaissance would consume more budget than the final plan
or generated artifacts. Native explorers are useful when independent concerns can
be investigated in parallel and then merged into one compact recon card.

Signals such as `source_files > 50`, `top_level_dirs > 8`,
`frameworks_detected > 3`, or `recon_threads_requested > 2` suggest considering
separate context; they do not mandate an explorer or fan-out.

Calculate this trigger after Phase 0a captures the project purpose, but before
Phase 1 footprint detection writes a full recon. The plugin should fan out
parallel explore threads only when the codebase is large enough that sequential
recon would dominate the budget. Tiny projects should stay in the host session.

## 5-thread parallel recon recipe

The five concerns below are a menu, not a quota. Choose only substantial
independent work not already covered; merge related small concerns or read them
directly in the host. Return compact structured results for selected threads.

### Thread 1 — Source code structure

Ask one explorer to find top-level directories, primary language files, and build
manifests. It should identify generated/vendor directories separately from source
code so the source-file count remains meaningful.

Prompt template:
```text
Explore source code structure for this checkout. Return a JSON-ish summary with:
key_facts, top_level_dirs, source_file_counts_by_language, build_manifests,
candidate_frameworks, generated_or_vendor_dirs, anomalies. Read only; do not edit.
Keep the result compact and cite representative paths.
```
### Thread 2 — Tests

Ask one explorer to map test directories, test runner configuration, fixtures,
coverage tooling, and obvious gaps between source layout and test layout.

Prompt template:
```text
Explore the test footprint for this checkout. Return a JSON-ish summary with:
key_facts, test_dirs, test_file_counts_by_framework, runner_config,
coverage_tooling, source_areas_without_visible_tests, anomalies. Read only;
do not edit. Keep the result compact and cite representative paths.
```
### Thread 3 — Configuration

Ask one explorer to inspect configuration shape without reading or reporting
secret values. `.env*` files are presence-and-key-shape only; contents remain
sensitive and should not be copied into the recon.

Prompt template:
```text
Explore configuration and operations shape for this checkout. Return a JSON-ish
summary with: key_facts, env_file_shapes_without_values, ci_cd_config,
infrastructure_as_code, package_or_runtime_config, deployment_signals,
security_sensitive_paths, anomalies. Read only; do not copy secrets or values.
```
### Thread 4 — Documentation

Ask one explorer to summarize onboarding and design documentation, including
`README.md`, `CONTRIBUTING.md`, `docs/`, ADR directories, and any runtime-specific
agent instructions already present.

Prompt template:
```text
Explore documentation for this checkout. Return a JSON-ish summary with:
key_facts, primary_docs, contributing_or_setup_docs, docs_dirs, adr_or_design_docs,
agent_instruction_docs, stale_or_conflicting_docs, anomalies. Read only; do not edit.
```
### Thread 5 — Existing agent artifacts

Ask one explorer to detect existing agent-system files across supported runtimes.
For user-global paths such as `~/.codex/AGENTS.md`, report existence only when
safe and available; do not dump private global content into project recon.

Prompt template:
```text
Explore existing agent artifacts for this checkout. Return a JSON-ish summary
with: key_facts, project_agent_files, runtime_agent_dirs, skills_dirs,
mcp_config_files, user_global_agent_signals, version_or_managed_markers,
anomalies. Check AGENTS.md, CLAUDE.md, .github/agents/, .claude/agents/,
.opencode/agents/, .codex/agents/, .gemini/agents/, and ~/.codex/AGENTS.md when
available. Read only; do not edit or expose private global content.
```

## Per-runtime invocation cheat-sheet

Use the host runtime's native call surface. The prompt body should be one of the
five templates above.

### GitHub Copilot CLI invocation

Use the native task surface from the host. Batch justified independent threads;
use background only when there is other independent work to do:

```text
task(agent_type: "explore", mode: "background", name: "recon-source-structure", prompt: "...")
# Select only justified independent concerns; use sync when there is no parallel work.
```

### Claude Code invocation

Let Claude auto-delegate to the built-in `Explore` subagent for broad read-only
research, or use an explicit Task/Agent call with `subagent_type: "Explore"` when
the host needs strict thread separation:

```text
Use Explore to inspect only source code structure. Return the JSON-ish recon shape.
```

### OpenCode invocation

Mention the built-in read-only explorer from the primary agent message:

```text
@explore find all top-level source directories and primary language manifests.
Return key facts, counts, candidate frameworks, and anomalies.
```

Build/Plan primaries may also auto-invoke `explore`; preserve the selected scope
boundaries so integration remains clear.

### OpenAI Codex invocation

Use an advertised spawn surface for justified concerns. Preserve configured
limits and the plugin's non-recursive safety boundary; do not claim a fixed
concurrency default or change limits for a routine task:

```text
Inspect the selected independent recon concern with a scoped explorer.
Return compact facts and source paths; respect model pins and resource limits.
```

### Gemini CLI invocation

Mention the built-in investigator, or rely on auto-invocation for complex code
questions:

```text
@codebase_investigator inspect the test footprint only. Return key facts,
counts, runner config, coverage tooling, and anomalies. Read only.
```

Because Gemini subagents cannot recursively delegate, keep all fan-out owned by
the root Gemini session.

## Merge & fan-in protocol

The host session collects N explorer results, spot-checks representative files,
and writes a single recon card. Do not paste all explorer output into `AGENTS.md`.
Keep temporary recon evidence in the plan/operational state. Synthesize only
durable purpose/stack/commands into root memory; do not recreate the removed
`RECON_SNAPSHOT` placeholder or a second lifecycle manual.

Merge order:
1. Normalize each explorer result into `thread`, `key_facts`, `counts`,
   `candidate_frameworks`, `sensitive_signals`, and `anomalies`.
2. Deduplicate paths and prefer concrete file evidence over inferred framework
   names.
3. Spot-check one or two representative files per thread before trusting the
   summary.
4. Emit at most five recon-card lines: purpose, source/build signals, test
   signals, config/security signals, and existing agent artifacts.
5. Cache the recon card for later phases. Do not re-run explorers unless the user
   changes the scope or asks for fresh reconnaissance.

## Fallback when explorer is disabled or unavailable

Native explorers may be disabled, unavailable, or outside the approved budget.
Use direct read-only tools for the selected concerns instead; do not invent a
configuration value to force enablement or relax permissions.

Select relevant concerns from the same menu:
1. Source code structure — `glob` top-level directories, language files, and
   build manifests; `view` representative manifests.
2. Tests — `glob` test directories and runner config; `view` package or runner
   files only.
3. Configuration — `glob` `.env*`, CI/CD, and IaC names; never print secret
   values from env files.
4. Documentation — `glob` README, CONTRIBUTING, docs, and ADR files; `view` only
   the first relevant sections.
5. Existing agent artifacts — `glob` project runtime agent directories and
   config; check user-global signals only when safe and needed.

This fallback should still produce the same compact recon-card schema. The only
change is who performs the read-only discovery.

## Anti-patterns

- Spawning explorer for tiny projects with fewer than 50 files, where startup and
  synthesis overhead exceeds the benefit.
- Treating every recon concern as a required worker or repeating already-known
  facts in several explorers.
- Treating explorer output as authoritative without reading the actual files.
  Explorers summarize, but they can miss anomalies; spot-check one or two files
  per thread.
- Re-spawning explorers on every Phase change. Recon is once, at Phase 1.
  Subsequent phases use the cached recon card.
- Using HTML comments to hide explorer output from the user. Explorer summaries
  should be visible in the recon card.
