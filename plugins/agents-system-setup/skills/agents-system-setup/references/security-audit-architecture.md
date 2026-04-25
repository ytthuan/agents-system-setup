# Security, Audit, Design Pattern, and Architecture Baseline

This reference is mandatory for `init`, `update`, `improve`, and `replicate` flows. The goal is not to make every project heavy-weight; it is to ensure every generated agent system has explicit ownership, boundaries, audit evidence, and architecture rationale.

## 1. Source-backed framework map

Use these sources when generating recommendations. Do not cite unsourced blog posts or invented frameworks.

| Concern | Source | Use in this skill |
|---|---|---|
| Agentic AI and LLM risks | OWASP GenAI Security / LLM Top 10: https://owasp.org/www-project-top-10-for-large-language-model-applications/ | Threat model prompt injection, sensitive information disclosure, insecure tool use, excessive agency, supply-chain exposure, and agent governance gaps. |
| Secure development lifecycle | NIST SSDF SP 800-218: https://csrc.nist.gov/Projects/ssdf | Map generated quality gates to PO, PS, PW, and RV practice groups. |
| MCP authorization and tool risk | MCP Security Best Practices: https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices | Review confused deputy risk, token handling, transport choices, client registration, and server trust boundaries before MCP writes. |
| Repository code security | GitHub Code Security: https://docs.github.com/en/code-security | Recommend secret scanning, code scanning, dependency review, Dependabot, and push protection when GitHub is in scope. |
| Dependency inventory | GitHub Dependency Graph: https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-the-dependency-graph | Require dependency inventory and vulnerable dependency review for software projects. |
| Supply-chain provenance | SLSA v1.1: https://slsa.dev/spec/v1.1/ | Recommend provenance, build integrity, and artifact verification gates for release-producing projects. |
| Policy as code | Open Policy Agent: https://www.openpolicyagent.org/docs/latest/ | Recommend OPA/Rego when policy decisions must be explicit and testable. |
| Cloud architecture quality | Azure Well-Architected Framework: https://learn.microsoft.com/en-us/azure/well-architected/ | Use pillars as quality-attribute prompts: reliability, security, cost, operational excellence, performance efficiency. |
| Architecture views | C4 Model: https://c4model.com/ | Generate context/container/component views or text equivalents. |
| Enterprise architecture | TOGAF Standard: https://www.opengroup.org/togaf | Use only for large organizations or enterprise governance; do not impose on small repos. |

## 2. Required interview inputs

Ask only what is not already detectable. Use one `ask_user` call per question.

| Area | Question | Choices / expected answer |
|---|---|---|
| Data sensitivity | "What is the highest sensitivity of data this project handles?" | `["Public only", "Internal business data", "User personal data / PII", "Payment / financial data", "Health / regulated data", "Secrets or credentials"]` |
| Auth boundary | "How is access controlled?" | `["No auth", "User login", "Service-to-service auth", "OAuth/OIDC", "API keys", "Unsure"]` |
| External tools | "Will agents call external systems or MCP servers?" | `["No external tools", "Approved internal tools only", "Public APIs", "MCP servers", "Unsure"]` |
| Audit trail | "What audit evidence should agents preserve?" | `["Diff summary only", "Test/build evidence", "Security findings", "Decision records / ADRs", "Compliance evidence", "Unsure"]` |
| Deployment / release | "Where do builds or artifacts ship?" | Reuse deployment answer; add registry/package/app-store/cloud signals. |
| Architecture style | "What architecture style should the agents preserve or move toward?" | `["Layered", "Clean/Hexagonal", "Event-driven", "Microservices", "Modular monolith", "Serverless", "CLI/library", "Unsure"]` |
| Critical qualities | "Which quality attributes matter most?" | `["Security", "Reliability", "Maintainability", "Performance", "Cost", "Accessibility", "Compliance"]` |
| Known anti-patterns | "Any architecture or design anti-patterns to avoid?" | Freeform; allow blank. |

## 3. Required plan outputs

Every plan must include these sections before file writes:

### Security & Audit Matrix

| Risk / control | Owner agent | Applies to paths | Evidence required | Source |
|---|---|---|---|---|
| Secrets handling | `@security-auditor` or merged reviewer | `.env*`, config, CI, deployment | Secret scan result or documented manual check | GitHub Code Security |
| MCP/tool boundary | `@orchestrator` + `@security-auditor` | `.mcp.json`, `opencode.json`, agent `mcpServers` | MCP approval gate result + auth/transport rationale | MCP Security Best Practices |
| Dependency risk | `@security-auditor` / `@tester` | lockfiles, manifests | Dependency review or package audit command | GitHub Dependency Graph |
| Prompt/tool abuse | `@threat-modeler` | agents, skills, prompts | OWASP GenAI checklist entries | OWASP GenAI |
| Build provenance | `@release-publisher` | CI/release files | provenance/SBOM plan or explicit not-applicable | SLSA |

### Threat Model Summary

Use this compact structure:

| Asset | Trust boundary | Threat | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| `<data/tool/system>` | `<boundary>` | `<abuse case>` | `<control>` | `@agent` | `planned|done|deferred` |

Minimum threats to consider:
- Prompt injection and instruction smuggling.
- Sensitive data exfiltration through tools, logs, or generated files.
- Excessive agency / unsafe write or deploy permissions.
- Insecure MCP server authorization or confused-deputy flows.
- Supply-chain risks from plugins, packages, skills, or generated scripts.

### Architecture & Design Pattern Matrix

| Decision | Selected pattern | Alternatives considered | Why | Risks / guardrails | ADR |
|---|---|---|---|---|---|
| `<boundary>` | `<pattern>` | `<other patterns>` | `<rationale>` | `<anti-patterns to avoid>` | `docs/adr/<id>.md` or `n/a` |

Default pattern guidance:
- Small apps: layered or modular monolith unless the user states otherwise.
- Plugin/CLI/library: ports-and-adapters for external services; stable public API boundary.
- Microservices: require service ownership, API contracts, and failure-mode notes.
- Event-driven: require idempotency, retry, ordering, and dead-letter handling notes.
- Cloud/infrastructure: map decisions to Well-Architected pillars.

### ADR Index

Do not create ADR files unless the user approves docs writes, but always include an ADR plan:

| ADR | Decision | Owner | Status |
|---|---|---|---|
| `ADR-0001` | `<decision>` | `@architecture-reviewer` | `planned|accepted|deferred` |

### Quality Gates

| Gate | Command or evidence | Owner | Required before done |
|---|---|---|---|
| Build/typecheck | `<repo command>` | `@tester` | yes/no |
| Tests | `<repo command>` | `@tester` | yes/no |
| Lint/format | `<repo command>` | `@tester` | yes/no |
| Secret scan | `<tool or manual evidence>` | `@security-auditor` | yes/no |
| Dependency/SCA | `<tool or manual evidence>` | `@security-auditor` | yes/no |
| Architecture review | `<checklist/ADR diff>` | `@architecture-reviewer` | yes/no |

## 4. Topology rules

The governance baseline is mandatory; dedicated agents are adaptive.

| Project signal | Required ownership |
|---|---|
| Any software project | Security and architecture review must be owned by either dedicated subagents or merged into `@reviewer` with explicit responsibilities. |
| Regulated data, PII, payments, health, credentials | Add `security-auditor`; consider `compliance-auditor`. |
| MCP servers or external tool calls | Add or merge `threat-modeler`; MCP approval gate remains mandatory. |
| CI/release/package publishing | Add supply-chain responsibilities to `release-publisher` or `security-auditor`. |
| Monorepo or multi-service | Add `architecture-reviewer` and make service boundaries explicit. |
| User asks for patterns/architecture | Add `design-pattern-reviewer` or merge into `architecture-reviewer`. |

Small repositories may merge roles into one `security-architecture-reviewer`, but the generated plan must still show the security, audit, architecture, and design-pattern responsibilities.

## 5. Improve-mode scoring

Score existing systems with `ok`, `warn`, `fail`, or `requires-human`.

| Category | OK | Warn | Fail |
|---|---|---|---|
| Security boundaries | Tool/MCP permissions are least-privilege and documented. | Broad tools exist but have rationale. | Broad tools with no rationale or approval gate. |
| Secrets | Secrets are excluded and scanning is documented. | Secret policy exists but no evidence. | Secrets or credentials are embedded or encouraged. |
| Audit evidence | Output contract includes checks, findings, files, and skipped items. | Summary exists but lacks evidence. | No audit trail. |
| Architecture ownership | Directory Architecture maps paths to owners and edit rules. | Owners exist but overlap is unclear. | Agents can edit everything without routing. |
| Design patterns | Pattern decisions and anti-patterns are documented. | Pattern implied but not explicit. | Contradictory patterns or no architecture rationale. |
| Supply chain | Dependencies/plugins/MCP servers cite trusted sources. | Some sources missing. | Invented or untrusted names are recommended. |

Every `warn` or `fail` must produce a proposed delta with rationale and user opt-in before applying.

## 6. Replication metadata

When parsing to Canonical IR, preserve governance fields when present:

| IR field | Meaning |
|---|---|
| `security_controls[]` | Controls, source references, evidence requirements. |
| `audit_requirements[]` | What proof must be collected before completion. |
| `architecture_decisions[]` | Pattern decisions, alternatives, risks, ADR refs. |
| `quality_gates[]` | Build/test/lint/security/architecture checks. |
| `sensitive_paths[]` | Paths with stricter ownership or read-only requirements. |

If a target runtime cannot represent a field directly, emit it into `AGENTS.md` managed sections and include the drop in the lossiness report.

## 7. Anti-patterns

- Treating security as a final optional wrap-up item only.
- Writing MCP config before the approval gate.
- Creating "security-auditor" with broad write access by default.
- Generating architecture diagrams or ADRs that are not tied to path ownership or agent responsibilities.
- Recommending plugins, MCP servers, or policy tools without a source URL.
- Adding enterprise frameworks like TOGAF to small repositories unless the user asks for enterprise governance.
