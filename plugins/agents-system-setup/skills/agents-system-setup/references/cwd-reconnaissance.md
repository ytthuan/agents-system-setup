# CWD Project Reconnaissance

Phase 1 runs a **safe-readonly** reconnaissance of the current working
directory before the interview begins. Recon grounds Q1 (purpose), Q3
(project type), Phase 1.7 (domain detection), and the Phase 2 plan
(Directory Architecture seeds, subagent roster suggestions) in evidence the
user can correct.

> Recon is **read-only**. It never writes, opens data files, or echoes
> secret-shaped strings. The user always confirms or corrects the card
> before the interview continues.

## Default scope

`recon_scope = safe-readonly` is the default and the only scope this
reference covers. Higher scopes (`sample-text`, `include-small-data`) are
out of scope for now and must not be enabled without explicit user opt-in.

| Concern | Rule |
|---|---|
| Path enumeration | Allowed for the entire cwd, capped at depth 3 from the repo root. |
| README / docs read | Allowed; `README*.md`, `docs/**/*.md`, `CONTRIBUTING.md`, `SECURITY.md`. Cap each file at 100 lines. |
| Source tree shape | Allowed; list directories up to depth 2, count files, do not open them. |
| Manifest read | Allowed for `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `*.csproj`, `Package.swift`, `build.gradle`, `pom.xml`, `mix.exs`, `composer.json`. Cap each at 200 lines. |
| Infra signals | List presence of `Dockerfile`, `docker-compose*.yml`, `.github/workflows/`, `terraform/`, `*.tf`, `helm/`, `Makefile`, `Justfile`, `Procfile`. Do not open. |
| Data signals | Enumerate paths only — `data/`, `datasets/`, `notebooks/`, `samples/`, `fixtures/`, `seeds/`, `*.csv`, `*.parquet`, `*.jsonl`, `*.ndjson`, `*.duckdb`, `*.db`, `*.sqlite`, `*.feather`, `*.arrow`, `*.h5`, `*.geojson`, `*.shp`, `*.dvc`, `*.ipynb`. Never open. |
| Tests signals | Enumerate `tests/`, `test/`, `__tests__/`, `*_test.go`, `*.spec.{ts,js}`, `*_spec.rb`. Do not open. |
| Schema files | List paths only — `schema.sql`, `*.proto`, `*.graphql`, `openapi.{yaml,json}`, `swagger.{yaml,json}`. Do not open unless < 50 lines and explicitly part of docs. |

### Always-skip directories

`node_modules/`, `.venv/`, `venv/`, `.tox/`, `target/`, `dist/`, `build/`,
`out/`, `vendor/`, `.next/`, `.nuxt/`, `.cache/`, `.gradle/`, `.idea/`,
`.vscode/cache/`, `coverage/`, `htmlcov/`, `__pycache__/`, `.mypy_cache/`,
`.pytest_cache/`, `.ruff_cache/`, `.terraform/`, `.serverless/`,
`.copilot/session-state/`, `.agents-system-setup/`.

### Privacy guardrails

1. **No data file reads.** `*.csv`, `*.parquet`, `*.jsonl`, `*.ndjson`,
   `*.duckdb`, `*.db`, `*.sqlite`, `*.feather`, `*.arrow`, `*.h5`,
   `*.geojson`, `*.shp`, `*.dvc`, `*.ipynb`, plus any path under a
   `data/` / `datasets/` / `samples/` / `fixtures/` / `seeds/` directory.
2. **Magic-byte detection before any read.** Reject the read if the first
   512 bytes contain a NUL byte or fail UTF-8 decode. Treat the file as
   binary and enumerate the path only.
3. **Size cap.** Skip the read if the file is larger than 64 KB.
4. **Secret redaction.** If a read text file matches any of the patterns
   below, redact the matched substring with `[REDACTED:<kind>]` in the
   captured snippet, **drop the entire matched line** from the
   Reconnaissance Card, and record one `privacy_redactions[]` entry with
   `{path, kind, line_no, count}`. Do not echo the redacted content back
   to the user.
   - AWS access key id: `AKIA[0-9A-Z]{16}`
   - AWS secret access key (env-style): `(?i)AWS_SECRET_ACCESS_KEY\s*[:=]\s*['"]?[A-Za-z0-9/+=]{30,}['"]?`
   - Generic API key context (quoted): `(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['"][^'"]{8,}['"]`
   - Generic API key context (unquoted env-style): `(?i)\b(api[_-]?key|secret|token|password)\s*=\s*[^\s'"]{16,}`
   - GitHub classic token: `gh[pousr]_[A-Za-z0-9]{36,}`
   - GitHub fine-grained PAT: `github_pat_[A-Za-z0-9_]{22,}`
   - OpenAI / Anthropic style key: `sk-(?:ant-)?[A-Za-z0-9_\-]{20,}`
   - Slack token: `xox[abprs]-[A-Za-z0-9-]+`
   - npmrc auth token: `(?i)//[^/\s]+/:?_authToken\s*=\s*\S+`
   - Authorization header: `(?i)Authorization:\s*Bearer\s+[A-Za-z0-9._\-+/=]+`
   - Google service-account private key field: `"private_key"\s*:\s*"-----BEGIN [A-Z ]*PRIVATE KEY-----`
   - Private key header (any): `-----BEGIN [A-Z ]*PRIVATE KEY-----`
   - JWT triplet: `eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+`
5. **Symlink discipline.** Resolve symlinks but never follow them outside
   the cwd; if the target is outside, list the path only and record
   `out_of_tree=true`.

## Reconnaissance Card schema

The card is rendered to the user via `ask_user` after recon completes.
Keep each field compact; long lists collapse to counts plus the top three
exemplars.

```yaml
project_kind_signals:    # ordered list, e.g. ["data-ml", "infrastructure"]
languages_seen:          # {language: file_count}
frameworks_seen:         # ordered list of detected frameworks/runtimes
infra_signals:           # {kind: [paths]}
data_signals:            # {kind: count, exemplars: [paths]}
docs_signals:            # {kind: [paths], summary: "<<= 200 chars"}
tests_signals:           # {kind: count, exemplars: [paths]}
notable_paths:           # ["path1", "path2", ...] (<=10 entries)
evidence_caps:           # {readme_lines, docs_files, manifests}
privacy_redactions:      # [{path, kind, count}]
recon_skipped: false     # true only when the user explicitly opts out
```

## User confirmation prompt

After recon completes, render the card and ask:

> "Here is what I detected in the project. Accept, correct, or skip?"
> Choices: `["Accept (Recommended)", "Correct one or more fields", "Skip recon (use interview answers only)"]`

- `Accept` — feed the card straight into Phase 1.7 / Phase 2.
- `Correct` — open follow-up `ask_user` calls per field the user wants to
  fix; preserve the rest.
- `Skip recon` — record `recon_skipped: true` and continue with the normal
  interview. The output contract reports `Recon: skipped`.

## Outputs

- The card is **transient working memory** for this session; it does not
  get committed.
- Optional snapshot: when `artifact_tracking != personal-global`, the
  orchestrator may write a compact snapshot into the `Read First` block of
  `AGENTS.md` (≤5 lines) so future sessions inherit the same grounding.
- The output contract reports `Recon: <signals|n/a|skipped>` and the
  number of redactions.

## Anti-patterns

- Opening data files (CSV / parquet / SQLite / parquet / notebooks).
- Reading manifest or doc files past the cap (200 / 100 lines).
- Echoing secret-shaped substrings back to the user.
- Following symlinks outside the cwd.
- Treating the card as authoritative without user confirmation.
- Using recon evidence to bypass interview gates (artifact tracking, MCP
  approval, plan approval, security-sensitive write gates).
- Running recon at scopes other than `safe-readonly` without explicit user
  opt-in.
