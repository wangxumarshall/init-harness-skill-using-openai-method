#!/usr/bin/env python3
"""Assess whether a repo is wired for unattended agent operation."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}")
AUTONOMY_FILES = [
    "AUTONOMY.md",
    "DELIVERY.md",
    "docs/runbooks/autonomous-operations.md",
    "docs/runbooks/deployment.md",
]
AUTONOMY_COMMANDS = {"deploy", "deploy-verify", "rollback", "monitor", "autonomy-loop"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check unattended-operation readiness for a harnessed repo.")
    parser.add_argument("--target", default=".", help="Repository root.")
    return parser.parse_args()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def runnable(command: str, root: Path) -> bool:
    env = os.environ.copy()
    result = subprocess.run(
        ["zsh", "-lc", command],
        cwd=root,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def load_manifest(root: Path) -> dict:
    path = root / "docs/generated/harness-manifest.json"
    if not path.exists():
        raise SystemExit("Missing docs/generated/harness-manifest.json")
    return json.loads(read(path))


def main() -> None:
    args = parse_args()
    root = Path(args.target).resolve()
    manifest = load_manifest(root)
    failures: list[str] = []

    enabled = set(manifest.get("enabled_surfaces", []))
    autonomy = manifest.get("autonomy") or {}
    if "autonomy" not in enabled or not autonomy.get("enabled"):
        failures.append("Autonomy surface is not enabled in the harness manifest")

    for rel in AUTONOMY_FILES:
        path = root / rel
        if not path.exists():
            failures.append(f"Missing autonomy file: {rel}")
            continue
        placeholders = sorted(set(PLACEHOLDER_RE.findall(read(path))))
        if placeholders:
            failures.append(f"{rel} still has placeholders: {', '.join(placeholders[:5])}")

    command_index = {}
    for item in manifest.get("required_commands", []):
        if isinstance(item, dict):
            command_index[item.get("name", "")] = item.get("command", "")

    for name in sorted(AUTONOMY_COMMANDS):
        command = command_index.get(name, "")
        if not command:
            failures.append(f"Manifest is missing required autonomy command: {name}")
            continue
        if PLACEHOLDER_RE.search(command):
            failures.append(f"Autonomy command {name!r} is still a placeholder")
            continue
        if not runnable(command, root):
            failures.append(f"Autonomy command {name!r} failed from repo root: {command}")

    for key in ("trigger_mode", "state_store", "approval_policy", "escalation_path"):
        value = str(autonomy.get(key, ""))
        if not value:
            failures.append(f"Manifest autonomy field is missing: {key}")
        elif PLACEHOLDER_RE.search(value):
            failures.append(f"Manifest autonomy field {key!r} is still a placeholder")

    if failures:
        print("Autonomy readiness failures:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("Autonomy readiness passed")


if __name__ == "__main__":
    main()
