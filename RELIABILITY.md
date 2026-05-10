# Reliability and Maintenance

Agents should be able to run, verify, and maintain this skill from the repository root without hidden context.

## Deterministic Commands

- Install: `python3 -m py_compile skills/openai-harness-engineering/scripts/*.py evals/*.py`
- Full validation: `python3 skills/openai-harness-engineering/scripts/audit_harness.py --target . --mode full`
- Drift scan: `python3 skills/openai-harness-engineering/scripts/check_harness_drift.py --target .`
- Eval loop: `python3 evals/run_evals.py && python3 evals/grade_evals.py`

## Harness Maintenance Loop

- run the drift scan
- clear placeholders before calling the repo ready
- review stale active plans
- update references when upstream OpenAI guidance changes
