# Native Runtime Initialization

> Last verified: 2026-09-07. Native initialization is discovery input for the
> plugin's compact canonical memory; it is not a replacement for artifact
> tracking, file-plan approval, conflict review, or provider-specific gates.

## Contents

- [Boundaries](#non-negotiable-boundaries)
- [Runtime matrix](#runtime-matrix)
- [Native-first workflow](#native-first-workflow)
- [Fallback](#disclosed-fallback)
- [Completion evidence](#completion-evidence)
- [Official sources](#official-sources)

## Non-negotiable boundaries

1. Run an initializer only after artifact tracking and the complete file plan
   are approved. Record intended paths and preimages first.
2. Invoke only the active harness. Never initialize every replication target.
3. When user-authored memory already exists, use the existing instruction-memory
   audit. Do not initialize over it merely to obtain a new draft.
4. Use a documented command surface that the active session actually exposes.
   Do not type a slash command as ordinary prompt text and claim native execution,
   and do not invent a shell command, flag, RPC, or dispatcher.
5. Reuse the native output. Never copy or extract a vendor's internal init
   prompt into this plugin.
6. Native output may describe the repository, but it cannot approve MCP,
   hooks, permissions, runtime settings, external actions, or policy changes.

## Runtime matrix

| Harness | Native surface | Documented default output | Required handling |
|---|---|---|---|
| OpenAI Codex CLI TUI | `/init` | `AGENTS.md` in the current directory | The current public bundled prompt targets a concise 200-400-word draft and says not to modify an existing file. That is prompt-level behavior, not a filesystem transaction guarantee. There is no documented standalone `codex init` or scaffold RPC; if the TUI command cannot be dispatched, return control or use the approved fallback. |
| GitHub Copilot CLI | Interactive `/init`; terminal `copilot init` | `.github/copilot-instructions.md` | Prefer the interactive root request below. The documented default is not a mandatory filename, but the additional text is not a guaranteed filename-switch API or a terminal argument. Inspect observed output before recording success. |
| Claude Code | `/init` | `CLAUDE.md` | Existing files may receive proposed improvements. Enhanced initialization can also propose skills, hooks, or `CLAUDE.local.md`; each additional artifact or config change needs its own approved file plan and applicable gate. |
| OpenCode | `/init` | `AGENTS.md` | Creates or improves project instructions. Confirm that the interactive command is available; do not invent a terminal `opencode init` equivalent. |
| Gemini CLI | `/init` | `GEMINI.md` | Honor configured context filenames and inspect the actual change set. The command documentation does not promise transactional updates. |

## Native-first workflow

### 1. Establish the safe input state

- Detect the active harness, version, working directory, configured context
  filenames, existing instruction files, symlinks, and path collisions.
- Complete artifact-tracking and file-plan approvals before invocation.
- Capture content hashes or byte-identical preimages for every path the native
  command could affect.
- If canonical or customized memory exists, stop here and audit that memory
  instead of running initialization over it.

### 2. Invoke one supported native surface

For a fresh Copilot setup, prefer this user-specified interactive request when
the running command surface accepts additional instructions:

```text
/init generate AGENTS.md at root instead of .github/copilot-instructions.md
```

Treat three facts separately:

- **Documented default:** `.github/copilot-instructions.md`.
- **Requested target:** root `AGENTS.md`.
- **Observed output:** the path or paths actually changed by this invocation.

Do not ask a destination question merely because the documented default differs.
Ask only when the running harness cannot accept or honor the root request, or
when existing content conflicts. Then offer the documented default draft, a
user-generated root draft, or the disclosed compact fallback as applicable.
Do not silently write both files, delete an unexpected output, add a redundant
Copilot adapter when `AGENTS.md` suffices, or change settings to hide warnings.

For the other runtimes, invoke the command shown in the matrix only through a
surface that advertises it in the active session. A skill may use Claude's
native Skill exposure when available, but it must not assume every SDK or
headless session advertises `/init`.

### 3. Inspect observed output before integration

Compare approved paths and preimages with the complete observed change set.
Unexpected paths, symlink traversal, collisions, or concurrent edits stop
integration for review. Do not restore a stale backup over a newer user edit.

Extract repository-specific purpose, commands, conventions, and boundaries from
the native draft, then verify them against repository evidence. The draft is
input to synthesis, not authority to broaden permissions or replace policy.

### 4. Synthesize compact canonical memory

Create one substantive root `AGENTS.md`. Target 80-120 physical lines and enforce
both hard limits on the complete merged file:

- no more than 150 physical lines; and
- no more than 12,288 UTF-8 bytes.

These limits are plugin policy, not an OpenAI requirement. Codex's documented
default combined instruction-chain budget is 32 KiB and can be configured
smaller; Anthropic recommends keeping `CLAUDE.md` under 200 lines. Account for
the whole applicable load chain rather than treating either upstream number as
permission to fill the budget. Never truncate policy to pass the limit: propose
approved synthesis or relocation, otherwise report nonconformance.

Keep essential ownership, security, approval, quality, and routing triggers
inline. Move detailed governance, workflows, and reusable procedures to
on-demand references or skills. Static model fields remain omitted unless the
user explicitly pins them.

### 5. Emit thin adapters only where needed

- Codex and OpenCode consume root `AGENTS.md` natively.
- Copilot consumes root `AGENTS.md` natively; emit no additional Copilot
  instruction file unless an approved compatibility or override need remains.
- Claude uses a small `CLAUDE.md` adapter containing `@AGENTS.md` plus only
  approved Claude-specific overrides.
- Gemini uses a small `GEMINI.md` adapter containing `@AGENTS.md` plus only
  approved Gemini-specific overrides. Prefer imports over symlinks or copies.

Native loaders may combine multiple files or imports. Copilot can load
`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and Copilot instruction files together;
it supports `@` imports from `AGENTS.md`, `CLAUDE.md`, and
`.github/copilot-instructions.md`, but not from `GEMINI.md`. Audit the actual
load graph and conflicting overrides. Imports and audience tags are not lazy
context savings, and ordinary Markdown links do not expand content for OpenCode.

## Disclosed fallback

If native invocation is unavailable, use a user-supplied native draft when one
exists. Otherwise:

1. explain which native surface was unavailable and why;
2. obtain approval for the compact plugin fallback and its exact paths;
3. generate from verified repository evidence, not a copied vendor prompt; and
4. label the result as fallback output, never as successful native `/init`.

Do not invent a dispatcher to bridge unsupported command surfaces.

## Completion evidence

Record:

- active harness, version, working directory, and invocation surface;
- approved paths and preimage hashes;
- documented default, requested target, and observed outputs;
- whether native output, user-supplied draft, or fallback was used;
- whole-file line and UTF-8 byte counts after merge;
- adapters/imports and any overlapping skill discovery paths;
- preserved content, conflicts, unexpected changes, and unresolved approvals;
- load evidence: `observed`, `reload-required`, or `unknown`.

File existence is not proof that an already-running harness loaded new memory or
skills. Require a new session or documented reload/refresh action where needed.

## Official sources

- Codex `/init`: <https://learn.chatgpt.com/docs/developer-commands#generate-agentsmd-with-init>
- Codex versioned prompt:
  <https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/tui/assets/prompt_for_init_command.md>
- Codex instruction discovery:
  <https://learn.chatgpt.com/docs/agent-configuration/agents-md>
- Copilot initialization:
  <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#project-initialization-for-copilot>
- Claude memory and `/init`: <https://code.claude.com/docs/en/memory>
- Claude commands: <https://code.claude.com/docs/en/commands>
- OpenCode rules: <https://opencode.ai/docs/rules/>
- Gemini commands: <https://geminicli.com/docs/reference/commands/>
- Gemini context files: <https://geminicli.com/docs/cli/gemini-md/>
