# Skill Evaluation Guide

Use this reference when maintaining this skill or when the user asks how to verify that the harness works.

## What To Evaluate

Test the skill on disposable repositories, not only by reading the generated files.

Good evaluation prompts cover:

- A new blank project with only a product idea.
- An existing repo with a README and package files.
- A user who provides incomplete details.
- A user who asks for long-running agent operations, not just scaffolding.
- A repo that already has `AGENTS.md` and some docs.
- A project with frontend, backend, database, CI, and deployment concerns.

## Expected Behaviors

The skill should:

- Ask for missing project facts unless the user asks to use placeholders.
- Create the docs tree and core files idempotently.
- Preserve existing user-authored content.
- Keep `AGENTS.md` short.
- Include persistent work planning and validation loops.
- Include mechanical enforcement language and remediation-oriented checks.
- Avoid inventing product facts.
- Explain what changed and what the user should do next.

## Suggested Eval Checks

After running the skill, inspect:

- `AGENTS.md` has links to root docs and active plan locations.
- `PLANS.md` defines active/completed plan movement.
- `RELIABILITY.md` includes local runtime, logs, health checks, and incidents.
- `QUALITY_SCORE.md` includes tests, linters, structural checks, and CI.
- Existing files were not overwritten without permission.
- The final user response lists created/updated files and validation status.

## Maintenance Checklist

- Keep `SKILL.md` under roughly 500 lines.
- Put detailed background in `references/`.
- Put deterministic generation logic in `scripts/`.
- Update adapter rules when the invocation behavior changes.
- Run `python3 -m py_compile` on scripts after edits.
- Run a dry-run initializer command in a temporary directory before release.
