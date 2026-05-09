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

## Trajectory Semantics

For a non-trivial task, the active exec-plan is the trajectory index. It should connect:

```text
Request -> Context -> Plan -> Actions -> Decisions -> Validation -> Incidents -> Learnings -> Closure
```

This does not create a new logging system and does not rename existing harness concepts. It gives each existing file type a clear job:

- `exec-plans`: index the task trajectory and current handoff state.
- `validation logs`: preserve evidence when command results, screenshots, traces, or smoke notes need to survive the session.
- `incident records`: branch out when a failure affects users, data, availability, or trust.
- `ADRs`: preserve durable architecture or product decisions that outlive one task.
- `runbooks`: capture repeatable setup, debugging, operations, or recovery knowledge learned during the task.
- `generated manifests`: describe the harness structure and required exec-plan sections.

Keep the exec-plan factual. Record files read, actions taken, command results, artifacts, links, decisions, blockers, and concise rationale. Do not record full chain-of-thought, secrets, sensitive payloads, or raw logs that contain private data.

Split content out of the exec-plan when:

- A validation result has enough evidence or artifacts to merit a stable `docs/validation/` record.
- A failure has user, data, availability, or trust impact and needs a `docs/incidents/` record.
- A decision changes architecture, durable product behavior, dependency policy, or operating model and needs an ADR or design doc.
- A debugging or operations procedure is likely to repeat and should become a `docs/runbooks/` entry.

## Persistent State

Generated plans should include:

- Task title and owner/agent.
- Date started and last updated.
- User request and interpreted goal.
- Non-goals.
- Current status.
- Context read and why it matters.
- Planned steps and actions taken.
- Decisions made and decision links.
- Validation commands, results, and evidence links.
- Incident links when applicable.
- Learnings, closure notes, open questions, blockers, follow-up work, and next-agent handoff.

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
