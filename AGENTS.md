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

## Engineering Rules

- Inspect the existing code path before adding abstractions.
- Match current architecture before inventing a new layer.
- Keep edits surgical; do not refactor unrelated code.
- Prefer the minimum code that solves the verified problem.
- Keep docs, scripts, and tests aligned when workflow or behavior changes.
- Add automated tests for new features.
- Use structured APIs or parsers when available.
- Code comments must be English.
- Never hand-edit generated code.
- Never add compatibility shims, dual-write logic, fallback paths, or legacy adapters unless explicitly asked.
- Prefer deleting obsolete paths over preserving both old and new behavior.
- Never introduce ad-hoc `console.*`; use existing logger modules.
- Never hardcode secrets, tokens, cookies, database credentials, or provider keys.
- Never modify, rotate, or commit production credentials from this repository.

## Evidence Rules

- Do not guess. Back claims with code, tests, logs, command output, or documented source files.
- If evidence is insufficient, say so and continue gathering evidence.
- If multiple interpretations exist, state them before choosing.
- Surface tradeoffs and push back when the simpler or safer path is clear.

## Verification

- Follow `QUALITY_SCORE.md` and `RELIABILITY.md` for required verification commands and release gates.
- Do not claim completion without recording the exact commands run and their results.

## Commits and PRs

- Keep commits atomic and grouped by logical intent.
- Use Conventional Commits such as `feat(web): ...`, `fix(server): ...`, `refactor(daemon): ...`, `test(e2e): ...`, `docs: ...`.
- Never commit code that still fails required lint, typecheck, or tests.
- PRs should include a short summary and exact verification commands; include screenshots for UI changes.

## Responses

- Reply in Chinese.
- Be concise.
- State result before cause when practical.
