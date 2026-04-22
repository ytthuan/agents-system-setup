<!-- Thanks for contributing! Please complete this checklist. -->

## Summary

<!-- What does this PR do, in one or two sentences? -->

## Type of change

- [ ] feat — new capability
- [ ] fix — bug fix
- [ ] docs — documentation only
- [ ] refactor — no behavior change
- [ ] chore — tooling, CI, deps
- [ ] test — adds or fixes tests

## Checklist

- [ ] I ran `bash scripts/validate.sh` (or `pwsh scripts/validate.ps1`) locally and it passed
- [ ] If I changed any plugin manifest, I bumped versions consistently across all four (`plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`) — or used `scripts/bump-version.sh`
- [ ] If user-facing behavior changed, I updated `CHANGELOG.md` under the `[Unreleased]` section
- [ ] If I added a new file, I checked it picks up the right line endings via `.gitattributes` (`*.sh` LF, `*.ps1` CRLF)
- [ ] CI is green on Linux, macOS, and Windows

## Linked issues

<!-- Closes #123, refs #456 -->

## Notes for the reviewer

<!-- Anything tricky, intentional non-obvious choices, or follow-ups deferred to a future PR. -->
