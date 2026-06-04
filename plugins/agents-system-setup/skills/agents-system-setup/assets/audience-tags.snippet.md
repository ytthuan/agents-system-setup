# Audience Tags Snippet

Audience tags are visible Markdown markers that tell each runtime which agent
class should treat a section as directive context. They are plain text, not HTML
comments, because visible markers survive provider markdown loaders, context
summaries, and copy/paste between runtimes.

## Audience values

Use exactly these three values. Do not add role-specific variants.

| Value | Meaning |
|---|---|
| `all` | Every agent, including the host orchestrator and every subagent, should read this section. |
| `host-orchestrator` | Only the host CLI session, the implicit orchestrator, should read this section in full. Subagents may skim for situational awareness but should not act on its directives. |
| `subagents` | Content directed at specialist subagents; the host orchestrator may skip when routing. |

## Emission rule

Audience tags emit ONLY when `subagent_count >= 2` AND
`output_profile in {balanced, full}`. For Compact profile or single-agent setups,
omit audience markers entirely because the file is small enough that segmentation
has no benefit.

## Per-profile rendering

| Profile | Rendering rule |
|---|---|
| **Compact** | Omit audience markers entirely; `AGENTS.md` stays minimal. |
| **Balanced** | Emit visible `**Audience:** <value>` line under each `## Section` heading; keep section body unchanged. |
| **Full** | Emit visible marker plus a leading "Why this section matters for <audience>" sentence under each section. |

## Marker placement

Place the marker immediately after the `##` heading and before any body text,
tables, blockquotes, or managed blocks.

```markdown
## Directory Architecture

**Audience:** all

| Path (glob) | Purpose | Owner | Edit rule |
|---|---|---|---|
```

The marker is visible project memory, not hidden metadata. If a section is copied
into a subagent prompt, the audience line should remain readable and harmless.

## Subagent Self-Contained Notice block

Inject this top-level section when the emission rule is met:

```markdown
## Subagent Self-Contained Notice

**Audience:** subagents

If you are a specialist subagent (not the host CLI session), your own `.agent.md`
or `.toml` file is the single source of truth for fail-closed operation.
You may read `AGENTS.md` rows for project-wide context and consult the
`task-handoff` skill when the host packet says `Skills Referenced: task-handoff loaded=true`.
Subagents are executors: never compose new delegation packets, never re-delegate.
Your own file must already inline role, owned paths, handoff acceptance, safety
boundaries, and reporting skeleton.
If scope exceeds your owned paths, stop and return-to-orchestrator with the
needed owner, paths, and reason.
```

## Anti-patterns

- Using HTML comments as audience tags. They are unreliable across runtime
  markdown loaders and summarizers.
- Adding a fourth audience value such as `reviewer-only`. The canonical set is
  exactly `all`, `host-orchestrator`, and `subagents`.
- Emitting audience tags in Compact mode. That regresses small-project context
  by adding segmentation where the file is already short.
