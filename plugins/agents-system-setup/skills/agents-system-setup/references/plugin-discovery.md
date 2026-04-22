# Plugin / Skill / MCP Discovery — opt-in with rationale

Source of truth for marketplaces: see [marketplaces.md](./marketplaces.md).
Per-platform install commands: see [platforms.md](./platforms.md).

## Hard Rules

1. **Never invent** plugin/skill/MCP names or URLs.
2. **Marketplace tiers first.** Free-text GitHub search is a Tier-3 fallback only.
3. **Mandatory rationale fields** for every candidate. Empty `why_recommended` or `tradeoffs` ⇒ drop the candidate.
4. **Per-capability `ask_user`** — present at most 3 candidates with rationale and let the user pick or skip.
5. **MCP candidates flow into the Phase 3.5 approval gate** — selection here is necessary but not sufficient.

## Candidate Schema (must populate every field)

```yaml
name:                   # e.g., playwright-mcp
source_tier:            # 1 (default), 2 (catalog), or 3 (fallback)
source_marketplace:     # e.g., github/awesome-copilot
repo_url:
bundles:                # any of: agents | skills | hooks | mcp | lsp
install_command_per_platform:
  copilot-cli:          # e.g., /plugin install microsoft/playwright-mcp
  claude-code:          # e.g., claude plugins install ...
  opencode:             # e.g., opencode plugin install ... (if applicable)
why_recommended:        # one sentence, project-specific
tradeoffs:              # one sentence — what to consider before picking
```

## Search Procedure (per capability)

1. **Tier 1** — fetch and grep:
   - https://github.com/github/copilot-plugins
   - https://github.com/github/awesome-copilot
2. **Tier 2** — fetch and grep:
   - https://github.com/anthropics/skills
   - https://github.com/anthropics/claude-code
   - https://github.com/claudeforge/marketplace
3. Stop once you have 1–3 viable candidates.
4. **Tier 3 (fallback only)** — `github-search_repositories`:
   - `topic:mcp <capability>` (sort: stars, perPage 5)
   - `topic:copilot-plugin <capability>`
5. Validate each candidate by fetching its README before recommending. If README is missing or vague, drop it.

## Comparison Table (render to user)

```
Capability: playwright

| # | Candidate          | Tier | Bundles      | Why                                          | Trade-offs                          |
|---|--------------------|------|--------------|----------------------------------------------|-------------------------------------|
| 1 | playwright-mcp     | 1    | mcp + skill  | Maintained by Microsoft; first-class browser  | Pulls headless Chromium (~150 MB)   |
| 2 | puppeteer-mcp      | 3    | mcp          | Lighter alternative                          | Community-maintained; less polish   |
```

Then `ask_user`:
> "For capability **playwright**, which would you like?"
> Choices: `["1: playwright-mcp (Tier 1)", "2: puppeteer-mcp (Tier 3)", "Show more (Tier-3 fallback)", "None — skip this capability"]`

## "Show more" branch

- Run Tier-3 search again with broader terms.
- Append up to **+5 additional candidates**, then re-render the table.
- After "Show more" once, the next prompt no longer offers "Show more" — final pick or skip.

## Capability → Search-Hint Table

These are *search hints*, not assumed-existing entries.

| Capability | Search hints |
|---|---|
| Browser / E2E | `playwright`, `puppeteer` |
| GitHub | `github` (official: github/github-mcp-server) |
| Filesystem | `filesystem` |
| Database | `postgres`, `sqlite`, `mysql` |
| Cloud — Azure | `azure` |
| Cloud — AWS | `aws` |
| Cloud — GCP | `gcp`, `google cloud` |
| Search | `brave search`, `kagi` |
| Docs | `context7`, `microsoft docs` |
| Containers | `docker`, `kubernetes` |
| Observability | `grafana`, `datadog` |
| Design | `figma` |
| Vector DB | `pinecone`, `weaviate`, `qdrant` |

## MCP Approval Rendering (handed off to Phase 3.5)

Only the user's *selected* MCP candidates reach Phase 3.5. Render proposal per platform:

```jsonc
// proposed: .mcp.json (Copilot CLI + Claude Code)
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}" }
    }
  }
}
```

```jsonc
// proposed: opencode.json › mcp (OpenCode)
{
  "mcp": {
    "github": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
      "environment": { "GITHUB_PERSONAL_ACCESS_TOKEN": "{env:GITHUB_PERSONAL_ACCESS_TOKEN}" },
      "enabled": true
    }
  }
}
```

Then ask:
> "Approve writing the above MCP config?"
> Choices: `["Approve all (Recommended)", "Approve selectively (per-server)", "Skip MCP entirely"]`

## Anti-patterns

- Recommending without `why_recommended` / `tradeoffs`.
- Auto-installing instead of presenting a choice.
- Mixing platforms in a single proposed file (Copilot/Claude share `.mcp.json`; OpenCode is separate).
- Forgetting that "skip this capability" is always a valid choice.
