#!/usr/bin/env python3
"""Initialize or refresh an OpenAI-style agent harness in a repository."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT_FILES = [
    "AGENTS.md",
    "ARCHITECTURE.md",
    "DESIGN.md",
    "FRONTEND.md",
    "BACKEND.md",
    "PLANS.md",
    "PRODUCT_SENSE.md",
    "QUALITY_SCORE.md",
    "RELIABILITY.md",
    "SECURITY.md",
]

DOC_DIRS = [
    "docs/adr",
    "docs/design-docs",
    "docs/exec-plans/active",
    "docs/exec-plans/completed",
    "docs/generated",
    "docs/incidents",
    "docs/product-specs",
    "docs/references",
    "docs/runbooks",
    "docs/validation",
]


@dataclass(frozen=True)
class HarnessContext:
    project_name: str
    project_description: str
    tech_stack: str
    domains: str
    primary_agent: str
    generated_on: str

    @property
    def domain_list(self) -> list[str]:
        parts = re.split(r"[,;/\n]+", self.domains)
        cleaned = [part.strip() for part in parts if part.strip()]
        return cleaned or ["{{CORE_DOMAIN}}"]

    @property
    def domain_bullets(self) -> str:
        return "\n".join(f"- {domain}" for domain in self.domain_list)

    @property
    def slug(self) -> str:
        value = re.sub(r"[^a-zA-Z0-9]+", "-", self.project_name.lower()).strip("-")
        return value or "project"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an agent-first harness constitution and operating docs."
    )
    parser.add_argument("--target", default=".", help="Repository root to initialize.")
    parser.add_argument("--project-name", default="{{PROJECT_NAME}}")
    parser.add_argument("--project-description", default="{{PROJECT_DESC}}")
    parser.add_argument("--tech-stack", default="{{TECH_STACK}}")
    parser.add_argument("--domains", default="{{CORE_DOMAINS}}")
    parser.add_argument("--primary-agent", default="{{CODING_AGENT}}")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated files. Use only with explicit user approval.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned changes without writing files.",
    )
    return parser.parse_args()


def h1(title: str) -> str:
    return f"# {title}\n\n"


def templates(ctx: HarnessContext) -> dict[str, str]:
    return {
        "AGENTS.md": agents_md(ctx),
        "ARCHITECTURE.md": architecture_md(ctx),
        "DESIGN.md": design_md(ctx),
        "FRONTEND.md": frontend_md(ctx),
        "BACKEND.md": backend_md(ctx),
        "PLANS.md": plans_md(ctx),
        "PRODUCT_SENSE.md": product_sense_md(ctx),
        "QUALITY_SCORE.md": quality_score_md(ctx),
        "RELIABILITY.md": reliability_md(ctx),
        "SECURITY.md": security_md(ctx),
        "docs/design-docs/core-beliefs.md": core_beliefs_md(ctx),
        "docs/runbooks/local-development.md": local_development_md(ctx),
        "docs/runbooks/debugging.md": debugging_md(ctx),
        "docs/validation/validation-log-template.md": validation_log_template_md(ctx),
        "docs/adr/0001-agent-harness-constitution.md": adr_md(ctx),
    }


def agents_md(ctx: HarnessContext) -> str:
    return (
        h1(f"{ctx.project_name} Agent Map")
        + f"""This repository is designed for agent-first development. This file is a map, not a policy dump.

## Start Here

1. Read the current user request.
2. Read the smallest relevant docs below.
3. Check `docs/exec-plans/active/` for in-progress work before editing.
4. Update plans, validation notes, and decisions as work progresses.

## System of Record

- [Architecture & Boundaries](./ARCHITECTURE.md)
- [Design Principles](./DESIGN.md)
- [Product Sense](./PRODUCT_SENSE.md)
- [Quality Score](./QUALITY_SCORE.md)
- [Reliability & Operations](./RELIABILITY.md)
- [Security Baseline](./SECURITY.md)
- [Planning Workflow](./PLANS.md)

## Core Directories

- `docs/design-docs/`: durable design context and beliefs.
- `docs/product-specs/`: requirements, specs, and accepted product behavior.
- `docs/exec-plans/active/`: active agent plans and resumable task state.
- `docs/exec-plans/completed/`: finished plans with outcomes and validation.
- `docs/runbooks/`: operational recipes agents can execute.
- `docs/validation/`: validation logs, smoke notes, and test evidence.
- `docs/incidents/`: user-impacting failure records and follow-up actions.
- `docs/adr/`: architecture decision records.

## Project Facts

- Project: {ctx.project_name}
- Description: {ctx.project_description}
- Tech stack: {ctx.tech_stack}
- Primary agent: {ctx.primary_agent}
- Core domains:
{ctx.domain_bullets}
"""
    )


def architecture_md(ctx: HarnessContext) -> str:
    return (
        h1("Architecture and Boundary Constraints")
        + f"""## Goal

Make `{ctx.project_name}` legible enough that a new agent can safely change it without private human context.

## Strict Layered Domain Architecture

Every business domain should follow a unidirectional dependency flow:

```text
Types -> Config -> Repo -> Service -> Runtime -> UI
```

- `Types`: shared schemas, type definitions, and validated shapes.
- `Config`: feature flags, environment configuration, and dependency wiring.
- `Repo`: persistence and external API access.
- `Service`: business rules and use cases.
- `Runtime`: jobs, handlers, routes, commands, workers, and orchestration.
- `UI`: presentation and interaction logic.

Cross-cutting concerns such as auth, telemetry, feature flags, and payments must enter through explicit provider interfaces. Hidden globals and ad hoc imports are boundary violations.

## Domain Map

Core domains:

{ctx.domain_bullets}

For each domain, document:

- Public types and validation schemas.
- Allowed dependencies.
- Storage ownership.
- External systems.
- Runtime entry points.
- UI surfaces, if any.

## Boundary Rules

- Parse and validate data at system boundaries.
- Keep business rules out of UI, route handlers, database adapters, and test fixtures.
- Prefer shared utilities over repeated one-off helpers.
- Add a boundary test or lint rule when a violation repeats.
- Do not refactor unrelated layers while solving a local task.

## Mechanical Enforcement

Architectural rules should become executable checks. Preferred enforcement order:

1. Existing compiler or type checker.
2. Existing linter and formatter.
3. Unit or integration tests.
4. Structural tests for forbidden imports, dependency direction, file placement, or naming.
5. CI workflows that run the checks in a clean environment.

Custom checks must print remediation instructions. A useful failure tells `{ctx.primary_agent}`:

- What rule failed.
- Which file or dependency caused it.
- The intended architecture.
- The safest next edit.

## Decision Records

Record durable architectural decisions in `docs/adr/`. Include context, decision, consequences, and validation expectations.
"""
    )


def design_md(ctx: HarnessContext) -> str:
    return (
        h1("Design Principles")
        + f"""## Operating Principle

Humans steer. Agents execute. The repo must contain enough context, commands, and feedback for `{ctx.primary_agent}` to solve problems without guessing.

## Agent Coding Rules

1. **Think Before Coding**: Do not assume hidden requirements. Surface tradeoffs. State assumptions explicitly. If a decision is risky and cannot be discovered from repo context, ask.
2. **Simplicity First**: Write the minimum code that solves the verified problem. Avoid speculative abstractions, unused features, and framework churn.
3. **Surgical Changes**: Touch only what the task requires. Clean up your own changes. Do not improve adjacent code as a side mission.
4. **Goal-Driven Execution**: Convert every task into success criteria, run checks, and keep looping until the criteria are met or a blocker is recorded.

## Harness Design Rules

- Prefer explicit files, commands, and tests over conversational memory.
- Make important instructions discoverable from `AGENTS.md`.
- Keep root docs concise and route details to focused files.
- Update docs when behavior, architecture, or operations change.
- Convert repeated manual fixes into scripts, tests, linters, or runbooks.

## Tech Stack Notes

Primary stack: `{ctx.tech_stack}`

Document stack-specific conventions here:

- Package manager and install command: `{{INSTALL_COMMAND}}`
- Development server command: `{{DEV_COMMAND}}`
- Test command: `{{TEST_COMMAND}}`
- Lint command: `{{LINT_COMMAND}}`
- Typecheck command: `{{TYPECHECK_COMMAND}}`
- Build command: `{{BUILD_COMMAND}}`

## Change Discipline

- Preserve existing style unless the task is explicitly a style or refactor task.
- Prefer local helpers and existing patterns before adding dependencies.
- Add dependencies only when they remove meaningful complexity and are justified in the plan.
- Keep PRs small enough for agent review and fast validation.
"""
    )


def frontend_md(ctx: HarnessContext) -> str:
    return (
        h1("Frontend Standards")
        + f"""## Scope

Use this file for UI, browser, accessibility, client state, styling, and visual verification decisions in `{ctx.project_name}`.

## Required Practices

- Keep UI state close to where it is used unless shared state is clearly required.
- Use existing component libraries, tokens, routing, and data-loading patterns.
- Validate user-visible flows in a browser when layout, interaction, or rendering changes.
- Ensure text does not overlap, overflow controls, or rely on viewport-scaled font sizes.
- Use accessible labels, focus states, keyboard paths, and semantic elements.
- Avoid generic decorative UI that does not serve the product workflow.

## Verification

For UI changes, record at least one of:

- Browser smoke flow.
- Component/unit test.
- Screenshot comparison or manual screenshot note.
- Console error check.
- Accessibility check.

## Project-Specific Frontend Commands

- Dev server: `{{FRONTEND_DEV_COMMAND}}`
- Test: `{{FRONTEND_TEST_COMMAND}}`
- Lint/typecheck: `{{FRONTEND_CHECK_COMMAND}}`
"""
    )


def backend_md(ctx: HarnessContext) -> str:
    return (
        h1("Backend Standards")
        + f"""## Scope

Use this file for APIs, services, persistence, jobs, integrations, queues, migrations, and server-side runtime behavior in `{ctx.project_name}`.

## Required Practices

- Validate all external inputs at the boundary.
- Keep persistence details behind repository or gateway interfaces.
- Keep business rules in service/use-case code, not route handlers or database adapters.
- Make retries, idempotency, pagination, and timeouts explicit for external calls.
- Treat migrations as production code with rollback or recovery notes.
- Log enough context to diagnose failures without leaking secrets or sensitive data.

## Verification

For backend changes, record the relevant checks:

- Unit tests for business rules.
- Integration tests for storage or external boundaries.
- Migration dry run or rollback note.
- API contract tests or schema checks.
- Local smoke command with logs.

## Project-Specific Backend Commands

- Server: `{{BACKEND_DEV_COMMAND}}`
- Test: `{{BACKEND_TEST_COMMAND}}`
- Migration: `{{MIGRATION_COMMAND}}`
- Smoke: `{{BACKEND_SMOKE_COMMAND}}`
"""
    )


def plans_md(ctx: HarnessContext) -> str:
    return (
        h1("Planning and Persistent Execution")
        + f"""## Purpose

`docs/exec-plans/` is the durable memory for long-running agent work. It lets `{ctx.primary_agent}` resume after context compaction, session restarts, branch switches, or review handoffs.

## When To Create a Plan

Create `docs/exec-plans/active/<task-slug>.md` when a task:

- Touches more than one file or subsystem.
- Requires investigation before implementation.
- Has meaningful risk, ambiguity, or rollback concerns.
- May run longer than one session.
- Needs multiple validation steps.

Small one-file fixes can skip a plan if the final response records validation.

## Active Plan Template

```markdown
# {{TASK_TITLE}}

- Status: active
- Owner/agent: {ctx.primary_agent}
- Started: {{YYYY-MM-DD}}
- Last updated: {{YYYY-MM-DD}}

## User Request

{{USER_REQUEST}}

## Goal

{{VERIFIABLE_GOAL}}

## Non-Goals

{{OUT_OF_SCOPE}}

## Context

{{RELEVANT_FILES_AND_DOCS}}

## Plan

1. {{STEP}}
2. {{STEP}}
3. {{STEP}}

## Decisions

- {{DECISION}} - {{WHY}}

## Validation

- [ ] `{{COMMAND}}` - {{EXPECTED_RESULT}}

## Progress Log

- {{YYYY-MM-DD}}: {{WHAT_CHANGED}}

## Open Questions

- {{QUESTION_OR_NONE}}

## Follow-Ups

- {{FOLLOW_UP_OR_NONE}}
```

## Closing Work

When complete:

1. Record validation commands and results.
2. Record files or modules changed.
3. Record follow-up work that should not block the current change.
4. Move the file from `active/` to `completed/`.

## PR Discipline

- Prefer short-lived PRs.
- Keep merge gates focused on checks that catch real regressions.
- Use agent review for larger changes, but do not replace executable validation with review.
"""
    )


def product_sense_md(ctx: HarnessContext) -> str:
    return (
        h1("Product Sense")
        + f"""## Product Summary

{ctx.project_description}

## Core Domains

{ctx.domain_bullets}

## Primary Users

- `{{PRIMARY_USER}}`: `{{USER_GOAL}}`
- `{{SECONDARY_USER}}`: `{{USER_GOAL}}`

## Core Journeys

1. `{{JOURNEY_NAME}}`: `{{USER_INTENT}}` -> `{{SUCCESSFUL_OUTCOME}}`
2. `{{JOURNEY_NAME}}`: `{{USER_INTENT}}` -> `{{SUCCESSFUL_OUTCOME}}`

## Product Principles

- Prefer workflows that are clear, recoverable, and observable.
- Optimize for the user's real job, not for demo-only completeness.
- Do not add product behavior that is not in a spec, issue, user request, or accepted decision.
- If behavior is ambiguous, document the assumption or ask before implementation.

## Non-Goals

- `{{NON_GOAL}}`

## Product Decision Sources

- Specs: `docs/product-specs/`
- Design docs: `docs/design-docs/`
- ADRs: `docs/adr/`
- Completed plans: `docs/exec-plans/completed/`
"""
    )


def quality_score_md(ctx: HarnessContext) -> str:
    return (
        h1("Quality Score")
        + f"""## Goal

Quality means `{ctx.project_name}` can be changed repeatedly by agents without silent regressions, architectural drift, or unreproducible bugs.

## Scorecard

Grade each changed module from 0 to 4:

- 0: No clear owner, no tests, no validation, unclear boundaries.
- 1: Basic behavior works, but checks are manual or incomplete.
- 2: Main paths covered by automated checks; boundaries mostly clear.
- 3: Edge cases, failure modes, and integration points are covered.
- 4: Checks are fast, deterministic, remediation-oriented, and documented.

## Minimum Bar For Changes

- Run the narrowest meaningful validation command.
- Add or update tests when behavior changes.
- Add regression coverage for bug fixes unless impractical; record why if skipped.
- Keep failing command output actionable for agents.
- Update affected docs or plans when contracts change.

## Validation Layers

- Formatting: `{{FORMAT_COMMAND}}`
- Linting: `{{LINT_COMMAND}}`
- Type checking: `{{TYPECHECK_COMMAND}}`
- Unit tests: `{{UNIT_TEST_COMMAND}}`
- Integration tests: `{{INTEGRATION_TEST_COMMAND}}`
- End-to-end or smoke tests: `{{SMOKE_COMMAND}}`
- Build: `{{BUILD_COMMAND}}`

## Review Checklist

- Does the change satisfy the user request?
- Are boundaries preserved?
- Are inputs validated at the edge?
- Are errors observable and actionable?
- Are secrets and sensitive data protected?
- Is there a recorded validation result?
"""
    )


def reliability_md(ctx: HarnessContext) -> str:
    return (
        h1("Reliability and Operations")
        + f"""## Goal

Agents must be able to run, observe, debug, and recover `{ctx.project_name}` locally or in ephemeral workspaces.

## Local Runtime

Document the canonical local commands:

- Install: `{{INSTALL_COMMAND}}`
- Start app: `{{DEV_COMMAND}}`
- Start dependencies: `{{DEPENDENCIES_COMMAND}}`
- Seed data: `{{SEED_COMMAND}}`
- Health check: `{{HEALTH_CHECK_COMMAND}}`
- Full validation: `{{FULL_VALIDATION_COMMAND}}`

## Ephemeral Workspaces

For risky or long-running changes:

- Use a clean worktree or disposable checkout.
- Start only the services required for the task.
- Record ports, environment variables, seeded data, and logs in the active plan.
- Clean up background processes before handing off.

## Observability

Runtime systems should expose:

- Structured logs with request/job identifiers.
- Health checks for critical dependencies.
- Metrics or counters for important workflows.
- Error traces with enough context to reproduce.
- Browser console and network information for frontend failures.

## Debugging Requirements

When fixing a bug:

1. Reproduce it.
2. Identify the failing boundary or invariant.
3. Add a regression check when practical.
4. Record validation in the active plan or final response.

## Incidents

Create `docs/incidents/<date>-<slug>.md` for user-impacting failures. Include impact, timeline, root cause, fix, validation, and follow-up prevention.
"""
    )


def security_md(ctx: HarnessContext) -> str:
    return (
        h1("Security Baseline")
        + f"""## Scope

Security rules apply to code, docs, generated artifacts, test fixtures, local scripts, CI, and deployment configuration in `{ctx.project_name}`.

## Required Practices

- Never commit secrets, tokens, private keys, production credentials, or real user data.
- Keep example environment files explicit and non-sensitive.
- Validate and sanitize untrusted input at the boundary.
- Enforce authorization near protected resources and business operations.
- Use least-privilege credentials for local, CI, staging, and production environments.
- Avoid logging secrets, tokens, credentials, or sensitive personal data.
- Review dependency additions for maintenance, license, and supply-chain risk.

## Agent Rules

- If a task requires a secret, ask the user to provide it through the approved runtime mechanism.
- If a secret is found in the repo, stop and report it; do not copy it into plans or logs.
- If security posture changes, update this file or the relevant runbook.

## Verification

- Dependency audit: `{{DEPENDENCY_AUDIT_COMMAND}}`
- Secret scan: `{{SECRET_SCAN_COMMAND}}`
- Auth/security tests: `{{SECURITY_TEST_COMMAND}}`
"""
    )


def core_beliefs_md(ctx: HarnessContext) -> str:
    return (
        h1("Core Beliefs")
        + f"""## Agent-First Development

The working model is: `Agent = Model + Harness`.

Humans steer by setting goals, constraints, and review standards. Agents execute by reading repo-local context, making changes, running checks, and recording outcomes.

## Repository Is Truth

Knowledge outside the repository is invisible to future agents. Convert decisions, product behavior, operational recipes, and validation lessons into committed files.

## Feedback Beats Memory

Prefer tools that fail loudly and explain how to fix the failure. Linters, tests, scripts, and health checks should teach `{ctx.primary_agent}` the next safe action.

## Parse At The Boundary

Do not guess data shapes. Validate external input, configuration, persisted records, API responses, and generated content at explicit boundaries.

## Anti-Entropy

Repeated mistakes should become shared utilities, checks, examples, or runbooks. Do not let agents repeatedly hand-roll the same fragile helper.

## Fast, Recoverable Iteration

Prefer small changes with visible validation. Minor non-blocking follow-ups should be recorded and handled in later focused work instead of expanding the current change indefinitely.
"""
    )


def local_development_md(ctx: HarnessContext) -> str:
    return (
        h1("Local Development Runbook")
        + f"""## Purpose

This runbook should let a new agent start `{ctx.project_name}` from a clean checkout.

## Setup

1. Install dependencies: `{{INSTALL_COMMAND}}`
2. Create local env file: `{{ENV_SETUP_COMMAND}}`
3. Start dependencies: `{{DEPENDENCIES_COMMAND}}`
4. Run migrations: `{{MIGRATION_COMMAND}}`
5. Seed data: `{{SEED_COMMAND}}`
6. Start app: `{{DEV_COMMAND}}`

## Health Check

- Command or URL: `{{HEALTH_CHECK_COMMAND_OR_URL}}`
- Expected result: `{{EXPECTED_HEALTH_RESULT}}`

## Common Failures

- `{{ERROR_MESSAGE}}`: `{{REMEDIATION}}`

## Cleanup

- Stop services: `{{STOP_COMMAND}}`
- Remove local generated state: `{{CLEAN_COMMAND}}`
"""
    )


def debugging_md(ctx: HarnessContext) -> str:
    return (
        h1("Debugging Runbook")
        + f"""## First Response

1. Reproduce the issue with the smallest command or user flow.
2. Capture exact inputs, environment, logs, screenshots, and versions.
3. Identify whether the failure is frontend, backend, data, integration, infrastructure, or documentation.
4. Create an active plan if the fix is not trivial.

## Evidence To Capture

- Failing command or browser steps.
- Expected vs actual behavior.
- Relevant logs and trace IDs.
- Network requests, status codes, and payload shapes.
- Database records or fixture data, if relevant.
- Recent changes that may have affected the path.

## Fix Discipline

- Fix the cause, not only the symptom.
- Add a regression check when practical.
- Update a runbook when diagnosis required non-obvious steps.
- Record validation before closing the plan.
"""
    )


def validation_log_template_md(ctx: HarnessContext) -> str:
    return (
        h1("Validation Log Template")
        + f"""Use this template when a task has meaningful validation evidence that should survive the session.

```markdown
# Validation: {{TASK_OR_CHANGE}}

- Date: {{YYYY-MM-DD}}
- Agent: {ctx.primary_agent}
- Branch/worktree: {{BRANCH_OR_WORKTREE}}
- Related plan: {{PLAN_PATH}}

## Commands

| Command | Result | Notes |
| --- | --- | --- |
| `{{COMMAND}}` | pass/fail/skipped | {{NOTES}} |

## Manual Checks

- {{CHECK}}: {{RESULT}}

## Artifacts

- Logs: {{PATH_OR_NONE}}
- Screenshots: {{PATH_OR_NONE}}
- Traces: {{PATH_OR_NONE}}

## Residual Risk

- {{RISK_OR_NONE}}
```
"""
    )


def adr_md(ctx: HarnessContext) -> str:
    return (
        h1("ADR 0001: Agent Harness Constitution")
        + f"""- Status: accepted
- Date: {ctx.generated_on}

## Context

`{ctx.project_name}` is adopting an agent-first operating model. Future agents need durable project context, executable checks, and resumable task state.

## Decision

The repository will maintain a harness constitution made of concise root docs, focused `docs/` directories, active execution plans, validation records, runbooks, and architecture decision records.

## Consequences

- Important project knowledge must be written into the repo.
- Long-running work should update `docs/exec-plans/active/`.
- Repeated review comments should become automated checks or runbook updates.
- `AGENTS.md` stays a map and should not become a giant prompt.

## Validation

Check that the root docs exist, `AGENTS.md` links are valid, and local setup/validation commands are documented.
"""
    )


def ensure_dirs(root: Path, dry_run: bool) -> list[str]:
    created: list[str] = []
    for rel in DOC_DIRS:
        path = root / rel
        if path.exists():
            continue
        created.append(rel + "/")
        if not dry_run:
            path.mkdir(parents=True, exist_ok=True)
    return created


def write_files(
    root: Path, files: dict[str, str], *, force: bool, dry_run: bool
) -> tuple[list[str], list[str], list[str]]:
    created: list[str] = []
    updated: list[str] = []
    skipped: list[str] = []

    for rel, content in files.items():
        path = root / rel
        if path.exists():
            existing = path.read_text(encoding="utf-8")
            if existing == content:
                skipped.append(rel + " (unchanged)")
                continue
            if not force:
                skipped.append(rel + " (exists; use --force only with approval)")
                continue
            updated.append(rel)
        else:
            created.append(rel)
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    return created, updated, skipped


def write_gitkeeps(root: Path, dry_run: bool) -> list[str]:
    created: list[str] = []
    for rel in DOC_DIRS:
        keep = root / rel / ".gitkeep"
        if keep.exists():
            continue
        created.append(f"{rel}/.gitkeep")
        if not dry_run:
            keep.parent.mkdir(parents=True, exist_ok=True)
            keep.write_text("", encoding="utf-8")
    return created


def write_manifest(
    root: Path,
    ctx: HarnessContext,
    file_paths: list[str],
    *,
    force: bool,
    dry_run: bool,
) -> tuple[str, str | None]:
    rel = "docs/generated/harness-manifest.json"
    manifest = {
        "project_name": ctx.project_name,
        "project_description": ctx.project_description,
        "tech_stack": ctx.tech_stack,
        "domains": ctx.domain_list,
        "primary_agent": ctx.primary_agent,
        "generated_on": ctx.generated_on,
        "managed_root_files": ROOT_FILES,
        "managed_files": sorted(file_paths + [rel]),
        "note": "Generated by openai-harness-engineering. Existing files are preserved unless --force is used.",
    }
    content = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    path = root / rel
    existed = path.exists()
    if existed and path.read_text(encoding="utf-8") == content:
        return "skipped", rel + " (unchanged)"
    if existed and not force:
        return "skipped", rel + " (exists; use --force only with approval)"
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return ("updated" if existed else "created"), rel


def print_summary(
    dirs: list[str],
    created: list[str],
    updated: list[str],
    skipped: list[str],
    gitkeeps: list[str],
    manifest_result: tuple[str, str | None],
    dry_run: bool,
) -> None:
    prefix = "Dry run complete" if dry_run else "Harness initialization complete"
    print(prefix)

    if dirs:
        print("\nDirectories:")
        for item in dirs:
            print(f"  created {item}")

    manifest_status, manifest_path = manifest_result
    if manifest_path:
        if manifest_status == "created":
            created.append(manifest_path)
        elif manifest_status == "updated":
            updated.append(manifest_path)
        else:
            skipped.append(manifest_path)

    if gitkeeps:
        created.extend(gitkeeps)

    if created:
        print("\nCreated:")
        for item in created:
            print(f"  {item}")
    if updated:
        print("\nUpdated:")
        for item in updated:
            print(f"  {item}")
    if skipped:
        print("\nSkipped:")
        for item in skipped:
            print(f"  {item}")


def main() -> None:
    args = parse_args()
    root = Path(args.target).resolve()
    ctx = HarnessContext(
        project_name=args.project_name,
        project_description=args.project_description,
        tech_stack=args.tech_stack,
        domains=args.domains,
        primary_agent=args.primary_agent,
        generated_on=dt.date.today().isoformat(),
    )

    files = templates(ctx)
    dirs = ensure_dirs(root, args.dry_run)
    created, updated, skipped = write_files(
        root, files, force=args.force, dry_run=args.dry_run
    )
    gitkeeps = write_gitkeeps(root, args.dry_run)
    manifest_result = write_manifest(
        root,
        ctx,
        list(files.keys()),
        force=args.force,
        dry_run=args.dry_run,
    )
    print_summary(dirs, created, updated, skipped, gitkeeps, manifest_result, args.dry_run)


if __name__ == "__main__":
    main()
