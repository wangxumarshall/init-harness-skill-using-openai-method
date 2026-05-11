# Validation: Autonomy layer and readiness audit

- Date: 2026-05-11
- Agent: Codex
- Branch/worktree: current workspace
- Related exec-plan: `docs/exec-plans/active/add-autonomy-surface-and-readiness-audit.md`

## Commands

| Command | Result | Notes |
| --- | --- | --- |
| `python3 -m py_compile skills/openai-harness-engineering/scripts/*.py evals/*.py` | pass | Updated generator, audit, readiness script, and eval code compile |
| `python3 skills/openai-harness-engineering/scripts/audit_harness.py --target . --mode full` | pass | Self-harness still passes full audit after autonomy changes |
| `python3 skills/openai-harness-engineering/scripts/check_harness_drift.py --target .` | pass | No harness drift detected |
| `python3 evals/run_evals.py` | pass | Regenerated eval artifacts including autonomy surface and autonomy-ready scenarios |
| `python3 evals/grade_evals.py` | pass | Deterministic grading passed for all scenarios |
| `python3 skills/openai-harness-engineering/scripts/init_harness.py --target "$TMPDIR" --project-name Demo --project-description Demo --tech-stack Python --domains Harness --primary-agent Codex --profile standard --include-autonomy` | pass | Manual spot check confirmed `AUTONOMY.md` and autonomy runbooks are generated |
| `python3 skills/openai-harness-engineering/scripts/check_autonomy_readiness.py --target "$TMPDIR"` | pass | After wiring real commands into the fixture repo, unattended readiness passes |

## Manual Checks

- Confirmed `--include-autonomy` generates `AUTONOMY.md`, `docs/runbooks/autonomous-operations.md`, and `docs/validation/autonomy-drill-template.md`.
- Confirmed the manifest now carries autonomy metadata and autonomy-specific required commands.
- Confirmed an autonomy-enabled blank repo still fails unattended readiness until real commands and policy values are wired, which matches the intended contract.

## Artifacts

- Logs: none
- Screenshots: none
- Traces: `evals/artifacts/`

## Residual Risk

- The skill now scaffolds and audits unattended-operation readiness, but it still depends on the target repo to supply real schedulers, deployment adapters, secrets, and approval integrations.
