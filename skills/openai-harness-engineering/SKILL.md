---
name: openai-harness-engineering
description: Initialize, audit, or operate a thin OpenAI-style harness for a new or existing software project. Use when the user asks for Harness Engineering, agent-first scaffolding, AGENTS.md/project constitution, persistent execution plans, long-running agent workflows, repo knowledge systems, or making a project easier for coding agents to run, debug, and improve over time.
license: MIT
---

# OpenAI Harness Engineering

Use this skill to turn a repository into an agent-legible operating environment. The point is not to create a large constitution. The point is to give future agents enough context, deterministic commands, feedback loops, and persistent state to solve problems over many sessions.

Core model: **Agent = Model + Harness**.

- Model: interpretation, comparison, judgment, reporting.
- Scripts: repeated deterministic mechanics.
- Repo docs: durable state and discoverable constraints.

As models get stronger, the prose layer should shrink while the mechanical layer gets sharper.

## What This Skill Does

- Initializes a thin harness with profile-based scaffolding.
- Creates persistent execution-plan, validation, runbook, and manifest locations.
- Uses `exec-plans` as the trajectory index for recoverable long-running work.
- Audits both structure and live workflow quality.
- Can add an autonomy surface for unattended execution policy and readiness checks.
- Adds drift checks so the harness can shed stale or decorative structure.
- Includes eval guidance and scripts for regression-testing the skill.

## When To Read References

- For conceptual grounding, read `references/openai_harness_notes.md`.
- For generated files and profile behavior, read `references/generated_files.md`.
- For persistent operating workflows, read `references/operations.md`.
- For maintaining or evaluating the skill, read `references/evaluation.md`.

Load only the smallest reference that helps the current task.

## Workflow

### 1. Classify the User Request

- **Initialize**: add or refresh a harness in a repo
- **Audit**: review current harness quality and drift
- **Operate**: create or update durable plans for non-trivial work
- **Explain**: explain the harness model or how to apply it

For this repository's own maintenance, treat the task as **Audit + Dogfood + Evaluate Skill**.

### 2. Inspect the Target Repo First

Before writing files, check:

- existing `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, `.trae/rules/`, `.codex/`
- existing `docs/`, `README`, package files, CI, scripts, tests, and runbooks
- whether the repo clearly signals frontend or backend surfaces

Preserve existing content unless the user explicitly asks to overwrite.

### 3. Initialize With the Script

Prefer the bundled initializer:

```bash
python3 skills/openai-harness-engineering/scripts/init_harness.py \
  --target . \
  --project-name "{{PROJECT_NAME}}" \
  --project-description "{{PROJECT_DESC}}" \
  --tech-stack "{{TECH_STACK}}" \
  --domains "{{CORE_DOMAINS}}" \
  --primary-agent "{{CODING_AGENT}}" \
  --profile standard
```

Profiles:

- `minimal`: core map, plans, quality, reliability
- `standard`: thin core plus adaptive frontend/backend surfaces when the repo clearly needs them
- `full`: all scaffold surfaces

Useful flags:

- `--include-frontend`
- `--include-backend`
- `--include-ops`
- `--include-autonomy`
- `--emit-adapters auto|none|all`
- `--automation-provider codex|none`
- `--automation-runtime ci-worker|app-server|both`
- `--emit-automation-adapters auto|none|all`
- `--dry-run`
- `--force`

Existing files are preserved by default. Managed documents can append missing managed sections only when they already contain the harness marker.

### 4. Tailor the Harness

After generation:

- replace placeholders with real commands and health checks
- link existing specs, CI workflows, and local setup docs
- keep `AGENTS.md` short and routing-oriented
- prefer scripts or CI over prose-only requirements
- mark unresolved enforcement explicitly until it exists
- when unattended execution is required, wire autonomy commands, escalation policy, checkpoint storage, secret refs, and automation adapters before calling the repo ready

### 5. Operate the Harness

For non-trivial work, create or update `docs/exec-plans/active/<task>.md`.

The active exec-plan is the trajectory index:

```text
Request -> Context -> Plan -> Actions -> Decisions -> Validation -> Incidents -> Learnings -> Closure
```

Record observable engineering facts, concise rationale, commands, results, evidence, and handoff state. Do not record full chain-of-thought, secrets, or sensitive payloads.

You can create a plan with:

```bash
python3 skills/openai-harness-engineering/scripts/new_plan.py \
  --target . \
  --title "{{TASK_TITLE}}" \
  --request "{{USER_REQUEST}}" \
  --goal "{{VERIFIABLE_GOAL}}" \
  --agent "{{CODING_AGENT}}"
```

### 6. Audit the Harness

Use the audit script when possible:

```bash
python3 skills/openai-harness-engineering/scripts/audit_harness.py --target . --mode full
```

Check:

- is the profile surface correct for this repo
- can a new agent find plans, quality gates, and recovery paths quickly
- are links valid and commands executable
- are placeholders still unresolved
- is recurring cleanup reachable from the core map
- does the skill repo itself pass its own audit

If the repo should run unattended, also use:

```bash
python3 skills/openai-harness-engineering/scripts/check_autonomy_readiness.py --target .
```

Check:

- is the autonomy surface enabled
- are deploy, verify, rollback, monitor, unattended loop, and app-server bridge commands real and runnable for the selected runtime
- are approval policy, state store, and escalation path wired instead of left as placeholders
- does `docs/generated/autonomy-config.json` agree with the manifest automation section and declared secret refs

### 7. Run Drift Checks and Evals

For maintenance:

```bash
python3 skills/openai-harness-engineering/scripts/check_harness_drift.py --target .
python3 evals/run_evals.py
python3 evals/grade_evals.py
```

Move durable repeated mechanics into scripts and CI when they stabilize.

## Output Expectations

- For initialization: summarize created, updated, and skipped files, then list the unresolved setup debt.
- For audits: lead with concrete failures or drift, then list recommended fixes.
- For operations: report the exec-plan path and how validation and handoff were recorded.

## Critical Rules

- Do not invent product facts.
- Do not overwrite user-authored docs without explicit approval.
- Do not put detailed business rules in `AGENTS.md`.
- Prefer executable enforcement over prose-only policy.
- Keep the harness thin; do not generate surfaces the repo does not need.
- Record observable engineering facts, not full chain-of-thought.
- Do not copy secrets or sensitive payloads into plans, logs, incidents, or runbooks.
