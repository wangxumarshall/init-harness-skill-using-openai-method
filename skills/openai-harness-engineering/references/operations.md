# Harness Operating Model

Use this reference when the user wants the harness to support long-running work.

## Work Loop

1. Orient from `AGENTS.md` and the smallest relevant linked docs.
2. Create or update an exec-plan for non-trivial work.
3. Make surgical changes.
4. Run deterministic validation.
5. Record evidence, decisions, and handoff state.
6. Close the plan into `docs/exec-plans/completed/`.

## Trajectory Model

The exec-plan is the trajectory index:

```text
Request -> Context -> Plan -> Actions -> Decisions -> Validation -> Incidents -> Learnings -> Closure
```

The harness keeps existing names and uses them deliberately:

- `exec-plans`: task trajectory index
- `validation logs`: evidence layer
- `runbooks`: repeated setup/debug/maintenance knowledge
- `incident records`: failure branch when user, data, availability, or trust are affected
- `generated manifest`: harness metadata

Record observable engineering facts, concise rationale, commands, results, artifacts, and handoff state. Do not record chain-of-thought or sensitive payloads.

## Maintenance Loop

Thin harnesses need recurring cleanup:

- run a drift scan
- clear stale placeholders
- close or refresh stale active plans
- convert repeated manual review comments into scripts, tests, or CI
