#!/usr/bin/env python3
"""Run deterministic eval scenarios for the harness skill."""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "skills/openai-harness-engineering/scripts/init_harness.py"
AUDIT = ROOT / "skills/openai-harness-engineering/scripts/audit_harness.py"
AUTONOMY_CHECK = ROOT / "skills/openai-harness-engineering/scripts/check_autonomy_readiness.py"
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


def run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False, env=merged)


def direct_trace(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> dict:
    result = run(command, cwd, env=env)
    return {
        "command": command,
        "cwd": str(cwd),
        "env_keys": sorted((env or {}).keys()),
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


def replace_in_files(repo: Path, replacements: dict[str, str]) -> None:
    for path in repo.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".json", ".yml", ".py"}:
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        for source, target in replacements.items():
            updated = updated.replace(source, target)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def wire_autonomy_fixture(
    repo: Path,
    *,
    monitor_should_fail: bool = False,
    include_app_server: bool = True,
    missing_secret_ref: bool = False,
) -> dict[str, str]:
    ok = "python3 -c 'raise SystemExit(0)'"
    fail = "python3 -c 'raise SystemExit(1)'"
    fixture_dir = repo / "ops/agent-runtime/fixture_commands"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    (fixture_dir / "executor.py").write_text(
        "import json\nprint(json.dumps({'ok': True, 'source': 'executor'}))\n",
        encoding="utf-8",
    )
    (fixture_dir / "app_server_start.py").write_text(
        "import json\nprint(json.dumps({'thread_id': 'thread-eval-1'}))\n",
        encoding="utf-8",
    )
    (fixture_dir / "app_server_read.py").write_text(
        "import json, os\nprint(json.dumps({'thread_id': os.environ.get('CODEX_THREAD_ID', ''), 'messages': []}))\n",
        encoding="utf-8",
    )
    (fixture_dir / "app_server_inject.py").write_text(
        "import json\nprint(json.dumps({'accepted': True}))\n",
        encoding="utf-8",
    )
    executor = "python3 ops/agent-runtime/fixture_commands/executor.py"
    app_start = "python3 ops/agent-runtime/fixture_commands/app_server_start.py"
    app_read = "python3 ops/agent-runtime/fixture_commands/app_server_read.py"
    app_inject = "python3 ops/agent-runtime/fixture_commands/app_server_inject.py"
    replacements = {
        "{{INSTALL_COMMAND}}": ok,
        "{{FULL_VALIDATION_COMMAND}}": ok,
        "{{DEPLOY_COMMAND}}": ok,
        "{{DEPLOY_VERIFY_COMMAND}}": ok,
        "{{ROLLBACK_COMMAND}}": ok,
        "{{MONITOR_COMMAND}}": fail if monitor_should_fail else ok,
        "{{AUTONOMY_LOOP_COMMAND}}": "python3 ops/agent-runtime/queue_worker.py --task-file docs/generated/autonomy-task.json",
        "{{AUTONOMY_OBJECTIVE}}": "Keep the demo service healthy and ship validated changes.",
        "{{AUTONOMY_TRIGGER_MODE}}": "scheduled",
        "{{AUTONOMY_STATE_STORE}}": "docs/generated/autonomy-state.json",
        "{{AUTONOMY_ESCALATION_PATH}}": "oncall@example.com",
        "{{AUTONOMY_APPROVAL_POLICY}}": "human approval required for production schema changes",
        "{{AUTONOMY_ALLOWED_ACTIONS}}": "implement code, run tests, deploy routine changes",
        "{{AUTONOMY_APPROVAL_REQUIRED_ACTIONS}}": "schema migrations, credential rotation",
        "{{AUTONOMY_STOP_CONDITIONS}}": "failing rollback, data loss risk, repeated deploy failures",
        "{{AUTONOMY_STATE_SYNC_COMMAND}}": ok,
        "{{AUTONOMY_RETRY_POLICY}}": "retry deploy twice, then escalate",
        "{{AUTONOMY_ESCALATION_TRIGGER}}": "two consecutive failed deploy verifications",
        "{{AUTONOMY_SHUTDOWN_COMMAND}}": ok,
        "{{AUTOMATION_EXECUTOR_COMMAND}}": executor,
        "{{APP_SERVER_START_COMMAND}}": app_start if include_app_server else ok,
        "{{APP_SERVER_READ_COMMAND}}": app_read if include_app_server else ok,
        "{{APP_SERVER_INJECT_COMMAND}}": app_inject if include_app_server else ok,
        "{{AUTOMATION_SCHEDULE}}": "*/30 * * * *",
        "{{SPEC_PATH_OR_REQUEST_LINK}}": "docs/product-specs/demo-spec.md",
        "{{DEPENDENCIES_COMMAND}}": ok,
        "{{DEV_COMMAND}}": ok,
        "{{HEALTH_CHECK_COMMAND}}": ok,
        "{{HEALTH_CHECK_COMMAND_OR_URL}}": ok,
        "{{EXPECTED_HEALTH_RESULT}}": "exit code 0",
        "{{FORMAT_COMMAND}}": ok,
        "{{LINT_COMMAND}}": ok,
        "{{TYPECHECK_COMMAND}}": ok,
        "{{UNIT_TEST_COMMAND}}": ok,
        "{{SMOKE_COMMAND}}": ok,
        "{{DEPENDENCY_AUDIT_COMMAND}}": ok,
        "{{SECRET_SCAN_COMMAND}}": ok,
        "{{SECURITY_TEST_COMMAND}}": ok,
        "{{DEPLOY_ARTIFACT_NOTE}}": "demo-build-1",
        "{{DEPLOY_EXPECTED_RESULT}}": "exit code 0",
        "{{ROLLBACK_TRIGGER}}": "failed post-deploy verification",
        "{{EXEC_PLAN_PATH}}": "docs/exec-plans/active/demo.md",
        "{{YYYY-MM-DD}}": "2026-05-11",
        "{{ROLLBACK_COMMAND_OR_NONE}}": ok,
    }
    replace_in_files(repo, replacements)
    product_specs = repo / "docs/product-specs"
    product_specs.mkdir(parents=True, exist_ok=True)
    (product_specs / "demo-spec.md").write_text("# Demo Spec\n\nAutonomy fixture.\n", encoding="utf-8")
    (repo / "docs/generated/autonomy-task.json").write_text(
        json.dumps({"task_id": "demo-task", "source": "fixture", "objective": "run worker"}, indent=2) + "\n",
        encoding="utf-8",
    )
    env = {"OPENAI_API_KEY": "test-openai-key"}
    if not missing_secret_ref:
        env["CODEX_HOME"] = str(repo / ".codex-home")
    return env


def run_scenario(row: dict[str, str], engine: str) -> dict:
    scenario_id = row["id"]
    temp_root, repo = prepare_repo(row["kind"])
    profile = row.get("profile") or "standard"
    primary_agent = row.get("primary_agent") or "Codex"
    include_autonomy = row.get("include_autonomy") == "true"
    automation_runtime = row.get("automation_runtime") or "both"
    traces: list[dict] = []
    present_files: list[str] = []
    captured_artifacts: dict[str, object] = {}

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
                            primary_agent,
                            "--profile",
                            profile,
                            "--automation-runtime",
                            automation_runtime,
                        ]
                        + (["--include-autonomy"] if include_autonomy else []),
                        ROOT,
                    )
                )
                traces.append(direct_trace(["python3", str(AUDIT), "--target", str(repo), "--mode", "structure", "--json"], ROOT))
                fixture_env: dict[str, str] | None = None
                needs_fixture = any(
                    row.get(key) == "true"
                    for key in ("expect_autonomy_ready", "run_autonomy_check", "run_monitor_fixture", "run_app_server_fixture")
                )
                if needs_fixture:
                    fixture_env = wire_autonomy_fixture(
                        repo,
                        monitor_should_fail=row.get("monitor_should_fail") == "true",
                        include_app_server=automation_runtime in {"app-server", "both"},
                        missing_secret_ref=row.get("missing_secret_ref") == "true",
                    )
                if row.get("expect_autonomy_ready") == "true" or row.get("run_autonomy_check") == "true":
                    traces.append(direct_trace(["python3", str(AUTONOMY_CHECK), "--target", str(repo)], ROOT, env=fixture_env))
                if row.get("run_monitor_fixture") == "true":
                    traces.append(
                        direct_trace(
                            ["python3", "ops/agent-runtime/monitor_and_maybe_rollback.py", "--reason", scenario_id],
                            repo,
                            env=fixture_env,
                        )
                    )
                    monitor_outcome = repo / "docs/generated/monitor-outcome.json"
                    if monitor_outcome.exists():
                        captured_artifacts["monitor_outcome"] = json.loads(monitor_outcome.read_text(encoding="utf-8"))
                if row.get("run_app_server_fixture") == "true":
                    traces.append(
                        direct_trace(
                            ["python3", "ops/agent-runtime/app_server_bridge.py", "start"],
                            repo,
                            env=fixture_env,
                        )
                    )
                    traces.append(
                        direct_trace(
                            ["python3", "ops/agent-runtime/app_server_bridge.py", "resume"],
                            repo,
                            env=fixture_env,
                        )
                    )
                    thread_state = repo / "docs/generated/autonomy-thread.json"
                    last_turn = repo / "docs/generated/app-server-last-turn.json"
                    if thread_state.exists():
                        captured_artifacts["thread_state"] = json.loads(thread_state.read_text(encoding="utf-8"))
                    if last_turn.exists():
                        captured_artifacts["app_server_last_turn"] = json.loads(last_turn.read_text(encoding="utf-8"))
                present_files = sorted(
                    str(path.relative_to(repo))
                    for path in repo.rglob("*")
                    if path.is_file()
                )
        if engine == "codex":
            write_jsonl(scenario_root(scenario_id) / "codex-trace.jsonl", maybe_codex_trace(row["prompt"], ROOT))

        summary = {
            "id": scenario_id,
            "kind": row["kind"],
            "prompt": row["prompt"],
            "expect_trigger": row["expect_trigger"] == "true",
            "profile": row.get("profile") or "",
            "primary_agent": primary_agent,
            "include_autonomy": include_autonomy,
            "automation_runtime": automation_runtime,
            "repo": str(repo),
            "present_files": present_files,
            "traces": traces,
            "captured_artifacts": captured_artifacts,
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
