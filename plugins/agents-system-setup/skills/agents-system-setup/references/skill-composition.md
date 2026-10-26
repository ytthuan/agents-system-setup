# Skill Composition During Migration

Convert capabilities, not file counts. An agent that already loads useful
skills does not need copies of those skills or an empty role wrapper.
Use this policy for new solo setups and [topology conversion](./topology-conversion.md).

## Inventory the complete skill list

Read each agent's native skill list (for example Claude `skills:`), body load
instructions, linked references, and `plugin_component_refs.skills`. Capture
these as `skill_refs` in [AgentIR](./replication.md#1a-agentir), including:

- Exact load ID, origin/runtime, resolved path, and source location in the agent.
- Required or optional, the task condition, and any ordering constraint.
- Whether this is an existing skill, a plain reference, or an unresolved name.

An unconditional native preload stays required whenever the source role would
apply; do not invent narrower conditions to reduce loading. Capture explicit
conditional loads as written. Narrowing either needs a reviewed mapping decision.

Resolve against the active runtime's actual discovery paths and permissions.
Two skills with the same name but different bodies/providers are a collision,
not duplicates. Do not assume parent-loaded skills will load in a reviewer.
Never turn source-agent `skills:` metadata into a universal SKILL.md dependency
field: the portable format does not define one.

## Reuse, reference, merge, or extract

| Decision | Use when | Result |
|---|---|---|
| **Reuse** (first choice) | An existing skill covers the responsibility and its constraints | Route the host directly to that skill; create no duplicate and no empty wrapper. |
| **Reference** | Existing skills remain independently useful; the role adds sequencing or project-specific steps | A small workflow skill lists exact IDs/paths and conditions; the host loads dependencies on demand. |
| **Merge** | Procedures have the same trigger, compatible scope, and compatible output/approval contracts | Propose one cohesive skill with unique instructions preserved and repeated text removed. |
| **Extract** | The agent has unique procedural knowledge not covered by existing skills | Emit a `solo-role` skill, with optional local references for depth. |

These decisions can combine: an `api-work` skill may extract a project's API
procedure while referencing `code-quality` and `api-testing`. Several agents
can reuse the same skill. One agent covering unrelated workflows can produce
several focused skills. A many-to-one merge is valid when the work is cohesive;
concatenating every agent prompt is not.

### Merge checks

1. Compare actual instructions, owned/read-only paths, triggers, gate evidence,
   and output contracts. Similar names alone do not justify merging.
2. Preserve unique project knowledge, commands, scripts, references, and source
   attribution. Rewrite relative links from the destination package and check
   that assets remain accessible after the source agent is removed.
3. Resolve conflicting rules explicitly in the plan; do not select one silently
   or weaken an existing approval or independent-review requirement.
4. Prefer references for shared/plugin/vendor skills. Editing an existing
   user-owned body requires a reviewed diff and backup; a kind marker does not
   grant ownership. Preserve `domain` bodies under their never-overwrite policy.
5. Delete a superseded skill only when explicitly approved and all consumers
   (agents, skills, commands, root indexes, runtime configuration) are updated.
   Shared or externally installed skills remain available to other consumers.
6. Inspect execution behavior before reusing or referencing a skill in solo:
   native fork settings (such as Claude `context: fork` / `agent:`), delegation
   steps, agent teams, hooks, and command calls may still launch workers. Adapt
   that behavior through an approved diff or a distinct host-executed workflow;
   a wrapper that merely links the original does not disable its fork behavior.
   An unresolved working-agent dependency blocks completed solo conversion.

New portable skills follow the naming/frontmatter contract. Reused native skills
keep their supported format and exact load ID, even when that runtime permits
a display name or a flat Markdown file. Referencing a third-party skill does
not authorize adding generation stamps or claiming its content as plugin-owned.

## Referencing skills from a skill

Use an ordinary body section rather than unsupported frontmatter. For example:

```markdown
## Skills Used

| Skill / native load ID | Load when | Requirement | Location |
|---|---|---|---|
| code-quality | Before editing or reviewing code | Required | ../code-quality/SKILL.md |
| api-testing | When an API contract changes | Required for that change | ../api-testing/SKILL.md |

Load the matching skill through the active runtime's skill loader before its
step. A Markdown link does not load it. If required loading is denied or the
skill is missing, stop that step and report the missing dependency.
```

Those example paths apply only to sibling skills; render real native IDs and
paths for the selected runtime. Cross-runtime copies are not dependencies of
one another. A plain reference file is read as a file, not invoked as a skill.

The host resolves the dependency graph for the current task:

- Load only matching dependencies. A workflow may be loaded to discover its
  prerequisites; load those before executing the steps that depend on them.
- Deduplicate by resolved skill identity within the current context; skip an
  already-loaded unchanged body. After compaction, a new session, or a changed
  definition, verify that the required content is available again.
- Detect self-reference and cycles before writes. Inline the small common step
  or extract a shared dependency to break a cycle; never recurse indefinitely.
- Missing/denied required dependencies block the affected step. Optional ones
  may be skipped with a reason and never stand in for required gate evidence.
- Referencing another skill does not spawn an agent, transfer permissions, or
  create independent review. Solo stays host-executed, with its reviewer exception.

## Conversion coverage

The plan accounts for every source responsibility and skill reference:

| Source agent / section | Decision | Destination skill(s) | Dependencies | Rules preserved / conflicts |
|---|---|---|---|---|
| implementer / craft | reuse | code-quality | none | Existing authoring standards |
| api-designer + api-implementer / API procedure | merge | api-work | code-quality, api-testing | Preserve both API and implementation constraints |
| tester / project scenarios | extract + reference | test-workflow | api-testing | Preserve test commands and fixtures |

Validate references and the coverage table before retiring agents. Unknown
fields, hooks, MCP configuration, model pins, and permission rules need an
explicit retained/mapped/unsupported decision, not silent copying into a skill.
Report `reused`, `referenced`, `merged`, `created`, and unresolved dependencies.
