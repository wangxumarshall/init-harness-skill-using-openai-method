#!/usr/bin/env python3
"""Audit a repository for OpenAI-style harness readiness."""

from __future__ import annotations

import argparse
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

    print(f"\nSummary: {failures} missing required items, {warnings} warnings")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
