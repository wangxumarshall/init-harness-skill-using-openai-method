# Quality Score

Quality in this repository means the skill can be changed repeatedly without losing thinness, deterministic behavior, or self-auditability.

## Minimum Bar

- `python3 -m py_compile skills/openai-harness-engineering/scripts/*.py evals/*.py`
- `python3 skills/openai-harness-engineering/scripts/audit_harness.py --target . --mode full`
- `python3 skills/openai-harness-engineering/scripts/check_harness_drift.py --target .`

## Review Questions

- Does the change keep the harness thin?
- Did deterministic checks stay actionable?
- Does the repo still dogfood its own expectations?
