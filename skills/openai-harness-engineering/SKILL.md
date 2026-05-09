---
name: openai-harness-engineering
description: Initialize, audit, or operate an OpenAI-style agent harness for a new or existing software project. Use when the user asks for Harness Engineering, agent-first scaffolding, AGENTS.md/project constitution, persistent execution plans, long-running agent workflows, repo knowledge systems, or making a project easier for Codex/Cursor/Claude/Trae/Gemini/OpenCode agents to run, debug, and improve over time.
license: MIT
---

# OpenAI Harness Engineering

Use this skill to turn a project repository into an agent-legible operating environment. The goal is not only to create docs; it is to give future agents enough context, commands, feedback loops, and persistent state to solve problems over many sessions.

Core model: **Agent = Model + Harness**. Humans steer; agents execute. The repository is the system of record.

## What This Skill Does

- Initializes a concise agent constitution and docs tree.
- Creates persistent execution-plan, validation, incident, runbook, and ADR locations.
- Uses `exec-plans` as the trajectory index for recoverable agent work without renaming existing harness concepts.
- Guides long-running work so state survives context compaction, restarts, and handoffs.
- Emphasizes mechanical enforcement: tests, linters, structural checks, CI, and remediation-oriented errors.
- Audits existing harness docs for gaps and drift.

## When To Read References

- For conceptual grounding and deeper analysis, read `references/openai_harness_notes.md`.
- For the generated file list and ownership rules, read `references/generated_files.md`.
- For persistent operating workflows, read `references/operations.md`.
- For maintaining or evaluating this skill, read `references/evaluation.md`.

Do not load every reference by default; choose the smallest one that helps the current task.

## Workflow

### 1. Classify the User Request

- **Initialize**: user wants to add harness scaffolding to a project.
- **Audit**: user wants a review of current agent docs, plans, or skill quality.
- **Operate**: user wants help running a long-lived agent workflow, debugging, or maintaining project state.
- **Explain**: user wants to understand OpenAI Harness Engineering.

For this repository's own maintenance, treat the task as **Audit + Improve Skill**.

### 2. Gather Only Missing Facts

For initialization, collect these facts if not already known:

- Project name.
- Project description.
- Core tech stack.
- Core business domains.
- Primary coding agent, such as Codex, Cursor, Claude Code, Trae, Gemini, or OpenCode.

If the user says to proceed with placeholders, do that. If the repo already reveals enough, infer conservatively and mention assumptions.

### 3. Inspect The Target Repo First

Before writing files, check:

- Existing `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, `.trae/rules/`, `.codex/`, or similar agent docs.
- Existing `docs/`, `README`, package files, CI, scripts, tests, and runbooks.
- Whether user-authored docs already contain product or architecture facts.

Preserve existing content unless the user explicitly asks to overwrite.

### 4. Initialize With The Script

Prefer the bundled script for deterministic scaffolding:

```bash
python3 skills/openai-harness-engineering/scripts/init_harness.py \
  --target . \
  --project-name "{{PROJECT_NAME}}" \
  --project-description "{{PROJECT_DESC}}" \
  --tech-stack "{{TECH_STACK}}" \
  --domains "{{CORE_DOMAINS}}" \
  --primary-agent "{{CODING_AGENT}}"
```

If running from an installed skill path, resolve the script relative to this `SKILL.md`. Use `--dry-run` before writing when the target repo already has harness files. Use `--force` only after explicit user approval.

The script creates:

- Root docs: `AGENTS.md`, `ARCHITECTURE.md`, `DESIGN.md`, `FRONTEND.md`, `BACKEND.md`, `PLANS.md`, `PRODUCT_SENSE.md`, `QUALITY_SCORE.md`, `RELIABILITY.md`, `SECURITY.md`.
- Docs tree: `docs/adr/`, `docs/design-docs/`, `docs/exec-plans/active/`, `docs/exec-plans/completed/`, `docs/generated/`, `docs/incidents/`, `docs/product-specs/`, `docs/references/`, `docs/runbooks/`, `docs/validation/`.
- Seed files for core beliefs, local development, debugging, validation logs, incident/runbook templates, and the initial ADR.

Run a quick harness audit after initialization:

```bash
python3 skills/openai-harness-engineering/scripts/audit_harness.py --target .
```

### 5. Tailor The Harness

After generation, adapt placeholders using discovered repo facts:

- Fill package manager, dev, build, lint, typecheck, test, smoke, migration, and seed commands.
- Link existing specs, architecture docs, issue templates, CI workflows, and local setup docs.
- Add domain names and module boundaries from the actual project.
- Add known local runtime details, ports, services, logs, and health checks.
- Keep `AGENTS.md` small. Move detail into focused docs.

Every "must" should have a verification path, or be marked as pending enforcement.

### 6. Operate The Harness

For non-trivial project work, create or update `docs/exec-plans/active/<task>.md` with:

- User request and interpreted goal.
- Non-goals.
- Relevant context and context actually read.
- Plan and status.
- Actions taken.
- Decisions and links to ADRs, specs, or design docs.
- Validation commands, results, and validation-log links.
- Incident links when failures affect users, data, availability, or trust.
- Learnings, closure notes, and next-agent handoff state.
- Open questions and follow-ups.

Treat the exec-plan as the trajectory index for the task: `Request -> Context -> Plan -> Actions -> Decisions -> Validation -> Incidents -> Learnings -> Closure`. It is not a transcript. Record externally visible engineering facts, concise rationale, commands, results, artifacts, links, and handoff state. Do not record full chain-of-thought, secrets, sensitive payloads, or raw command output that contains private data.

You can create a plan with:

```bash
python3 skills/openai-harness-engineering/scripts/new_plan.py \
  --target . \
  --title "{{TASK_TITLE}}" \
  --request "{{USER_REQUEST}}" \
  --goal "{{VERIFIABLE_GOAL}}" \
  --agent "{{CODING_AGENT}}"
```

When complete, move it to `docs/exec-plans/completed/`. For user-impacting failures, create an incident record. For repeated debugging knowledge, update a runbook.

### 7. Audit The Harness

When asked to analyze or improve a harness, check:

- Is `AGENTS.md` a short map rather than a giant prompt?
- Can a new agent find architecture, product intent, commands, active work, and validation rules quickly?
- Are docs backed by tests, linters, structural checks, CI, scripts, or runbooks?
- Are command failures actionable enough for an agent to fix?
- Is long-running work persisted in active/completed plans?
- Are runtime debugging, observability, and incident loops documented?
- Does the skill itself use progressive disclosure, scripts, references, and eval guidance?

Use the audit script when possible, then apply engineering judgment to anything it cannot check:

```bash
python3 skills/openai-harness-engineering/scripts/audit_harness.py --target .
```

## Output Expectations

For initialization, summarize created, updated, and skipped files, then list immediate next steps such as filling command placeholders or running a setup smoke test.

For audits, lead with concrete gaps and recommended fixes. Include file paths. If you make changes, report what changed and how you verified it.

## Critical Rules

- Do not invent product facts.
- Do not overwrite existing harness docs without explicit approval.
- Do not put detailed business rules in `AGENTS.md`.
- Prefer executable enforcement over prose-only policy.
- Record externally visible engineering facts, not full chain-of-thought.
- Do not copy secrets, sensitive payloads, or private command output into plans, validation logs, incidents, or runbooks.
- Keep changes surgical and repo-specific.
- The generated harness content should be in English unless the user explicitly requests another language for project docs.
