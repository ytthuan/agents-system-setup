# Context Optimization

Synthesize project memory from repository facts and the active harness's native
draft, not a filled workflow manual. Keep essential decisions resident; load
procedures through skills. See [native initialization](./native-initialization.md)
for commands, supported dispatch, approvals, and fallback behavior.

## Contents

- [Output profiles](#1-output-profiles)
- [Generated-output hierarchy](#2-generated-output-hierarchy)
- [Placement rule](#2a-placement-rule--where-a-piece-of-knowledge-goes)
- [Context budgets](#3-context-budgets)
- [Inline vs reference split](#4-inline-vs-reference-split)
- [Concise delegation packets](#6-concise-delegation-packets)
- [Context freshness rule](#context-freshness-rule)
- [Task-Type Routing Map](#task-type-routing-map)
- [Compact mode trimming](#compact-mode-trimming)
- [Layered context & audience tags](#layered-context--audience-tags)

## 1. Output profiles

| Profile | Use when | Detail placement |
|---|---|---|
| `Balanced` (default) | Most projects | Concise root rules; task-specific detail in skills and project policy. |
| `Compact` | Small repos or tight context | Minimal root decisions and only relevant on-demand material. |
| `Full` | Audits or regulated projects | Fuller on-demand matrices, rationale, and examples; the same root limit. |

All profiles obey the complete-file root budget. Full never means unlimited
always-loaded memory. Do not pad a small project to meet the target length.

## 2. Generated-output hierarchy

| Artifact | Context rule |
|---|---|
| `AGENTS.md` | Canonical project facts, working commands, ownership, critical controls, gate triggers, and skill index. |
| Native memory adapters | Thin `@AGENTS.md` imports where supported, not policy copies. Copilot/OpenCode/Codex can use root memory directly. |
| Runtime agent files | Role, owned/read-only paths, compact project digest, fail-closed intake, safety, and reporting. |
| Host workflow skills | Load for delegation, code quality, Build Gate, or doctor work; do not inline their full bodies in root memory. |
| Project domain skills | Load project-specific knowledge only for concrete matching triggers. Preserve user-owned bodies. |
| Project policy | Local governance detail, capability coverage, ADRs, and review responsibilities; never eagerly import it. |
| Operational state | Native-init evidence, approvals, migration events, and checksums belong in JSON/JSONL, not root memory. |

### 2a. Placement rule — where a piece of knowledge goes

| Knowledge | Goes to | Why |
|---|---|---|
| Needed on every task | `AGENTS.md` | Routing, ownership, approval boundaries, and gate triggers stay resident. |
| Needed on some tasks and project-specific | A `skill-kind: domain` skill | A concrete trigger selects the body; metadata is not the full procedure. |
| Generic craft | An existing host skill such as `task-delegation`, `code-quality`, or `code-change-build-gate` | Reuse one versioned workflow instead of repeating it. |
| Deep task detail | That skill's `references/` or local project policy | Load only the relevant section. |

Do not move a gate's trigger, owner, approval requirement, or missing-evidence
blocking rule into an undiscoverable file. Do not leave a full copy behind after
approved relocation. An ordinary Markdown link makes a reference findable;
it does not prove runtime discovery or a skill load.

## 3. Context budgets

| Surface | Target | Enforced rule |
|---|---|---|
| Complete synthesized `AGENTS.md` | 80-120 physical lines | At most **150 lines AND 12,288 UTF-8 bytes** after substitution and merging, including user content. |
| Main `SKILL.md` | About 250 lines | At most 500 lines; move detail into references, not giant lines. |
| Skill description | Trigger-rich and concise | Follow the native schema; do not paste the procedure into metadata. |
| Worker instructions | Under about 80 lines | Retain fail-closed intake, ownership, safety, and reporting. Codex has its own body budget. |

The numeric root cap is **plugin policy**, not an OpenAI requirement. Codex's
current native `/init` scaffold targets 200-400 words; its configurable
`project_doc_max_bytes` defaults to a 32 KiB instruction-chain budget.
Anthropic recommends under 200 lines per `CLAUDE.md`. See
[source-backed runtime details](./native-initialization.md).

Count physical LF-delimited lines, including an unterminated final line. CRLF
uses one line delimiter but both bytes count. Decode as UTF-8 strictly; count
raw bytes before newline normalization. Long single lines do not evade the byte
limit. Never truncate, silently remove rules, or raise a runtime limit to pass.

Run the emitted read-only checker before publishing the generated manifest:

```bash
python3 .agents-system-setup/agents-doctor.py --memory-only
```

A hard budget failure blocks compliant completion. Iterate the approved
synthesis/relocation, or report `nonconforming` when the user declines repair.
Existing unapproved instructions remain untouched. `--memory-only` checks drafts
without requiring a manifest; normal doctor invocation retains its missing-
manifest exit code. Repository fixtures reuse this same checker.

Report bytes and lines exactly. Token counts need the tokenizer name/version
and measured content scope; otherwise label an estimate or `unavailable`.
Do not install a tokenizer or upload project instructions merely to obtain a
count. `cl100k_base` is not an exact cross-vendor or current-model tokenizer.

Report controlled adapter/import bytes separately from root bytes. Imports are
eager; links and audience labels are not lazy loading. Audit the applicable
instruction chain, overrides, configured context filenames, and overlapping
skill paths. Honor smaller known runtime budgets; unknown personal/global
context is unknown, not zero. Claim effective context only with runtime evidence.

## 4. Inline vs reference split

Use [AGENTS.md.template](../assets/AGENTS.md.template) as a synthesis contract,
not a demand to preserve every heading or create empty sections. Keep project
commands exact; do not invent build/test/lint commands when none exist.
Retain useful facts from the native draft and verify them against repository
evidence. Synthesize, do not append the old template after native output.

Use [project-policy.md.template](../assets/project-policy.md.template) for
approved local detail, normally `docs/agents/project-policy.md`. Substitute
`PROJECT_POLICY_PATH` in root links and omit inapplicable policy sections and
their contents links. Personal/global setups choose an approved, runtime-readable
local path instead; do not silently write repository docs. A proposed but
unwritten file cannot satisfy a required reference.

Root summary fields preserve the active controls and owners:
`SECURITY_AUDIT_SUMMARY_ROWS`, `THREAT_MODEL_SUMMARY`, and
`ARCHITECTURE_DECISION_SUMMARY`. Full source-backed rows, alternatives, ADRs,
and capability coverage live in project policy. The root Agent Roster lists
only justified workers with concrete triggers; zero specialists is valid.

Render `BUILD_GATE_ROOT_BLOCK` only for an enabled software-dev Build Gate:

```markdown
## Build Gate (SDLC)

Strictness: <selected>. Before code changes, load `code-change-build-gate`
from Skills; compute `max(size_bucket, criticality_bucket)`. Its local matrix
defines required gates. Missing skill, approval, or evidence blocks work/sign-off.
```

The skill contains the matrix and strictness modifiers. The resident trigger
is fail-closed; do not reproduce the full matrix in every root file.
Render `CODE_QUALITY_ROOT_BLOCK` for code-bearing projects:

```markdown
## Code Quality & Maintainability

Conform to existing conventions while writing. Load `code-quality` from Skills
before writing/reviewing code; required review remains independently owned.
```

Record skipped/inapplicable gates in the manifest/report instead of mandatory
empty root sections. `LEARNING_MEMORY_SUMMARY` states the selected profile and,
when enabled, the owner, local index path, and load trigger. Disabled means no
memory writes. Setup timestamps, recon logs, and latest task verdicts stay out.

Each `SKILL_TABLE_ROWS` entry needs **name, concrete trigger, and native load
name/local SKILL.md path** for the selected runtimes. Include actual relevant
skills, never a marketplace catalog. Name-based loading must be native and
discoverable; keep runtime-specific paths unambiguous. Deduplicate overlapping
discovery paths only with evidence, not by assuming identical names are merged.

## 5. Clear generated writing style

Use short rules and exact commands. Remove repeated lifecycle/packet prose,
generic exhortations, empty tables, and superseded facts. Preserve user meaning
and critical constraints. Show a repair diff before replacing user-owned content.
No prose compression that hides dozens of unrelated instructions on one line.

## 6. Concise delegation packets

The [canonical schema](./handoff.md#delegation-packet-canonical-schema) retains
the **12 required-minimum fields** in `task-delegation`. Do not duplicate the
field list in root memory. Pass the subtask, owned paths, relevant gates, selected
skills/context, and stop conditions; workers retain an inline safety minimum.

Load [prompt guidelines](./prompt-guidelines.md) for assignment authoring, not
as mandatory background reading for every worker. Host-loaded skill evidence
does not transfer its content to children. Pass necessary excerpts or use an
advertised child preload/load mechanism; report a blocker if required content
or permission is missing.

## Context freshness rule

`AGENTS.md@<sha>` or `recent` describes the host's snapshot freshness, not child
context inheritance. A child may avoid reloading only material it actually
received or loaded. Otherwise load the relevant root rows/skill or return a
`question_request`. `reload` means stale/unknown; replication and updates use it.
Memory file edits may require a new session/reload to take effect.

## Task-Type Routing Map

| Task | Required context | Optional detail |
|---|---|---|
| Direct read-only or docs work | Relevant ownership and gate rows | Project policy only if its trigger applies. |
| Delegation | `task-delegation`, scoped plan/context, worker boundary | Native routing details for the active runtime. |
| Code edit / bug fix / refactor | `code-quality`, enabled `code-change-build-gate`, affected ownership | Relevant ADRs and evidence. |
| Security / MCP / release / replication | Explicit scope, approval and evidence requirements | Matching security, runtime, and migration references. |
| Instruction-memory audit | Root memory, adapters, applicable overrides, declared skills | `instruction-memory-audit.md` and read-only doctor findings. |

Keep all mandatory gates for the task. Never load entire reference catalogs
merely because a table lists them.

## Compact mode trimming

Trim explanations, not the worker's acceptance checklist, reporting skeleton,
owned paths, or safety boundary. Preserve section anchors still referenced by
consumers. Codex follows the
[summary + pointer rule](./agent-format.md#codex-toml-summary--pointer-rule)
without assuming that its parent already delivered a referenced file.

## Layered context & audience tags

The managed project-standard digest remains required in every emitted worker.
Its hash is a drift warning, not proof of skill loading or an integrity boundary.
Codex uses the three-line digest; other workers use the five-line version.

Audience labels are optional reading hints, not loader controls. New compact
root files do not require a marker under every heading or a separate
Self-Contained Notice. Preserve useful existing labels within the same budget;
never claim that they exclude content from tokens. Full may expand on-demand
detail, not add rationale under every always-loaded heading.

## 7. Anti-patterns

- Passing a budget by checking only the template or managed block.
- Treating `<details>`, imports, audience labels, or host loading as free context.
- Moving an enforced trigger/owner out of root without a fail-closed load rule.
- Overwriting user/domain-skill content or blindly deleting legacy adapters.
- Claiming exact token savings without measuring the actual loaded context.
- Using copied vendor prompts or invented commands as native initialization.
