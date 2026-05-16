# CWD Project Reconnaissance

Phase 1 runs a **safe-readonly** reconnaissance of the current working
directory. Recon is **purpose-driven**: Phase 0 captures the user's
headline purpose first (or the explicit `"exploring"` sentinel), and
Phase 1 recon uses that intent to score and rank signals. The card
grounds Q1 (purpose confirmation), Q3 (project type), Phase 1.7 (domain
detection), and the Phase 2 plan (Directory Architecture seeds,
subagent roster suggestions) in evidence the user can correct.

> Recon is **read-only**. It never writes, opens data files, or echoes
> secret-shaped strings. The user always confirms or corrects the card
> before the interview continues.

## Default scope

`recon_scope = safe-readonly` is the default and the only scope this
reference covers. Higher scopes (`sample-text`, `include-small-data`) are
out of scope for now and must not be enabled without explicit user opt-in.

## Purpose-aware scoring

Phase 0 sub-step 0 captures `headline_purpose` before the directory is
scanned. Phase 1 recon uses it to **score and highlight** signals so the
most purpose-relevant groups bubble to the top of the Reconnaissance
Card. Scoring is keyword + manifest overlap, not embeddings.

### Scoring rubric

1. **Tokenize** `headline_purpose`:
   - Lowercase the headline.
   - Split on whitespace, commas, `/`, and the conjunctions
     `and`/`or`/`&` to yield one clause per fragment so multi-purpose
     statements like `"build a payments API and a mobile client"` keep
     their facets separable.
   - Drop English stopwords plus generic intent stopwords
     (`build`, `create`, `make`, `setup`, `improve`, `audit`, `agent`,
     `agents`, `system`, `project`, `app`, `application`).
   - Keep alphanumeric tokens of length ≥ 2.
2. **Per signal group** compute `purpose_relevance` as the **max across
   clauses** (so a group strongly matching one clause is not diluted by
   weak matches in another):
   - `high` — ≥2 token matches against group exemplars **or** the
     group's manifest declares a matching framework/language.
   - `med` — exactly 1 token match **or** a soft category match
     (purpose mentions "API", group is `infra_signals.dockerfile`).
   - `low` — no token match but group is non-empty.
   - `n-a` — group is empty **or** `headline_purpose == "exploring"`.
3. **Sort** the card by relevance: `high` → `med` → `low` → `n-a`.
4. **Never filter.** Every non-empty group is still rendered; only
   ordering changes. Discoverability matters more than tidiness.
5. **Improve-mode caveat.** Purpose-relevance affects **card ordering
   only**. The improve-mode audit still covers all runtime, security,
   governance, and architecture surfaces regardless of how a group
   ranked here — see `Phase 1.5 — Improve / Replicate branch` in
   `SKILL.md`.

### Exploring fallback

The `"exploring"` sentinel is set **only** when the user selects the
exact labeled choice `"I'm exploring — let recon lead"` from the
Phase 0 sub-step 0 prompt. The Phase 0 implementation **must
normalize** this selection to the literal string
`headline_purpose = "exploring"`; do not infer the sentinel from vague
freeform answers like `"not sure"`, `"whatever"`, blank input, or
short impatient strings. Vague answers are stored verbatim and pass
through Q1 confirmation as a real (if weak) headline.

When `headline_purpose == "exploring"`:

- Set every group's relevance to `n-a`.
- Render the card in default insertion order.
- After the user confirms the card, the orchestrator re-asks the Phase 0
  sub-step 0 purpose question as a fresh ask (Q1 in interview terms),
  now grounded in what the card showed.

This keeps the discovery-led path available without back-doors that
restore the old recon-first flow for users who *did* state intent.

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
   - npmrc auth token (registry-scoped or bare): `(?i)(?://[^/\s]+/:?_authToken|(?:^|\s)_authToken)\s*=\s*\S+`
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
headline_purpose:        # string from Phase 0, or the literal "exploring"
purpose_relevance:       # {<group_name>: "high"|"med"|"low"|"n-a"}
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

- When `headline_purpose` is a real headline (groups sorted by
  `purpose_relevance`):
  > "Here is what I detected in the project, sorted by relevance to
  > your stated purpose. Accept, correct, or skip?"
- When `headline_purpose == "exploring"` (default order, no scoring):
  > "Here is what I detected in the project. Accept, correct, or skip?"

Choices (both variants): `["Accept (Recommended)", "Correct one or more fields", "Skip recon (use interview answers only)"]`

When `headline_purpose == "exploring"`, the orchestrator re-asks the
purpose question (Phase 0 sub-step 0) **after** this confirmation, now
grounded in what the card showed.

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
- **Letting recon propose purpose before the user states it** — anchors
  the interview on what the directory looks like instead of what the
  user wants. Phase 0 sub-step 0 captures `headline_purpose` first; the
  card scores against that intent. The only exception is the explicit
  `"exploring"` sentinel set by the user.
- **Treating blank or ambiguous answers as `exploring`** — the sentinel
  is set only by the exact labeled choice `"I'm exploring — let recon
  lead"`. Vague freeform answers (`"not sure"`, `"whatever"`, empty
  input) are weak headlines, not exploring; store them verbatim and
  pass them to Q1 confirmation.
- **Filtering out low-relevance groups** — never drop non-empty groups
  from the card; only sort. Filtering hides signals the user might want
  to correct.
