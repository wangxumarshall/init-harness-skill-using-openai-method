#!/usr/bin/env python3
"""Audit a repository for OpenAI-style harness readiness."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_FILES = [
    "AGENTS.md",
    "ARCHITECTURE.md",
    "DESIGN.md",
    "PLANS.md",
    "PRODUCT_SENSE.md",
    "QUALITY_SCORE.md",
    "RELIABILITY.md",
    "SECURITY.md",
    "docs/generated/harness-manifest.json",
    "docs/validation/validation-log-template.md",
    "docs/incidents/incident-template.md",
    "docs/runbooks/runbook-template.md",
]

REQUIRED_DIRS = [
    "docs/exec-plans/active",
    "docs/exec-plans/completed",
    "docs/runbooks",
    "docs/validation",
    "docs/incidents",
    "docs/adr",
]

AGENTS_LINKS = [
    "ARCHITECTURE.md",
    "DESIGN.md",
    "PRODUCT_SENSE.md",
    "QUALITY_SCORE.md",
    "RELIABILITY.md",
    "SECURITY.md",
    "PLANS.md",
]

KEYWORDS = {
    "ARCHITECTURE.md": ["Mechanical Enforcement", "Types -> Config -> Repo -> Service"],
    "PLANS.md": ["docs/exec-plans/active", "Validation", "Progress Log"],
    "QUALITY_SCORE.md": ["Linting", "Type checking", "Unit tests"],
    "RELIABILITY.md": ["Health check", "Observability", "Incidents"],
    "SECURITY.md": ["Never commit secrets", "Verification"],
}

REQUIRED_EXEC_PLAN_SECTIONS = [
    "User Request",
    "Goal",
    "Non-Goals",
    "Context",
    "Context Read",
    "Plan",
    "Actions Taken",
    "Decisions",
    "Decision Links",
    "Validation",
    "Validation Evidence",
    "Incident Links",
    "Learnings",
    "Progress Log",
    "Open Questions",
    "Follow-Ups",
    "Closure Notes",
    "Next Agent Handoff",
]

REQUIRED_TRAJECTORY_METADATA = [
    "trajectory_model",
    "exec_plan_index_pattern",
    "trajectory_related_dirs",
    "required_exec_plan_sections",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit harness files in a repo.")
    parser.add_argument("--target", default=".", help="Repository root.")
    return parser.parse_args()


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="ignore")


def report(status: str, message: str) -> None:
    print(f"[{status}] {message}")


def has_section(text: str, section: str) -> bool:
    return bool(re.search(rf"^## {re.escape(section)}\s*$", text, re.MULTILINE))


def check_plan_sections(rel: str, text: str) -> int:
    failures = 0
    for section in REQUIRED_EXEC_PLAN_SECTIONS:
        if has_section(text, section):
            continue
        failures += 1
        report("fail", f"{rel} is missing exec-plan trajectory section: {section}")
    return failures


def main() -> None:
    args = parse_args()
    root = Path(args.target).resolve()
    failures = 0
    warnings = 0

    for rel in REQUIRED_FILES:
        path = root / rel
        if path.exists():
            report("ok", f"{rel} exists")
        else:
            failures += 1
            report("missing", f"{rel} is required for agent orientation")

    for rel in REQUIRED_DIRS:
        path = root / rel
        if path.is_dir():
            report("ok", f"{rel}/ exists")
        else:
            failures += 1
            report("missing", f"{rel}/ is required for persistent operations")

    agents = root / "AGENTS.md"
    if agents.exists():
        text = read(agents)
        line_count = len(text.splitlines())
        if line_count > 160:
            warnings += 1
            report("warn", "AGENTS.md is long; keep it as a map and move detail elsewhere")
        for target in AGENTS_LINKS:
            if target not in text:
                warnings += 1
                report("warn", f"AGENTS.md does not mention {target}")

    for rel, terms in KEYWORDS.items():
        path = root / rel
        if not path.exists():
            continue
        text = read(path)
        for term in terms:
            if re.search(re.escape(term), text, re.IGNORECASE):
                continue
            warnings += 1
            report("warn", f"{rel} should mention {term!r}")

    plans_path = root / "PLANS.md"
    if plans_path.exists():
        plans_text = read(plans_path)
        if not re.search(r"exec-plan.*trajectory index", plans_text, re.IGNORECASE | re.DOTALL):
            failures += 1
            report("fail", "PLANS.md must explain that an exec-plan acts as the trajectory index")
        failures += check_plan_sections("PLANS.md active plan template", plans_text)

    plan_files = sorted((root / "docs" / "exec-plans" / "active").glob("*.md"))
    plan_files += sorted((root / "docs" / "exec-plans" / "completed").glob("*.md"))
    for path in plan_files:
        failures += check_plan_sections(str(path.relative_to(root)), read(path))

    manifest_path = root / "docs" / "generated" / "harness-manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(read(manifest_path))
        except json.JSONDecodeError as exc:
            failures += 1
            report("fail", f"docs/generated/harness-manifest.json is invalid JSON: {exc}")
        else:
            for key in REQUIRED_TRAJECTORY_METADATA:
                if key in manifest:
                    continue
                failures += 1
                report("fail", f"docs/generated/harness-manifest.json is missing {key!r}")
            if (
                "trajectory_model" in manifest
                and manifest.get("trajectory_model") != "exec-plan-indexed"
            ):
                failures += 1
                report(
                    "fail",
                    "docs/generated/harness-manifest.json must set trajectory_model to 'exec-plan-indexed'",
                )
            sections = manifest.get("required_exec_plan_sections", [])
            missing_sections = [
                section
                for section in REQUIRED_EXEC_PLAN_SECTIONS
                if section not in sections
            ]
            for section in missing_sections:
                failures += 1
                report(
                    "fail",
                    "docs/generated/harness-manifest.json required_exec_plan_sections "
                    f"is missing {section!r}",
                )

    validation_template = root / "docs" / "validation" / "validation-log-template.md"
    if validation_template.exists():
        validation_text = read(validation_template)
        if "Related exec-plan" not in validation_text:
            failures += 1
            report(
                "fail",
                "docs/validation/validation-log-template.md must include a Related exec-plan field",
            )

    print(f"\nSummary: {failures} failures, {warnings} warnings")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
