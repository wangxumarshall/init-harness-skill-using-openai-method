# Harness Skill Evals

Use these prompts against disposable repositories when changing `skills/openai-harness-engineering/`.

## Eval 1: Blank Project Initialization

Prompt:

```text
Use $openai-harness-engineering to initialize this blank repo.
Project name: OpsFlow
Description: Internal operations workflow system
Stack: Next.js, TypeScript, Postgres
Domains: Users, Workflows, Notifications
Primary agent: Codex
```

Expected:

- Creates root harness docs and `docs/` tree.
- `AGENTS.md` is short and links to root docs.
- `PLANS.md` defines active/completed plan workflow.
- `RELIABILITY.md` includes local runtime, health checks, observability, and incidents.
- `audit_harness.py --target .` exits with status 0.

## Eval 2: Existing Repo Preservation

Prompt:

```text
Use $openai-harness-engineering to add a harness to this existing repo. Preserve existing docs.
```

Expected:

- Inspects existing docs before writing.
- Uses `--dry-run` or explains planned writes when root harness docs exist.
- Does not overwrite existing user-authored files without explicit approval.
- Reports skipped files clearly.

## Eval 3: Long-Running Task Operation

Prompt:

```text
Use $openai-harness-engineering to set up a persistent plan for fixing intermittent payment retries.
```

Expected:

- Creates or updates `docs/exec-plans/active/<task>.md`.
- Includes goal, non-goals, context, decisions, validation, progress log, questions, and follow-ups.
- Does not implement unrelated product behavior.

## Eval 4: Harness Audit

Prompt:

```text
Use $openai-harness-engineering to audit whether this repo can support long-running Codex work.
```

Expected:

- Leads with concrete gaps.
- Checks `AGENTS.md`, root docs, active plans, validation, reliability, runbooks, and mechanical enforcement.
- Distinguishes script-detected issues from judgment-based recommendations.

## Eval 5: Concept Explanation

Prompt:

```text
Explain OpenAI Harness Engineering and how this repo should apply it.
```

Expected:

- Explains `Agent = Model + Harness`.
- Connects harness quality to repo-local knowledge, executable feedback, and persistent state.
- Gives repo-specific recommendations, not only generic theory.

## Eval 6: Agent Trajectory Continuity Without Renaming Existing Concepts

Prompt:

```text
Use $openai-harness-engineering to initialize a disposable repo, then create an active plan for debugging a flaky checkout workflow.
```

Expected:

- Keeps the existing terms and paths: `exec-plans`, `validation logs`, `incident records`, `ADRs`, `runbooks`, and `manifest`.
- Does not create `docs/trajectory/` or rename `PLANS.md`.
- `PLANS.md` explains that an exec-plan is the trajectory index.
- The generated active exec-plan lives under `docs/exec-plans/active/` and includes request, context, plan, actions, decisions, validation, incidents, learnings, closure, and next-agent handoff sections.
- `docs/validation/validation-log-template.md` includes a `Related exec-plan` field.
- `docs/incidents/incident-template.md` and `docs/runbooks/runbook-template.md` link back to related exec-plans.
- `docs/generated/harness-manifest.json` includes `trajectory_model: "exec-plan-indexed"`, `exec_plan_index_pattern`, `trajectory_related_dirs`, and `required_exec_plan_sections`.
- The records summarize observable engineering facts and evidence without requiring full chain-of-thought or sensitive command output.
