---
description: Set up, migrate, or roll back this project's agent system
subagent: false
---

Load the `agents-system-setup` skill using the skill tool, then handle these
arguments in the current host session:

$ARGUMENTS

Examples: `migrate monolithic`, `migrate monolithic --dry-run`,
`migrate specialists`, `rollback`. Follow the skill's explicit command routing.
If the skill cannot be loaded, report that and stop before any write.
