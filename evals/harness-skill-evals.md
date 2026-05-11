# Harness Skill Evals

The executable eval entrypoints are:

```bash
python3 evals/run_evals.py
python3 evals/grade_evals.py
```

Scenarios live in `evals/prompts.csv` and cover:

- explicit invocation
- implicit invocation
- negative control
- blank repo init
- existing repo preservation
- minimal profile init
- standard profile init
- autonomy surface init
- autonomy readiness fixture
- audit-only workflow
- operate/create-plan workflow
- self-repo dogfood audit
