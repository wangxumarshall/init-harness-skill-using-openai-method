# OpenAI Harness Engineering Skill

An agent-first skill for initializing, auditing, and operating durable software project harnesses. It is based on OpenAI's Harness Engineering idea: **Agent = Model + Harness**. The model matters, but the repository environment, instructions, tools, tests, runbooks, and feedback loops determine whether agents can keep solving problems over time.

This skill is designed for Codex, Cursor, Claude Code, Trae, Gemini, OpenCode, and similar coding agents.

## What It Builds

The skill turns a new or existing repository into a system of record for agents:

- A short `AGENTS.md` map that routes agents to focused docs.
- Architecture, design, frontend, backend, quality, reliability, security, and product-sense docs.
- Persistent execution plans under `docs/exec-plans/active/` and `docs/exec-plans/completed/`.
- Runbooks, validation logs, incident records, ADRs, and generated manifests.
- A deterministic initializer script that preserves existing files unless overwrite is explicitly requested.
- Helper scripts for harness audits and persistent execution-plan creation.

The goal is not just scaffolding. The goal is a project that a new agent can enter, understand, run, debug, validate, and continue after context compaction or a new session.

## Agent Trajectory

This skill treats agent trajectory as an organizing principle: a recoverable, auditable, reviewable path through real engineering work.

It does not rename the existing harness terms or add a separate transcript system. The durable path is:

```text
Request -> Context -> Plan -> Actions -> Decisions -> Validation -> Incidents -> Learnings -> Closure
```

- `exec-plans` are the trajectory index for non-trivial work.
- `validation logs` are the evidence layer.
- `incident records` are the failure branch.
- `ADRs` are the durable decision layer.
- `runbooks` are the learned operation layer.
- `generated manifests` are the harness self-description layer.

The boundary matters: record observable engineering facts, concise rationale, commands, results, links, and handoff state. Do not record full chain-of-thought, paste sensitive command output, invent precision, or create documentation debt by logging trivial work in excessive detail.

## References

- [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)
- [Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex)
- [Skills, shell tips, and compaction: lessons from real-world Codex use](https://developers.openai.com/blog/skills-shell-tips)
- [Testing agent skills systematically with evals](https://developers.openai.com/blog/eval-skills)
- [Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?](https://arxiv.org/html/2602.11988v1)
- [On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents](https://arxiv.org/html/2601.20404v2)

## Core Capabilities

### Initialize

Generate an OpenAI-style harness constitution for a target repo:

```bash
python3 skills/openai-harness-engineering/scripts/init_harness.py \
  --target /path/to/project \
  --project-name "Example App" \
  --project-description "A workflow app for internal operations" \
  --tech-stack "Next.js, TypeScript, Postgres" \
  --domains "Users, Workflows, Notifications" \
  --primary-agent "Codex"
```

Use `--dry-run` to inspect planned changes. Use `--force` only when you intend to overwrite existing generated files.

### Audit

Ask an agent to use `$openai-harness-engineering` to review an existing repo for harness quality. It will check whether a new agent can find architecture, product context, commands, active work, validation expectations, debugging paths, and persistent state.

You can also run the audit script directly:

```bash
python3 skills/openai-harness-engineering/scripts/audit_harness.py --target /path/to/project
```

### Operate

For non-trivial work, the skill routes agents through a durable loop:

1. Read the repo map and active plans.
2. Create or update an execution plan.
3. Make surgical changes.
4. Run validation.
5. Record decisions, results, blockers, and follow-ups.
6. Move completed work into `docs/exec-plans/completed/`.

This is the part that helps projects keep running instead of relying on one chat session.

Create an active plan directly:

```bash
python3 skills/openai-harness-engineering/scripts/new_plan.py \
  --target /path/to/project \
  --title "Fix checkout retry failures" \
  --request "Investigate and fix intermittent checkout retries" \
  --goal "Checkout retries are deterministic and covered by regression tests" \
  --agent "Codex"
```

### Evaluate

The skill includes guidance for testing itself on disposable projects, checking idempotency, preserving user-authored docs, and verifying that generated harnesses support long-running work.

## Installation

### Codex CLI

```bash
codex plugin marketplace add wangxumarshall/openai-harness-engineering
codex plugin install openai-harness-engineering
```

Invoke with:

```text
$openai-harness-engineering initialize this repo
```

### Claude Code

```bash
/plugin marketplace add wangxumarshall/openai-harness-engineering
/plugin install openai-harness-engineering@harness-engineering-skills
```

### Cursor

```bash
mkdir -p .cursor/rules
curl -o .cursor/rules/openai-harness-engineering.mdc \
  https://raw.githubusercontent.com/wangxumarshall/openai-harness-engineering/main/.cursor/rules/openai-harness-engineering.mdc
```

### Trae

```bash
mkdir -p .trae/rules
curl -o .trae/rules/openai-harness-engineering.md \
  https://raw.githubusercontent.com/wangxumarshall/openai-harness-engineering/main/.trae/rules/openai-harness-engineering.md
```

### Manual Skill Install

Copy `skills/openai-harness-engineering/` into your agent's skills directory, preserving `SKILL.md`, `scripts/`, `references/`, and `agents/`.

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
    ├── init_harness.py
    └── new_plan.py
```

## Design Notes

- `SKILL.md` stays concise and procedural.
- Detailed concepts live in `references/` and are loaded only when needed.
- Repeated deterministic work lives in `scripts/`.
- Generated `AGENTS.md` is deliberately short to avoid becoming a stale prompt dump.
- Mechanical enforcement is preferred over prose-only policy.

## License

MIT
