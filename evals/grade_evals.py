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
    present_files = set(summary.get("present_files", []))
    captured_artifacts = summary.get("captured_artifacts", {})
    expect_trigger = row["expect_trigger"] == "true"
    expected_exit = int(row.get("expected_exit") or 0)

    if expect_trigger and not traces:
        errors.append("expected skill-like execution traces but found none")
    if not expect_trigger and traces:
        errors.append("negative control should not produce execution traces")

    for trace in traces:
        command_text = " ".join(trace.get("command", []))
        if trace.get("returncode", 0) != expected_exit and "audit_harness.py" in command_text:
            errors.append(
                f"expected audit exit {expected_exit} but got {trace.get('returncode', 0)} for "
                f"{command_text}"
            )
        elif "audit_harness.py" not in command_text and trace.get("returncode", 0) != 0:
            if "check_autonomy_readiness.py" in command_text and row.get("expect_autonomy_ready") != "true":
                continue
            errors.append(f"command failed: {command_text}")

    if row["profile"]:
        init_trace = next((trace for trace in traces if "init_harness.py" in " ".join(trace.get("command", []))), None)
        if init_trace and f"--profile {row['profile']}" not in " ".join(init_trace.get("command", [])):
            errors.append(f"expected profile {row['profile']} was not used")
        if row.get("include_autonomy") == "true" and init_trace and "--include-autonomy" not in " ".join(init_trace.get("command", [])):
            errors.append("expected --include-autonomy flag was not used")
        if row.get("automation_runtime") and init_trace and f"--automation-runtime {row['automation_runtime']}" not in " ".join(init_trace.get("command", [])):
            errors.append(f"expected automation runtime {row['automation_runtime']} was not used")

    expected_files = [item.strip() for item in (row.get("expect_files") or "").split(",") if item.strip()]
    for path in expected_files:
        if path not in present_files:
            errors.append(f"expected generated file missing from summary: {path}")

    if row.get("expect_autonomy_ready") == "true" or row.get("run_autonomy_check") == "true":
        autonomy_trace = next((trace for trace in traces if "check_autonomy_readiness.py" in " ".join(trace.get("command", []))), None)
        if not autonomy_trace:
            errors.append("expected autonomy readiness trace but found none")
        elif row.get("expect_autonomy_ready") == "true" and autonomy_trace.get("returncode", 0) != 0:
            errors.append("autonomy readiness check did not pass")
        elif row.get("expect_autonomy_ready") != "true" and autonomy_trace.get("returncode", 0) == 0:
            errors.append("autonomy readiness check unexpectedly passed")

    if row.get("expect_failure_contains"):
        autonomy_trace = next((trace for trace in traces if "check_autonomy_readiness.py" in " ".join(trace.get("command", []))), None)
        if not autonomy_trace or row["expect_failure_contains"] not in (autonomy_trace.get("stdout", "") + autonomy_trace.get("stderr", "")):
            errors.append(f"expected autonomy readiness failure to mention {row['expect_failure_contains']!r}")

    if row.get("run_monitor_fixture") == "true":
        monitor_trace = next((trace for trace in traces if "monitor_and_maybe_rollback.py" in " ".join(trace.get("command", []))), None)
        if not monitor_trace:
            errors.append("expected monitor fixture trace but found none")
        outcome = captured_artifacts.get("monitor_outcome")
        if not outcome:
            errors.append("expected monitor outcome artifact but found none")
        else:
            expected = row.get("expect_monitor_outcome")
            if expected == "rolled_back" and not outcome.get("rolled_back"):
                errors.append("expected rollback outcome but rolled_back was false")

    if row.get("run_app_server_fixture") == "true":
        if not captured_artifacts.get("thread_state") or not captured_artifacts.get("app_server_last_turn"):
            errors.append("expected app-server thread state artifacts but found none")

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
