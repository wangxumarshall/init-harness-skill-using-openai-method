# Add Codex automation adapters

- Status: active
- Owner/agent: Codex
- Started: 2026-05-11
- Last updated: 2026-05-11
- Trajectory role: exec-plan index

## User Request

Implement Codex-first unattended automation adapters, autonomy-config runtime contract, and readiness/eval coverage.

## Goal

Initializer emits runnable Codex CI/worker and app-server adapters, readiness validates them, and eval/audit/drift all pass.

## Non-Goals

- Build a real scheduler, queue backend, webhook ingress, or cloud deploy platform inside this repository.
- Ship provider-specific adapters for non-Codex providers in v1.

## Context

- `skills/openai-harness-engineering/scripts/init_harness.py` - generator entrypoint and template surface.
- `skills/openai-harness-engineering/scripts/check_autonomy_readiness.py` - unattended readiness contract.
- `skills/openai-harness-engineering/scripts/audit_harness.py` and `check_harness_drift.py` - self-audit and drift control.
- `evals/run_evals.py`, `evals/grade_evals.py`, `evals/prompts.csv` - deterministic regression harness.
- `README.md`, `skills/openai-harness-engineering/SKILL.md`, `skills/openai-harness-engineering/references/generated_files.md` - outward-facing capability docs.

## Context Read

- `docs/exec-plans/active/add-autonomy-surface-and-readiness-audit.md` - previous autonomy work and explicit follow-up toward provider-specific adapters.
- `README.md` - existing public initializer and readiness contract.
- `skills/openai-harness-engineering/scripts/init_harness.py` - current surfaces, manifest writer, and adapter templates.
- `skills/openai-harness-engineering/scripts/check_autonomy_readiness.py` - current readiness rules before automation support.
- `evals/run_evals.py` and `grade_evals.py` - existing fixture model and grading behavior.

## Plan

1. Extend initializer output and manifest shape for automation provider/runtime metadata plus autonomy config.
2. Generate runnable Codex CI/worker and app-server adapter fixtures and teach readiness checks to validate them.
3. Expand audit/drift/evals, then run full self-validation and record evidence.

## Actions Taken

- Added automation provider/runtime flags, autonomy config emission, manifest automation metadata, and Codex-first adapter templates. - `skills/openai-harness-engineering/scripts/init_harness.py`
- Upgraded autonomy readiness, audit, and drift checks to validate automation config, secret refs, runtime-specific adapter files, and manifest/config coherence. - `skills/openai-harness-engineering/scripts/check_autonomy_readiness.py`, `skills/openai-harness-engineering/scripts/audit_harness.py`, `skills/openai-harness-engineering/scripts/check_harness_drift.py`
- Expanded eval scenarios and fixture wiring for happy path, rollback, app-server resume, and missing-secret failure cases. - `evals/run_evals.py`, `evals/grade_evals.py`, `evals/prompts.csv`
- Synced public docs and self-harness manifest, then added validation evidence for this automation layer. - `README.md`, `skills/openai-harness-engineering/SKILL.md`, `skills/openai-harness-engineering/references/generated_files.md`, `docs/generated/harness-manifest.json`, `docs/validation/codex-automation-adapters-2026-05-11.md`

## Decisions

- Default automation provider remains Codex, with runtime defaulting to `both` while CI/worker remains the simpler main path. - Matches the implementation plan and keeps app-server support available without splitting configs.
- `docs/generated/autonomy-config.json` is the single runtime contract for queue worker and app-server bridge. - Avoids dual configuration surfaces.
- Readiness checks require secret refs to be present in the environment by name. - Distinguishes scaffold-only repos from actually wired unattended runtimes.
- GitHub Actions `${{ ... }}` expressions are not treated as harness placeholders. - Prevents false failures when validating workflow files.

## Decision Links

- ADR: none
- Design doc/spec: none

## Validation

- [x] `python3 -m py_compile skills/openai-harness-engineering/scripts/*.py evals/*.py` - updated Python surfaces compile
- [x] `python3 skills/openai-harness-engineering/scripts/audit_harness.py --target . --mode full` - self-harness full audit passes
- [x] `python3 skills/openai-harness-engineering/scripts/check_harness_drift.py --target .` - drift scan passes
- [x] `python3 evals/run_evals.py` - automation fixtures regenerate successfully
- [x] `python3 evals/grade_evals.py` - deterministic grading passes for all scenarios

## Validation Evidence

- Validation log: `docs/validation/codex-automation-adapters-2026-05-11.md`
- Summary: The skill now emits runnable Codex automation adapters plus a machine-readable runtime contract, and the self-harness validates those surfaces through audit, drift, and fixture-backed evals.

## Incident Links

- Incident: none

## Learnings

- Runtime adapters become much easier to verify once queue-worker, monitor, and app-server bridge all share the same autonomy config schema.
- Treating secret refs as environment names rather than prose placeholders gives a much sharper readiness boundary.

## Progress Log

- 2026-05-11: Plan created.

## Open Questions

- Whether to add provider-specific adapters beyond Codex in a second phase, or keep the cross-provider contract schema-only for now.

## Follow-Ups

- Add a provider-neutral queue contract doc or schema example if future providers need to plug into the same runtime surface.
- Consider a dedicated fixture for `repository_dispatch` payload handoff into the worker/app-server bridge.

## Closure Notes

- Outcome: implemented
- Changed files/modules: `skills/openai-harness-engineering/scripts/init_harness.py`, `skills/openai-harness-engineering/scripts/check_autonomy_readiness.py`, `skills/openai-harness-engineering/scripts/audit_harness.py`, `skills/openai-harness-engineering/scripts/check_harness_drift.py`, `evals/run_evals.py`, `evals/grade_evals.py`, `evals/prompts.csv`, `README.md`, `skills/openai-harness-engineering/SKILL.md`, `skills/openai-harness-engineering/references/generated_files.md`, `docs/generated/harness-manifest.json`, `docs/validation/codex-automation-adapters-2026-05-11.md`
- Residual risk: generated adapters are runnable fixtures and integration contracts, not a full production scheduler/secret/deploy platform.

## Next Agent Handoff

- Current state: Codex-first automation adapters, readiness checks, and eval coverage are in place and passing.
- Next recommended action: dogfood the generated adapter set in a target repo with real secrets, deploy commands, and scheduler wiring.
- Blockers: none
