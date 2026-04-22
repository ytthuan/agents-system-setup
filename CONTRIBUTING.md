# Contributing to agents-system-setup

Thanks for your interest. This plugin ships across four runtimes, so contributions need to stay portable. Please read the relevant section before opening a PR.

## Table of contents

- [Local setup](#local-setup)
- [Validators](#validators)
- [Branching & PR flow](#branching--pr-flow)
- [Commit style](#commit-style)
- [Cutting a release](#cutting-a-release)
- [Going public checklist](#going-public-checklist)
- [Style notes](#style-notes)

## Local setup

```bash
git clone https://github.com/ytthuan/agents-system-setup.git
cd agents-system-setup
```

No language runtime is required for the skill itself. CI uses Node 20 (markdownlint), Python 3.11 (validator JSON/YAML parsing), shellcheck (Linux/macOS), and PSScriptAnalyzer (Windows). Locally you can install whichever subset you need.

## Validators

Run before pushing:

```bash
# POSIX (macOS / Linux / Git Bash / WSL)
bash scripts/validate.sh

# Windows native PowerShell
pwsh -File scripts/validate.ps1
```

Both scripts perform identical checks:

- JSON parse + required-field validation for the four manifests
- Version consistency across `plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`
- YAML frontmatter parse for every `SKILL.md` and `*.agent.md`
- Filename-vs-`name` match
- Encoding (UTF-8 without BOM)
- Line-ending policy from `.gitattributes` (`*.sh` → LF, `*.ps1` → CRLF)
- Internal Markdown link resolution

The validators are the source of truth — CI runs the same scripts.

## Branching & PR flow

1. Branch from `main` (`feat/<short-description>` or `fix/<short-description>`).
2. Commit using [Conventional Commits](https://www.conventionalcommits.org/) (see [Commit style](#commit-style)).
3. Run the validators locally.
4. Open a PR. The template includes a checklist — fill it in.
5. CI runs on Linux, macOS, and Windows. All three must be green.
6. Squash-merge after review.

## Commit style

Conventional Commits, lowercase type, imperative subject:

```
feat: add wave plan to phase 2 output
fix: handle empty owns_paths in parallel-safety check
docs: clarify codex install flow
chore: bump dependabot interval
```

Types we use: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`.

Always include the Copilot co-author trailer when an AI assistant helped:

```
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## Cutting a release

Releases are tag-driven and fully automated. The bump script keeps the four manifest versions in sync.

```bash
# 1. Make sure main is green and your working tree is clean
git checkout main && git pull

# 2. Bump (semver: patch / minor / major or explicit X.Y.Z)
bash scripts/bump-version.sh 0.2.1
# or:  pwsh -File scripts/bump-version.ps1 -Version 0.2.1

# 3. Review the changes (manifests + CHANGELOG.md stub)
git diff

# 4. Edit the new CHANGELOG section to summarize what shipped

# 5. Commit, tag, push
git commit -am "chore: release v0.2.1"
git tag v0.2.1
git push && git push --tags
```

The `release.yml` workflow:
1. Re-runs validators (catches a tag pushed without prior CI).
2. Extracts the matching `## [0.2.1]` section from `CHANGELOG.md`.
3. Builds `agents-system-setup-v0.2.1.tar.gz`.
4. Creates a GitHub Release with the tarball and notes.
5. Runs a post-release matrix smoke test on Linux/macOS/Windows installing from the tarball.

If the smoke test fails, the release is left as draft — investigate, delete the bad tag, fix forward, re-tag.

## Going public checklist

This repo is private until we're confident the public surface is safe. Before flipping visibility:

- [ ] All workflows in `.github/workflows/` have minimal `permissions:` blocks (no `permissions: write-all`).
- [ ] `SECURITY.md` exists and points to private vulnerability reporting.
- [ ] Branch protection on `main`: require PR, require linear history, require all CI status checks, require 1 approving review (once you have collaborators), block force-pushes.
- [ ] Secret scanning + push protection enabled (Settings → Code security).
- [ ] Dependabot enabled for `github-actions` ecosystem (already configured in `.github/dependabot.yml`).
- [ ] No secrets / tokens / private endpoints committed (`gitleaks` clean run).
- [ ] At least one tagged release (`v0.2.1` or later) so the README install commands point at a reproducible artifact.

Then:

```bash
gh repo edit ytthuan/agents-system-setup \
  --visibility public \
  --accept-visibility-change-consequences
```

## Style notes

- Markdown: use forward slashes everywhere (Windows users get correct rendering too).
- Shell: POSIX `bash` 4+. No `bash`-isms inside `sh`-only contexts.
- PowerShell: target PowerShell 5.1+ on Windows, PowerShell 7+ cross-platform. Prefer `Set-Content -Encoding utf8NoBOM` on PS7; on 5.1 use `[IO.File]::WriteAllText($path, $text, [Text.UTF8Encoding]::new($false))`.
- JSON: 2-space indent, trailing newline.
- YAML frontmatter: quote any value containing `:` or starting with `-`.
- Never write a `permissions:` block in a workflow that's broader than the job needs.

Thanks for contributing!
