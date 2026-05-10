# OpenAI Harness Engineering Notes

Use this reference when the user asks for a deeper explanation of the harness model.

## Core Ideas

- Harness engineering treats agent performance as `model + harness`.
- As models improve, the durable harness gets thinner in prose and stronger in mechanics.
- The repository is the system of record for plans, validation, decisions, and operational recovery knowledge.
- Short maps, progressive disclosure, deterministic scripts, CI carry-over, and recurring cleanup are the enduring patterns.

## Anti-Patterns

- giant `AGENTS.md` files that duplicate everything
- prose requirements with no executable verification path
- one-shot scaffolding with no drift detection
- relying on chat memory instead of repo state
- generating frontend or backend surfaces the repo does not actually need
