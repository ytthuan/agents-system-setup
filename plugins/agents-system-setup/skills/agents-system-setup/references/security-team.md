# Security Team Generation

Use this reference when the user asks the plugin to generate a dedicated
security team, bug-hunting team, application-security review team, vulnerability
analysis workflow, or disclosure/triage workflow.

This reference is intentionally source-backed and original. Do not copy text,
artifact layouts, or workflow schemas from proprietary security plugins. If a
vendor security plugin is useful, recommend it through
[plugin discovery](./plugin-discovery.md) with vendor and license attribution.

## Source-backed model

| Source | Public concept used here |
|---|---|
| OWASP SAMM | Risk-driven secure software lifecycle across governance, design, implementation, verification, and operations; threat assessment, security testing, defect management, and incident management streams. |
| NIST SSDF SP 800-218 | Secure development practice groups: Prepare the Organization, Protect the Software, Produce Well-Secured Software, and Respond to Vulnerabilities. |
| OWASP Vulnerability Disclosure Cheat Sheet | Clear reporting channel, scope and terms, sufficient reproduction detail, reasonable timelines, open communication, advisories/CVEs, credit, and researcher-safe boundaries. |
| CISA Coordinated Vulnerability Disclosure | Coordinated identification, remediation, disclosure, mitigation sharing, and stakeholder synchronization for vulnerabilities. |
| FIRST CVSS v4 | Base, Threat, Environmental, and Supplemental metrics; enrich technical severity with environment-specific risk before prioritization. |
| CWE / OWASP Top 10 | Common weakness vocabulary and web risk categories for finding classification. |

## When to generate a dedicated security team

Generate a dedicated security team when any of these signals is present:

- the user selects `Security team / Bug hunting` during the interview;
- the request mentions bug hunting, vulnerability research, appsec review,
  penetration-testing support, disclosure triage, bug bounty, exploitability
  analysis, threat modeling, security analysis, or remediation verification;
- the project handles PII, payments, health, credentials, regulated data,
  external tools/MCP, CI/release infrastructure, cloud infrastructure, or
  multiple services and the user wants stronger security coverage than the
  baseline `security-auditor`.

Do not generate the full team for ordinary software projects by default. Keep the
existing security/audit baseline unless the user requests this topology or the
risk intake justifies a dedicated team.

## Security team sizing

| Depth | Use when | Roles |
|---|---|---|
| Baseline | normal software project with routine governance needs | `security-auditor` or merged reviewer responsibility |
| Dedicated | user asks for security team, bug hunting, or security analysis | security lead, threat modeler, vulnerability researcher, validation/reproduction analyst, attack-path/severity analyst, remediation verifier |
| Expanded | large, regulated, cloud, supply-chain, bug-bounty, or incident-response program | add supply-chain security, cloud/infra security, disclosure/bug-bounty triage, incident-response liaison, compliance auditor |

The security lead may be a separate role in large setups. In compact setups, the
orchestrator owns program coordination and the security roles remain specialists.

## Role roster

| Role | Responsibility | Default permissions | Primary outputs |
|---|---|---|---|
| `security-lead` | Own security-team scope, routing, authorization boundaries, and final synthesis | read-only; no final business approval unless the orchestrator delegates it | scope, waves, accepted risk assumptions, consolidated finding state |
| `threat-modeler` | Map assets, trust boundaries, attacker stories, assumptions, and security invariants | read-only | threat model summary, attack surface map, security invariants |
| `vulnerability-researcher` | Inspect scoped code paths for plausible weaknesses and source/control/sink candidates | read-only plus bounded local search | candidate inventory, affected paths, evidence sources, duplicate hints |
| `validation-reproducer` | Confirm, falsify, or bound candidate findings with tests, PoCs, static trace, or harnesses | read-only by default; runner only with approval | validation status, reproduction steps, counterevidence, proof gaps |
| `attack-path-analyst` | Establish reachability, exploitability, severity, priority, and realistic impact | read-only | attack path facts, severity rationale, confidence, business-priority notes |
| `remediation-verifier` | Check proposed fixes, regression tests, and bypass variants | read-only unless routed through owning implementer | fix verification, non-regression evidence, residual risk |
| `bug-bounty-triage` | Handle external reports, scope, duplicate checks, researcher-safe communication, disclosure state | read-only; no public disclosure without approval | triage state, needs-info questions, disclosure notes |
| `supply-chain-security` | Review dependencies, release provenance, lockfiles, build/release workflows, and artifact trust | read-only plus approved audit commands | dependency/provenance findings, affected manifests, fix owner |
| `cloud-infra-security` | Review IaC, cloud permissions, network exposure, policy, and secrets boundaries | read-only plus approved audit commands | cloud/infra risk notes, least-privilege deltas, evidence |
| `incident-response-liaison` | Connect confirmed high-impact findings to response, containment, and communication workflow | read-only | incident trigger notes, escalation path, containment evidence |
| `compliance-auditor` | Map controls and evidence to requested compliance needs | read-only | compliance evidence matrix, gaps, audit artifacts |

## Operating workflow

1. **Scope and authorization** - Confirm owned assets, in-scope paths, testing
   limits, external scanning rules, data handling, and approvals. If unclear,
   return `question_request` before risky action.
2. **Threat model** - Identify assets, trust boundaries, attacker-controlled
   inputs, security invariants, and likely high-impact failure modes.
3. **Discovery** - Inspect scoped code and supporting context for plausible
   source/control/sink or broken-invariant candidates. Keep candidates specific
   and avoid grouping independent issues without evidence.
4. **Validation** - Confirm, falsify, or defer each candidate using the strongest
   bounded method available: focused tests, realistic-interface reproduction,
   local harness, static trace, or explicit proof-gap note.
5. **Attack-path and severity** - Establish reachability, preconditions,
   boundary crossing, impact, likelihood, counterevidence, confidence, severity,
   and priority.
6. **Remediation** - Route fixes to the owning implementation agent. Security
   roles propose minimal safe fixes and tests; they do not write code unless the
   Directory Architecture grants ownership and approvals are recorded.
7. **Verification and closure** - Verify the original issue no longer
   reproduces, legitimate behavior still works, nearby bypasses were checked,
   and disclosure/triage state is updated.

## Scan modes

| Mode | Scope rule | Required control |
|---|---|---|
| Diff-scoped review | Start from changed files and the minimum supporting code needed to understand the security impact. | Stay anchored to the diff; expand only to directly affected siblings or shared controls. |
| Repository-wide review | Start from product/runtime surfaces, trust boundaries, privileged workflows, and security-sensitive components. | Use a compact coverage plan so top risks and explicit exclusions are auditable. |
| Advisory or report validation | Start from the reported weakness, affected version/path, and claimed source/control/sink. | Close the exact report as confirmed, duplicate, not reproducible, out of scope, needs info, mitigated, or deferred. |
| Remediation verification | Start from a validated finding and proposed fix. | Prove the vulnerable path is fixed and normal behavior still works. |

## Authorization and safety boundaries

Generated security teams must default to authorized assets and local repository
evidence. They must not imply permission to attack third-party systems,
production services, or user data.

Hard rules:

- No external scanning, exploit execution, credential use, persistence, data
  exfiltration, destructive tests, production traffic, or disclosure outreach
  without explicit approval and scope.
- No storing secrets, raw tokens, PII samples, exploit payload dumps, or private
  researcher communications in generated memory.
- No broad write access for discovery, validation, attack-path, triage, or
  compliance roles.
- Remediation writes route through the owning implementation agent unless a
  narrow remediation role is explicitly granted owned paths.
- Missing product policy, authorization scope, or test permission becomes one
  `question_request`, not an assumption.

## Evidence and output contract

For every candidate, finding, suppression, or deferral, require enough evidence
for another security reviewer to reconstruct the decision.

```text
Security analysis:
  scope: <diff | repository | report | remediation | program>
  authorization: <owned-code | approved-target | needs-approval>
  asset_or_boundary: <asset/trust boundary>
  candidate_or_finding: <id/title>
  affected_locations: <file:line list or "not established">
  attacker_control: <yes | plausible | no | unknown>
  broken_control_or_sink: <control/sink/invariant>
  validation_status: <confirmed | likely | needs-info | duplicate | not-reproducible | out-of-scope | mitigated | deferred>
  evidence:
    - <command/test/static trace/file reference>
  counterevidence:
    - <specific safe control or limiting fact, or "none found">
  severity:
    cwe: <ids or "none">
    cvss_notes: <base/threat/environmental considerations or "n/a">
    priority: <P0 | P1 | P2 | P3 | n/a>
    rationale: <why this priority>
  remediation:
    owner: <agent/team>
    fix_guidance: <minimal safe fix or "n/a">
    verification: <test/reproduction/non-regression evidence>
  proof_gaps: <remaining uncertainty or "none">
```

Use concise Markdown in final reports. Do not dump raw schemas unless the user
asked for machine-readable output.

## Severity and triage policy

- Classify weakness type with CWE or OWASP-style categories when known.
- Use CVSS-style technical factors for vulnerability characteristics, but do not
  treat a score as the whole business priority.
- Enrich severity with environment, reachability, data sensitivity, privilege
  boundary, exploit maturity, blast radius, and compensating controls.
- High or critical priority requires a realistic in-scope attacker path and
  material security impact.
- Downgrade or suppress issues that are self-only, out of scope, not
  attacker-reachable, already require equivalent privileges, or lack a concrete
  security impact.
- Preserve proof gaps instead of hiding them. `deferred` is acceptable when the
  next evidence step is clear and proportionate.

## Bug-bounty and disclosure lane

Use this lane only when the user asks for disclosure or external-report triage.

| Stage | Expected handling |
|---|---|
| Intake | Record report source, scope, affected asset, reproduction detail, and communication constraints. |
| Triage | Check authorization scope, duplicates, completeness, impact, severity, and required follow-up questions. |
| Coordination | Route valid issues to owners, preserve reporter-safe communication notes, and avoid public disclosure without approval. |
| Remediation | Track fix owner, target evidence, retest plan, and residual risk. |
| Closure | Record final state: fixed, duplicate, informative, not applicable, out of scope, needs info, or deferred. |

## Provider rendering notes

- Copilot, Claude, and OpenCode can render each role as a normal subagent using
  provider-native least-privilege permissions.
- Codex renders security roles as `.codex/agents/*.toml`; reviewer/security
  roles use `sandbox_mode = "read-only"` unless the plan grants narrow write
  ownership.
- Gemini keeps fan-out in the root session; security subagents return structured
  findings and follow-up work to the root/orchestrator.
- Every runtime uses the Plan Handoff Contract; security tasks use full-form
  packets when they involve validation, remediation, disclosure, external tools,
  exploit execution, or multi-agent fan-out.

## Anti-patterns

- Copying proprietary security-plugin prompts, report schemas, artifact paths, or
  workflow wording.
- Creating one broad `security-god-agent` with edit, shell, web, and disclosure
  authority.
- Treating grep hits as findings without source/control/sink evidence.
- Reporting scary bug classes without reachability, impact, counterevidence, and
  proof-gap notes.
- Letting one safe sibling suppress a different candidate without exact
  counterevidence.
- Running unapproved tests against third-party or production systems.
- Auto-installing security plugins, MCP servers, or external scanners.
- Treating remediation as complete without reproducing or otherwise checking the
  original vulnerable path.
