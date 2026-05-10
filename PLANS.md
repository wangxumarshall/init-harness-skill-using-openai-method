# Planning and Persistent Execution

`docs/exec-plans/` is the durable trajectory index for non-trivial work in this repository.

The active exec-plan is the trajectory index:

```text
Request -> Context -> Plan -> Actions -> Decisions -> Validation -> Incidents -> Learnings -> Closure
```

## When To Create a Plan

- changes span more than one file or subsystem
- the work includes investigation before implementation
- the task needs multiple validation steps
- the work may outlive one session

## Closing Work

1. Record validation commands and results.
2. Record changed files or modules.
3. Move the plan from `docs/exec-plans/active/` to `docs/exec-plans/completed/`.
