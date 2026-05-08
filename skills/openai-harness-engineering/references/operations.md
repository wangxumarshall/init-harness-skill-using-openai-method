# Harness Operating Model

Use this reference when the user wants the harness to help a project run for a long time, recover from failures, or improve itself.

## Work Loop

For non-trivial work, agents should use this loop:

1. **Orient**: Read `AGENTS.md`, active plans, architecture, product sense, and relevant runbooks.
2. **Plan**: Create or update `docs/exec-plans/active/<task>.md` with goal, scope, success criteria, and validation commands.
3. **Execute**: Make surgical edits. Prefer established local patterns and shared utilities.
4. **Verify**: Run the narrowest meaningful checks first, then broader checks when risk justifies it.
5. **Record**: Write validation results, decisions, unresolved risks, and next steps into the active plan.
6. **Close**: Move completed plans to `docs/exec-plans/completed/` with outcome, shipped changes, and follow-up tasks.

## Persistent State

Generated plans should include:

- Task title and owner/agent.
- Date started and last updated.
- User request and interpreted goal.
- Non-goals.
- Current status.
- Files and modules touched.
- Decisions made.
- Validation commands and results.
- Open questions and blockers.
- Follow-up work.

This is what lets a new agent resume after context compaction or a new session.

## Reliability Loop

When a bug or incident appears:

1. Reproduce with the smallest local command or browser flow.
2. Capture logs, screenshots, traces, inputs, versions, and environment.
3. Write a record in `docs/incidents/` if the issue affects users, data, availability, or trust.
4. Add or update a runbook in `docs/runbooks/` when the fix teaches future agents how to diagnose a class of failure.
5. Add a regression test or structural check when practical.

## Harness Maintenance Loop

At regular intervals or after major changes:

- Check that `AGENTS.md` links still exist.
- Run the documented setup and validation commands from a clean checkout or ephemeral worktree.
- Remove stale generated docs, or mark them deprecated.
- Convert repeated manual review comments into lint rules, tests, scripts, or checklist items.
- Improve failing command output so it tells agents what to do next.

## Agent Review Loop

For larger changes, use one agent to implement and another to review when available. Reviews should focus on:

- Behavioral bugs.
- Broken boundaries.
- Missing validation.
- Security and data risks.
- Divergence from product goals.

Do not use review agents as a substitute for executable checks.
