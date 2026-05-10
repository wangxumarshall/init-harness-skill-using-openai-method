# Skill Evaluation Guide

Use this reference when validating the skill itself.

## What To Test

- profile-based initialization
- preservation of existing user-authored docs
- structure and workflow audit behavior
- drift detection
- self-repo dogfood compliance
- deterministic eval grading

## Expected Behaviors

The skill should:

- keep `AGENTS.md` short
- avoid generating unnecessary surfaces
- preserve existing files by default
- fail workflow audits when placeholders remain unresolved
- require at least one deterministic verification path
- pass its own full audit in this repository

## Eval Loop

Run:

```bash
python3 evals/run_evals.py
python3 evals/grade_evals.py
```

Use `python3 evals/run_evals.py --engine codex` to store JSONL traces from `codex exec --json` when the binary is available.
