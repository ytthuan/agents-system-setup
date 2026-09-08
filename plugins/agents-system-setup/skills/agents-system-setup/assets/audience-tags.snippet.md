# Audience Tags Snippet

Audience tags are optional reading hints, not runtime loader controls. They
neither remove text from context nor make a referenced skill available to a
child. New compact root memory does not require per-section markers or a
separate Subagent Self-Contained Notice.

## Audience values

| Value | Meaning |
|---|---|
| `all` | Relevant to host and workers. |
| `host-orchestrator` | Host coordination guidance; workers do not orchestrate. |
| `subagents` | Worker execution guidance. |

Preserve useful existing `**Audience:**` labels within the same complete-file
150-line/12-KiB budget. Do not add a rationale paragraph beneath every heading
in Full profile; put explanatory detail on demand.

## Marker placement

When a label genuinely helps, put it beneath its heading:

```markdown
## Directory Architecture

**Audience:** all
```

## Worker self-containment

Keep the compact project-standard digest, owned paths, acceptance checklist,
safety boundaries, and reporting skeleton inside each worker's own file.
Workers are executors: never re-delegate; return `question_request` or
`return-to-orchestrator` for missing context or scope.

The host loads `task-delegation` before assignments. A packet saying
`Skills Referenced: task-delegation loaded=true` records a **host** load only;
pass the child's necessary excerpts or use a supported child preload/load.
Do not tell the child to rely on a skill body it never received.

## Migration

Classify obsolete per-heading markers and repeated Self-Contained Notice prose
as compact-repair candidates, not automatic deletion. Preserve user content and
required worker guards; show the proposed diff before an approved replacement.
