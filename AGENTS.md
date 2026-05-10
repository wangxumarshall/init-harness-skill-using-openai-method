# openai-harness-engineering Agent Map

This repository dogfoods a thin harness for the skill itself. Use it as a map, not a manual.

## Start Here

1. Read the current request.
2. Read the smallest linked doc that answers the task.
3. Check `docs/exec-plans/active/` before editing.
4. Leave behind updated validation or plan state when the work is non-trivial.

## Core Docs

- [Planning Workflow](./PLANS.md)
- [Quality Gates](./QUALITY_SCORE.md)
- [Reliability and Maintenance](./RELIABILITY.md)
- [Harness Skill](./skills/openai-harness-engineering/SKILL.md)
- [Harness Maintenance Runbook](./docs/runbooks/harness-maintenance.md)

## Core Directories

- `docs/exec-plans/active/`
- `docs/exec-plans/completed/`
- `docs/validation/`
- `docs/runbooks/`
- `docs/generated/`

## Repo Facts

- Profile: `minimal`
- Primary agent: `Codex`
- Deterministic checks live in `skills/openai-harness-engineering/scripts/` and `evals/`
- Drift control is required; use the maintenance runbook and drift check script
