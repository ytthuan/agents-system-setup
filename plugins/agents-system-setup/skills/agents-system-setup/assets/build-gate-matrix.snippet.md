<!-- agents-system-setup:build-gate-matrix:start -->
**Enabled:** strictness={{BUILD_GATE_STRICTNESS}}; trigger=every code change.
Compute `max(size_bucket, criticality_bucket)` and load the local
`code-change-build-gate` skill before implementation sign-off.
**Logical owners:** build/review/bug-hunt=Quality Gates rows;
unit={{UNIT_TEST_OWNER}}; e2e={{E2E_OWNER}};
validation={{CHANGE_VALIDATOR_OWNER}}; review is independent of writer.
Required gates and evidence are fail-closed. Missing or denied skill context
blocks the affected code action/sign-off.
<!-- agents-system-setup:build-gate-matrix:end -->
