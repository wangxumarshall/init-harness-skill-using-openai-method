# Thin Harness Redesign

- Status: completed
- Owner/agent: Codex
- Started: 2026-05-10
- Last updated: 2026-05-10
- Trajectory role: exec-plan index

## User Request

Revise the skill so it behaves like a thinner, more durable harness and implement the plan.

## Goal

The skill ships profile-based initialization, structure plus workflow audits, drift checks, a self-harness, and executable eval support.

## Non-Goals

- add background automations
- turn this repository into a full-profile harness consumer

## Context

- README and skill docs framed the harness too much as static scaffolding
- scripts did not support profile-based output or workflow validation
- the repository did not dogfood its own harness expectations

## Context Read

- `README.md` - product promise and user-facing workflow
- `skills/openai-harness-engineering/SKILL.md` - skill invocation contract
- `skills/openai-harness-engineering/scripts/*.py` - deterministic behavior

## Plan

1. Reframe the docs around a thin harness model.
2. Upgrade initializer and audit scripts.
3. Add drift checks, eval runner, and self-harness docs.
4. Validate the repository against its own audit.

## Actions Taken

- Rewrote the initializer around profiles, adaptive surfaces, and managed sections.
- Rebuilt the audit around structure and workflow layers.
- Added a read-only drift checker and eval runner/grader.
- Added a minimal self-harness to the repo.

## Decisions

- Keep the self-harness on the `minimal` profile.
- Require at least one deterministic command in the manifest.
- Treat unresolved placeholders as workflow failures, not structure failures.

## Decision Links

- ADR: none
- Design doc/spec: README and SKILL refresh

## Validation

- [x] `python3 -m py_compile skills/openai-harness-engineering/scripts/*.py evals/*.py` - scripts compile
- [x] `python3 skills/openai-harness-engineering/scripts/audit_harness.py --target . --mode full` - self-harness passes

## Validation Evidence

- Validation log: `docs/validation/self-audit.md`
- Summary: core script and self-audit checks passed after the redesign

## Incident Links

- Incident: none

## Learnings

- thin harnesses still need strong machine-readable metadata and recurring cleanup

## Progress Log

- 2026-05-10: plan captured and closed with self-harness support

## Open Questions

- none

## Follow-Ups

- add richer codex-exec trace grading when the CLI contract is stable

## Closure Notes

- Outcome: implemented thin harness redesign
- Changed files/modules: README, skill docs, scripts, evals, self-harness docs
- Residual risk: codex JSONL trace capture depends on local `codex` availability

## Next Agent Handoff

- Current state: self-harness and deterministic eval scaffolding are in place
- Next recommended action: expand grader depth when eval trace schema stabilizes
- Blockers: none
