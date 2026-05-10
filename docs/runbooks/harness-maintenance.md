# Harness Maintenance Runbook

- Owner/agent: Codex
- Last verified: 2026-05-10
- Related exec-plan: `docs/exec-plans/completed/thin-harness-redesign.md`
- Related incident: none

## Purpose

Run the deterministic checks that keep this skill thin, executable, and current with upstream harness guidance.

## Prerequisites

- run commands from the repository root
- Python 3 available on the path

## Procedure

1. Compile scripts: `python3 -m py_compile skills/openai-harness-engineering/scripts/*.py evals/*.py`
2. Audit the self-harness: `python3 skills/openai-harness-engineering/scripts/audit_harness.py --target . --mode full`
3. Scan for drift: `python3 skills/openai-harness-engineering/scripts/check_harness_drift.py --target .`
4. Run and grade evals: `python3 evals/run_evals.py && python3 evals/grade_evals.py`

## Validation

- `python3 skills/openai-harness-engineering/scripts/audit_harness.py --target . --mode full` - exits 0

## Rollback or Recovery

- if audit fails, fix manifest/profile mismatches or stale placeholders before rerunning

## Common Failures

- missing self-harness files: re-check `AGENTS.md`, `PLANS.md`, `QUALITY_SCORE.md`, `RELIABILITY.md`
- drift issues: update stale links, plans, or manifest surface declarations

## Learnings

- upstream reference changes should be reflected in README and `references/` together
