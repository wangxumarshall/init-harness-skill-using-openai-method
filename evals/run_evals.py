#!/usr/bin/env python3
"""Run deterministic eval scenarios for the harness skill."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "skills/openai-harness-engineering/scripts/init_harness.py"
AUDIT = ROOT / "skills/openai-harness-engineering/scripts/audit_harness.py"
NEW_PLAN = ROOT / "skills/openai-harness-engineering/scripts/new_plan.py"
PROMPTS = ROOT / "evals/prompts.csv"
ARTIFACTS = ROOT / "evals/artifacts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run harness eval scenarios.")
    parser.add_argument(
        "--engine",
        choices=["direct", "codex"],
        default="direct",
        help="Use direct script execution or capture codex exec JSONL traces when available.",
    )
    return parser.parse_args()


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)


def direct_trace(command: list[str], cwd: Path) -> dict:
    result = run(command, cwd)
    return {
        "command": command,
        "cwd": str(cwd),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def maybe_codex_trace(prompt: str, cwd: Path) -> list[dict]:
    if shutil.which("codex") is None:
        return [{"type": "note", "message": "codex binary unavailable; no live codex trace captured"}]
    result = run(["codex", "exec", "--json", prompt], cwd)
    lines = []
    for line in result.stdout.splitlines():
        try:
            lines.append(json.loads(line))
        except json.JSONDecodeError:
            lines.append({"type": "raw", "line": line})
    if result.stderr:
        lines.append({"type": "stderr", "line": result.stderr})
    return lines


def scenario_root(scenario_id: str) -> Path:
    return ARTIFACTS / scenario_id


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, events: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events), encoding="utf-8")


def prepare_repo(kind: str) -> tuple[Path, Path]:
    temp_root = Path(tempfile.mkdtemp(prefix="harness-eval-"))
    repo = temp_root / "repo"
    repo.mkdir()
    if "existing repo" in kind:
        (repo / "README.md").write_text("# Existing Repo\n\nUser-authored intro.\n", encoding="utf-8")
        (repo / "package.json").write_text(json.dumps({"dependencies": {"react": "1.0.0"}}), encoding="utf-8")
    return temp_root, repo


def run_scenario(row: dict[str, str], engine: str) -> dict:
    scenario_id = row["id"]
    temp_root, repo = prepare_repo(row["kind"])
    profile = row.get("profile") or "standard"
    traces: list[dict] = []

    try:
        if row["expect_trigger"] == "true":
            if "operate" in row["id"]:
                traces.append(
                    direct_trace(
                        [
                            "python3",
                            str(NEW_PLAN),
                            "--target",
                            str(repo),
                            "--title",
                            "Flaky checkout retries",
                            "--request",
                            "Investigate flaky checkout retries",
                            "--goal",
                            "Retries are deterministic and validated",
                            "--agent",
                            "Codex",
                        ],
                        ROOT,
                    )
                )
            elif "audit" in row["id"] or "dogfood" in row["id"]:
                target = ROOT if "self" in row["id"] else repo
                traces.append(direct_trace(["python3", str(AUDIT), "--target", str(target), "--mode", "full", "--json"], ROOT))
            else:
                traces.append(
                    direct_trace(
                        [
                            "python3",
                            str(INIT),
                            "--target",
                            str(repo),
                            "--project-name",
                            "Eval Repo",
                            "--project-description",
                            "Disposable repo for harness evals",
                            "--tech-stack",
                            "Python",
                            "--domains",
                            "Testing",
                            "--primary-agent",
                            "Codex",
                            "--profile",
                            profile,
                        ],
                        ROOT,
                    )
                )
                traces.append(direct_trace(["python3", str(AUDIT), "--target", str(repo), "--mode", "structure", "--json"], ROOT))
        if engine == "codex":
            write_jsonl(scenario_root(scenario_id) / "codex-trace.jsonl", maybe_codex_trace(row["prompt"], ROOT))

        summary = {
            "id": scenario_id,
            "kind": row["kind"],
            "prompt": row["prompt"],
            "expect_trigger": row["expect_trigger"] == "true",
            "profile": row.get("profile") or "",
            "repo": str(repo),
            "traces": traces,
        }
        write_json(scenario_root(scenario_id) / "summary.json", summary)
        return summary
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def main() -> None:
    args = parse_args()
    rows = list(csv.DictReader(PROMPTS.read_text(encoding="utf-8").splitlines()))
    results = [run_scenario(row, args.engine) for row in rows]
    write_json(ARTIFACTS / "index.json", results)
    print(f"Stored eval artifacts in {ARTIFACTS}")


if __name__ == "__main__":
    main()
