# Self-Update Preflight

> Last verified: 2026-05-06. Run this before setup so generated agent systems use the latest source-backed runtime rules without silently changing plugin, MCP, or user configuration.

## Policy

Phase -1 checks the local agents-system-setup checkout at:

```sh
${AGENTS_SYSTEM_SETUP_HOME:-$HOME/github/agents-system-setup}
```

The preflight uses `git status --porcelain=v1`, `git fetch`, `git rev-list`, and
`git merge --ff-only`. It may fast-forward the checkout only when all of these
are true:

1. The directory exists and is a Git worktree.
2. The worktree and index are clean.
3. The current branch has an upstream.
4. `git fetch` succeeds.
5. The local branch is behind upstream and has no local-only commits.
6. `git merge --ff-only` succeeds.

Ask the user, or emit a `question_request` when human input is unavailable, on
dirty worktrees, missing installs, missing upstreams, divergent branches,
local-only commits, fetch failures, or ambiguity about which plugin manager owns
the install mode. Never edit MCP config, plugin config, runtime settings, or generated
agent files as part of the self-update preflight.

## POSIX snippet

Use this pattern from a POSIX shell. It writes no scratch files and does not
touch runtime configuration.

```sh
set -eu

ass_home="${AGENTS_SYSTEM_SETUP_HOME:-$HOME/github/agents-system-setup}"

if [ ! -d "$ass_home/.git" ]; then
  printf '%s\n' "question_request: missing agents-system-setup checkout at $ass_home"
  exit 0
fi

cd "$ass_home"

status="$(git status --porcelain=v1)"
if [ -n "$status" ]; then
  printf '%s\n' "question_request: agents-system-setup checkout has local changes"
  exit 0
fi

upstream="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"
if [ -z "$upstream" ]; then
  printf '%s\n' "question_request: agents-system-setup branch has no upstream"
  exit 0
fi

if ! git fetch --prune --quiet; then
  printf '%s\n' "question_request: git fetch failed for agents-system-setup"
  exit 0
fi

counts="$(git rev-list --left-right --count HEAD..."$upstream")"
set -- $counts
ahead="$1"
behind="$2"

if [ "$ahead" = "0" ] && [ "$behind" = "0" ]; then
  printf '%s\n' "agents-system-setup preflight: already up to date"
elif [ "$ahead" = "0" ]; then
  git merge --ff-only "$upstream"
  printf '%s\n' "agents-system-setup preflight: fast-forwarded from $upstream"
else
  printf '%s\n' "question_request: agents-system-setup branch is ahead or divergent"
fi
```

## Provider update matrix

| Runtime | User-owned plugin update command | Notes |
|---|---|---|
| Copilot CLI | `copilot plugin update agents-system-setup` | Run only when the user wants the installed Copilot plugin updated. Do not rewrite `.mcp.json` or hooks silently. |
| Claude Code | `/plugin marketplace update <marketplace-name>` then `/reload-plugins` | Marketplace refresh and plugin reload are interactive Claude commands. Do not edit `.claude/settings.json` without approval. |
| OpenCode | `opencode plugin <module>` | OpenCode plugin modules are command/config based; do not add an install subcommand. Update the module source by its package-manager or Git instructions. |
| OpenAI Codex CLI | `codex plugin marketplace upgrade [name]` | CLI marketplace command only. Codex App plugin UI/config remains separate. |
| Gemini CLI | `gemini extensions update <name>` or `gemini extensions update --all` | Extension update only; generated `.gemini/agents/*.md` and MCP blocks still need normal approval gates. |

## Output evidence

Record one compact line in the plan and output contract:

```text
Update preflight: <checked|already-current|ff-updated|requires-human|skipped> · source=<path-or-manager> · evidence=<git range or question_request id>
```

When a provider plugin-manager command is suggested or run by user approval, also
record the runtime and command. Do not claim that generated artifacts were
updated unless the normal Phase 4/5 write path ran.

## Anti-patterns

- Updating MCP/plugin/runtime config during preflight.
- Fast-forwarding a dirty or divergent checkout.
- Assuming the install location when `AGENTS_SYSTEM_SETUP_HOME` and the default path disagree.
- Treating a missing checkout as permission to clone or install without asking.
- Assuming OpenCode has an install subcommand; use `opencode plugin <module>` or the module's documented package/Git update path.
- Bumping versions, tagging, releasing, or pushing as part of preflight.

## Sources

- Git fast-forward semantics: <https://git-scm.com/docs/git-merge>.
- Copilot CLI plugin docs: <https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-cli-plugins>.
- Claude Code plugin docs: <https://docs.claude.com/en/docs/claude-code/plugins>.
- OpenCode agents/plugins docs: <https://opencode.ai/docs/agents/>.
- OpenAI Codex plugin docs: <https://developers.openai.com/codex/plugins>.
- Gemini CLI extension docs: <https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/index.md>.
