# OpenAI Harness Engineering Notes

Use this reference when the user asks what OpenAI Harness Engineering means, asks for a deeper analysis, or needs the generated harness tailored to a team process.

## Source Concepts

- Harness engineering treats the agent's performance as `model + harness`. The repository, tools, instructions, tests, linters, and runtime feedback loops are part of the product.
- The human role shifts from hand-writing implementation to designing agent environments, specifying intent, curating context, and creating fast feedback loops.
- The repo should become the system of record. Architectural decisions, product decisions, runbooks, and local workflow knowledge should be committed where agents can read them.
- Useful harnesses are legible to agents: small entry points, explicit maps, deterministic commands, reproducible environments, and errors that explain how to remediate themselves.
- Long-running agent work needs continuity: plans, task logs, validation results, decisions, and follow-up work must be written back into the repo so future sessions can resume.

## Capability Targets

A mature harness should support these capabilities:

1. **Orientation**: An agent can enter the repo cold and find architecture, product context, commands, boundaries, and active work within minutes.
2. **Execution**: An agent can turn a request into a plan, edit code, run local validation, and update status without hidden human context.
3. **Verification**: The repo has tests, linters, structural checks, and smoke commands that produce actionable output.
4. **Runtime Debugging**: Bugs can be reproduced locally or in ephemeral workspaces with logs, metrics, browser/devtools traces, and seeded data.
5. **Persistence**: Work survives context compaction, session restarts, and agent handoffs through repo-local plans, decisions, logs, and completed records.
6. **Maintenance**: Agents regularly identify stale docs, flaky checks, duplicate utilities, and broken onboarding paths, then repair them in small follow-up changes.
7. **Evaluation**: The team can test whether the harness and skills work by running realistic prompts against disposable repos and checking the created artifacts.

## Design Implications

- Prefer file maps and concise entry points over giant prompts.
- Move detailed policy into focused docs that can be loaded only when relevant.
- Convert important prose constraints into executable checks where possible.
- Put remediation instructions in failing checks so agents can fix issues autonomously.
- Capture decisions as ADRs, plans as files, and validation as command output summaries.
- Keep generated scaffolding conservative. The harness should not invent product facts.

## Anti-Patterns

- A massive `AGENTS.md` that mixes every rule, product detail, and runbook.
- Docs that say "must" without any command, test, lint rule, owner, or verification path.
- Knowledge living only in chat, issues, Slack, design tools, or a developer's memory.
- One-shot scaffolding with no update path, no drift detection, and no validation.
- Agent instructions that encourage broad refactors during unrelated tasks.
- Runtime systems that cannot be started locally or observed through logs and health checks.
