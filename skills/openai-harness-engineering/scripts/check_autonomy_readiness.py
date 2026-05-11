#!/usr/bin/env python3
"""Assess whether a repo is wired for unattended agent operation."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_./-]+\}\}")
AUTONOMY_FILES = [
    "AUTONOMY.md",
    "DELIVERY.md",
    "docs/runbooks/autonomous-operations.md",
    "docs/runbooks/deployment.md",
]
AUTONOMY_COMMANDS = {"deploy", "deploy-verify", "rollback", "monitor", "autonomy-loop"}
APP_SERVER_COMMANDS = {"app_server_start", "app_server_read", "app_server_inject"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check unattended-operation readiness for a harnessed repo.")
    parser.add_argument("--target", default=".", help="Repository root.")
    return parser.parse_args()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def runnable(command: str, root: Path, env: dict[str, str] | None = None) -> bool:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    result = subprocess.run(
        ["zsh", "-lc", command],
        cwd=root,
        env=merged,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def load_json(path: Path) -> dict:
    return json.loads(read(path))


def load_manifest(root: Path) -> dict:
    path = root / "docs/generated/harness-manifest.json"
    if not path.exists():
        raise SystemExit("Missing docs/generated/harness-manifest.json")
    return load_json(path)


def main() -> None:
    args = parse_args()
    root = Path(args.target).resolve()
    manifest = load_manifest(root)
    failures: list[str] = []

    enabled = set(manifest.get("enabled_surfaces", []))
    autonomy = manifest.get("autonomy") or {}
    automation = manifest.get("automation") or {}
    if "autonomy" not in enabled or not autonomy.get("enabled"):
        failures.append("Autonomy surface is not enabled in the harness manifest")
    if not automation.get("enabled"):
        failures.append("Automation adapters are not enabled in the harness manifest")

    for rel in AUTONOMY_FILES:
        path = root / rel
        if not path.exists():
            failures.append(f"Missing autonomy file: {rel}")
            continue
        placeholders = sorted(set(PLACEHOLDER_RE.findall(read(path))))
        if placeholders:
            failures.append(f"{rel} still has placeholders: {', '.join(placeholders[:5])}")

    config_path = root / "docs/generated/autonomy-config.json"
    if not config_path.exists():
        failures.append("Missing docs/generated/autonomy-config.json")
        config = {}
    else:
        config = load_json(config_path)
        placeholders = sorted(set(PLACEHOLDER_RE.findall(read(config_path))))
        if placeholders:
            failures.append(f"docs/generated/autonomy-config.json still has placeholders: {', '.join(placeholders[:5])}")

    adapter_files = automation.get("adapter_files") or []
    for rel in adapter_files:
        path = root / rel
        if not path.exists():
            failures.append(f"Missing automation adapter file: {rel}")
            continue
        if path.suffix in {".md", ".json", ".yml", ".py"}:
            placeholders = sorted(set(PLACEHOLDER_RE.findall(read(path))))
            if placeholders:
                failures.append(f"{rel} still has placeholders: {', '.join(placeholders[:5])}")

    command_index = {}
    for item in manifest.get("required_commands", []):
        if isinstance(item, dict):
            command_index[item.get("name", "")] = item.get("command", "")

    commands = config.get("commands") or {}
    for name in sorted(AUTONOMY_COMMANDS):
        manifest_command = command_index.get(name, "")
        if not manifest_command:
            failures.append(f"Manifest is missing required autonomy command: {name}")
            continue
        if PLACEHOLDER_RE.search(manifest_command):
            failures.append(f"Autonomy command {name!r} is still a placeholder")
            continue
        config_key = name.replace("-", "_")
        config_command = commands.get(config_key, "")
        if config_command and config_command != manifest_command and name != "autonomy-loop":
            failures.append(f"Manifest and autonomy config disagree on command: {name}")
        if not runnable(manifest_command, root):
            failures.append(f"Autonomy command {name!r} failed from repo root: {manifest_command}")

    for key in ("trigger_mode", "state_store", "approval_policy", "escalation_path"):
        value = str(autonomy.get(key, ""))
        if not value:
            failures.append(f"Manifest autonomy field is missing: {key}")
        elif PLACEHOLDER_RE.search(value):
            failures.append(f"Manifest autonomy field {key!r} is still a placeholder")

    if config:
        for key in ("version", "provider", "runtime", "task_sources", "state", "commands", "approval", "rollback_policy", "monitor_policy", "limits", "secrets"):
            if key not in config:
                failures.append(f"Autonomy config is missing field: {key}")

        provider = automation.get("provider")
        runtime = automation.get("runtime")
        if config.get("provider") != provider:
            failures.append("Autonomy config provider does not match harness manifest")
        if config.get("runtime") != runtime:
            failures.append("Autonomy config runtime does not match harness manifest")

        state = config.get("state") or {}
        for key in ("checkpoint_path", "thread_id_path", "run_log_path"):
            value = str(state.get(key, ""))
            if not value:
                failures.append(f"Autonomy config state field is missing: {key}")
            elif PLACEHOLDER_RE.search(value):
                failures.append(f"Autonomy config state field {key!r} is still a placeholder")

        approval = config.get("approval") or {}
        policy = str(approval.get("policy", ""))
        if not policy:
            failures.append("Autonomy config approval.policy is missing")
        elif PLACEHOLDER_RE.search(policy):
            failures.append("Autonomy config approval.policy is still a placeholder")

        secret_refs = automation.get("secret_refs") or []
        config_secrets = config.get("secrets") or []
        if list(config_secrets) != list(secret_refs):
            failures.append("Autonomy config secrets do not match manifest secret_refs")
        for secret in config_secrets:
            if not isinstance(secret, str) or not secret.strip():
                failures.append("Autonomy config contains an empty secret ref")
                continue
            if PLACEHOLDER_RE.search(secret):
                failures.append(f"Autonomy config secret ref is still a placeholder: {secret}")
                continue
            if not os.environ.get(secret):
                failures.append(f"Required secret ref is not set in the environment: {secret}")

        executor_command = str(commands.get("executor", ""))
        if not executor_command:
            failures.append("Autonomy config command is missing: executor")
        elif PLACEHOLDER_RE.search(executor_command):
            failures.append("Autonomy config command 'executor' is still a placeholder")

        if runtime in {"app-server", "both"}:
            for key in sorted(APP_SERVER_COMMANDS):
                command = str(commands.get(key, ""))
                if not command:
                    failures.append(f"Autonomy config command is missing: {key}")
                elif PLACEHOLDER_RE.search(command):
                    failures.append(f"Autonomy config command {key!r} is still a placeholder")
            expected = {"ops/agent-runtime/app_server_bridge.py", "ops/agent-runtime/app_server_schema.json"}
            missing = expected - set(adapter_files)
            for rel in sorted(missing):
                failures.append(f"Manifest runtime requires app-server adapter but does not declare: {rel}")

        if runtime in {"ci-worker", "both"}:
            expected = {
                ".github/workflows/agent-loop.yml",
                ".github/codex/prompts/agent-loop.md",
                "ops/agent-runtime/queue_worker.py",
                "ops/agent-runtime/monitor_and_maybe_rollback.py",
            }
            missing = expected - set(adapter_files)
            for rel in sorted(missing):
                failures.append(f"Manifest runtime requires ci-worker adapter but does not declare: {rel}")

    if failures:
        print("Autonomy readiness failures:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("Autonomy readiness passed")


if __name__ == "__main__":
    main()
