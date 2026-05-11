# OpenAI Harness Engineering Skill

An agent-first skill for initializing, auditing, and operating thin, durable software project harnesses.

It is grounded in OpenAI's harness idea: **Agent = Model + Harness**. As models improve, the harness should get thinner in prose and stronger in mechanics. The durable value is not a giant prompt dump. It is a repo that a new agent can enter, validate, repair, and continue.

This skill is designed for Codex, Cursor, Claude Code, Trae, Gemini, OpenCode, and similar coding agents.

## What It Builds

The skill turns a repository into a system of record for agents:

- A short `AGENTS.md` map that routes agents to the smallest relevant docs.
- A lightweight adapter layer for agent-specific entrypoints such as `CLAUDE.md`.
- A `DELIVERY.md` lifecycle that keeps spec -> implement -> test -> verify -> deploy visible.
- An optional `AUTONOMY.md` surface for unattended-operation policy, escalation, and checkpoint expectations.
- Persistent execution plans under `docs/exec-plans/active/` and `docs/exec-plans/completed/`.
- Runbooks, validation logs, and machine-readable harness metadata.
- Deterministic scripts for initialization, harness auditing, plan creation, and drift checks.
- An eval loop for regression-testing the skill itself.

The goal is a project that survives context compaction, handoffs, and repeated changes without depending on one chat session.
For standard and full profiles, it also keeps deployment and rollback expectations in the repo instead of in chat memory.

## Thin Harness Model

The stable split is:

- **Model**: interpretation, comparison, judgment, reporting.
- **Scripts**: repeated deterministic mechanics.
- **Repo docs**: durable state, discoverable constraints, and handoff context.

Useful harnesses stay thin:

- `AGENTS.md` is a short map, not a manual.
- Detailed guidance lives in focused docs and is loaded only when needed.
- Repeated mechanics migrate into scripts and CI.
- Drift checks and recurring cleanup keep the harness from accreting decorative prose.

### What Gets Thinner Over Time

- Thick prompt manuals shrink.
- Duplicated prose shrinks.
- One-shot scaffolding shrinks.
- Executable checks, traces, plans, and recurring cleanup remain.

## Core Capabilities

### Initialize

Generate an adaptive harness for a target repo:

```bash
python3 skills/openai-harness-engineering/scripts/init_harness.py \
  --target /path/to/project \
  --project-name "Example App" \
  --project-description "A workflow app for internal operations" \
  --tech-stack "Next.js, TypeScript, Postgres" \
  --domains "Users, Workflows, Notifications" \
  --primary-agent "Codex" \
  --profile standard
```

Profiles:

- `minimal`: just the thin core map, plans, quality, reliability, and supporting directories.
- `standard`: core docs plus adaptive frontend/backend surfaces when the repo clearly signals them.
- `full`: emit the whole scaffold surface.

Useful flags:

- `--include-frontend`
- `--include-backend`
- `--include-ops`
- `--include-autonomy`
- `--emit-adapters auto|none|all`
- `--dry-run`
- `--force`

The initializer preserves existing files by default. If a managed document already exists and contains the harness marker, missing managed sections can be appended without overwriting user-authored content.

### Audit

Audit a repo for harness quality:

```bash
python3 skills/openai-harness-engineering/scripts/audit_harness.py \
  --target /path/to/project \
  --mode full
```

Audit layers:

- `structure`: required files, directories, links, manifest/profile consistency
- `workflow`: unresolved placeholders, command executability, plan shape, recurring cleanup reachability
- `full`: both

Machine-readable output:

```bash
python3 skills/openai-harness-engineering/scripts/audit_harness.py \
  --target /path/to/project \
  --mode full \
  --json
```

Exit codes:

- `0`: pass
- `1`: structure failures
- `2`: workflow failures
- `3`: both

### Autonomy Readiness

When a target repo should support unattended operation, scaffold the autonomy surface:

```bash
python3 skills/openai-harness-engineering/scripts/init_harness.py \
  --target /path/to/project \
  --project-name "Example App" \
  --project-description "A workflow app for internal operations" \
  --tech-stack "Next.js, TypeScript, Postgres" \
  --domains "Users, Workflows, Notifications" \
  --primary-agent "Codex" \
  --profile standard \
  --include-autonomy
```

This adds:

- `AUTONOMY.md`
- `docs/runbooks/autonomous-operations.md`
- `docs/validation/autonomy-drill-template.md`
- autonomy-specific manifest fields and required commands

Assess whether a repo is actually wired for unattended execution:

```bash
python3 skills/openai-harness-engineering/scripts/check_autonomy_readiness.py --target /path/to/project
```

This stricter check expects real, runnable commands for validation, deploy, post-deploy verify, rollback, monitoring, and the unattended loop itself.

### Operate

For non-trivial work, use exec-plans as the trajectory index:

```text
Request -> Context -> Plan -> Actions -> Decisions -> Validation -> Incidents -> Learnings -> Closure
```

Create an active plan directly:

```bash
python3 skills/openai-harness-engineering/scripts/new_plan.py \
  --target /path/to/project \
  --title "Fix checkout retry failures" \
  --request "Investigate and fix intermittent checkout retries" \
  --goal "Checkout retries are deterministic and covered by regression tests" \
  --agent "Codex"
```

### Drift Control

Run a read-only drift scan:

```bash
python3 skills/openai-harness-engineering/scripts/check_harness_drift.py --target /path/to/project
```

It reports:

- broken local links
- stale unresolved placeholders
- stale active plans
- manifest/docs mismatches

### Evaluate

Run the skill's deterministic eval harness:

```bash
python3 evals/run_evals.py
python3 evals/grade_evals.py
```

When `codex` is available, `evals/run_evals.py --engine codex` also stores JSONL traces from `codex exec --json`.

## Harness Maintenance Loop

Thin harnesses stay valuable by shedding stale structure:

1. Run a doc drift scan.
2. Clear unresolved placeholders before calling the harness ready.
3. Review stale active plans and either update or close them.
4. Move repeated manual review comments into scripts, tests, or CI.

## References

- [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)
- [Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex)
- [Skills, shell tips, and compaction: lessons from real-world Codex use](https://developers.openai.com/blog/skills-agents-sdk)
- [Testing agent skills systematically with evals](https://developers.openai.com/blog/eval-skills)
- [Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?](https://arxiv.org/abs/2602.11988)
- [On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents](https://arxiv.org/abs/2601.20404)

## Project Structure

```text
skills/openai-harness-engineering/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── evaluation.md
│   ├── generated_files.md
│   ├── openai_harness_notes.md
│   └── operations.md
└── scripts/
    ├── audit_harness.py
    ├── check_autonomy_readiness.py
    ├── check_harness_drift.py
    ├── init_harness.py
    └── new_plan.py
evals/
├── prompts.csv
├── run_evals.py
├── grade_evals.py
└── artifacts/
```

## License

MIT
