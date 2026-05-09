#!/usr/bin/env python3
"""Create a persistent execution plan for long-running agent work."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug or "task"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create docs/exec-plans/active plan.")
    parser.add_argument("--target", default=".", help="Repository root.")
    parser.add_argument("--title", required=True, help="Plan title.")
    parser.add_argument("--goal", default="{{VERIFIABLE_GOAL}}")
    parser.add_argument("--request", default="{{USER_REQUEST}}")
    parser.add_argument("--agent", default="{{CODING_AGENT}}")
    parser.add_argument("--slug", default=None)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing active plan with the same slug.",
    )
    return parser.parse_args()


def plan_content(title: str, request: str, goal: str, agent: str, today: str) -> str:
    return f"""# {title}

- Status: active
- Owner/agent: {agent}
- Started: {today}
- Last updated: {today}
- Trajectory role: exec-plan index

## User Request

{request}

## Goal

{goal}

## Non-Goals

- {{OUT_OF_SCOPE}}

## Context

- {{RELEVANT_FILES_AND_DOCS}}

## Context Read

- {{FILE_OR_DOC}} - {{WHY_IT_MATTERS}}

## Plan

1. {{STEP}}
2. {{STEP}}
3. {{STEP}}

## Actions Taken

- {{ACTION}} - {{FILES_OR_MODULES}}

## Decisions

- {{DECISION}} - {{WHY}}

## Decision Links

- ADR: {{ADR_PATH_OR_NONE}}
- Design doc/spec: {{DOC_PATH_OR_NONE}}

## Validation

- [ ] `{{COMMAND}}` - {{EXPECTED_RESULT}}

## Validation Evidence

- Validation log: {{VALIDATION_LOG_PATH_OR_NONE}}
- Summary: {{RESULT_SUMMARY}}

## Incident Links

- Incident: {{INCIDENT_PATH_OR_NONE}}

## Learnings

- {{LEARNING_OR_NONE}}

## Progress Log

- {today}: Plan created.

## Open Questions

- {{QUESTION_OR_NONE}}

## Follow-Ups

- {{FOLLOW_UP_OR_NONE}}

## Closure Notes

- Outcome: {{OUTCOME_OR_PENDING}}
- Changed files/modules: {{CHANGED_FILES_OR_MODULES}}
- Residual risk: {{RISK_OR_NONE}}

## Next Agent Handoff

- Current state: {{STATE}}
- Next recommended action: {{NEXT_ACTION}}
- Blockers: {{BLOCKERS_OR_NONE}}
"""


def main() -> None:
    args = parse_args()
    root = Path(args.target).resolve()
    slug = args.slug or slugify(args.title)
    plan_dir = root / "docs" / "exec-plans" / "active"
    path = plan_dir / f"{slug}.md"

    if path.exists() and not args.force:
        raise SystemExit(f"Plan already exists: {path}")

    today = dt.date.today().isoformat()
    content = plan_content(args.title, args.request, args.goal, args.agent, today)
    plan_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
