#!/usr/bin/env python3
"""Grade deterministic eval artifacts for the harness skill."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "evals/prompts.csv"
ARTIFACTS = ROOT / "evals/artifacts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Grade harness eval artifacts.")
    parser.add_argument("--artifacts", default=str(ARTIFACTS), help="Artifact directory.")
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def grade_summary(row: dict[str, str], summary: dict) -> list[str]:
    errors: list[str] = []
    traces = summary.get("traces", [])
    expect_trigger = row["expect_trigger"] == "true"
    expected_exit = int(row.get("expected_exit") or 0)

    if expect_trigger and not traces:
        errors.append("expected skill-like execution traces but found none")
    if not expect_trigger and traces:
        errors.append("negative control should not produce execution traces")

    for trace in traces:
        if trace.get("returncode", 0) != expected_exit and "audit_harness.py" in " ".join(trace.get("command", [])):
            errors.append(
                f"expected audit exit {expected_exit} but got {trace.get('returncode', 0)} for "
                f"{' '.join(trace.get('command', []))}"
            )
        elif "audit_harness.py" not in " ".join(trace.get("command", [])) and trace.get("returncode", 0) != 0:
            errors.append(f"command failed: {' '.join(trace.get('command', []))}")

    if row["profile"]:
        init_trace = next((trace for trace in traces if "init_harness.py" in " ".join(trace.get("command", []))), None)
        if init_trace and f"--profile {row['profile']}" not in " ".join(init_trace.get("command", [])):
            errors.append(f"expected profile {row['profile']} was not used")

    return errors


def main() -> None:
    args = parse_args()
    artifacts = Path(args.artifacts)
    rows = list(csv.DictReader(PROMPTS.read_text(encoding="utf-8").splitlines()))
    failures: list[str] = []
    for row in rows:
        summary_path = artifacts / row["id"] / "summary.json"
        if not summary_path.exists():
            failures.append(f"{row['id']}: missing summary artifact")
            continue
        errors = grade_summary(row, read_json(summary_path))
        failures.extend(f"{row['id']}: {error}" for error in errors)

    if failures:
        print("Eval grading failures:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("All eval artifacts passed deterministic grading")


if __name__ == "__main__":
    main()
