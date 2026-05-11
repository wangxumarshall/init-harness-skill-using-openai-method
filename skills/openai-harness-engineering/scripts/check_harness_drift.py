#!/usr/bin/env python3
"""Read-only drift checks for a thin harness."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_./-]+\}\}")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
LAST_UPDATED_RE = re.compile(r"^- Last updated: (\d{4}-\d{2}-\d{2})$", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check harness drift without mutating files.")
    parser.add_argument("--target", default=".", help="Repository root.")
    parser.add_argument(
        "--placeholder-age-days",
        type=int,
        default=7,
        help="Report placeholders in files older than this many days.",
    )
    parser.add_argument(
        "--stale-plan-days",
        type=int,
        default=14,
        help="Report active plans older than this many days without update.",
    )
    return parser.parse_args()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def file_age_days(path: Path) -> int:
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return (datetime.now(timezone.utc) - modified).days


def load_manifest(root: Path) -> dict:
    path = root / "docs" / "generated" / "harness-manifest.json"
    if not path.exists():
        return {}
    return json.loads(read(path))


def broken_links(root: Path, path: Path) -> list[str]:
    issues: list[str] = []
    for target in LINK_RE.findall(read(path)):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        normalized = target.split("#", 1)[0]
        candidate = (path.parent / normalized).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            issues.append(normalized)
            continue
        if not candidate.exists():
            issues.append(normalized)
    return issues


def placeholder_issue(path: Path, max_age: int) -> list[str]:
    if file_age_days(path) < max_age:
        return []
    return sorted(set(PLACEHOLDER_RE.findall(read(path))))


def stale_plan_issue(path: Path, threshold: int) -> str | None:
    text = read(path)
    match = LAST_UPDATED_RE.search(text)
    if match:
        try:
            updated = datetime.strptime(match.group(1), "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if (datetime.now(timezone.utc) - updated).days > threshold:
                return f"last updated {match.group(1)}"
            return None
        except ValueError:
            return "invalid Last updated field"
    if file_age_days(path) > threshold:
        return f"file age {file_age_days(path)} days"
    return None


def main() -> None:
    args = parse_args()
    root = Path(args.target).resolve()
    manifest = load_manifest(root)
    issues: list[str] = []

    markdown_paths = sorted(root.glob("*.md"))
    markdown_paths += sorted((root / "docs").rglob("*.md")) if (root / "docs").exists() else []
    for path in markdown_paths:
        rel = path.relative_to(root)
        links = broken_links(root, path)
        if links:
            issues.append(f"{rel}: broken links -> {', '.join(links)}")
        placeholders = placeholder_issue(path, args.placeholder_age_days)
        if placeholders:
            issues.append(f"{rel}: stale placeholders -> {', '.join(placeholders)}")

    active_dir = root / "docs" / "exec-plans" / "active"
    if active_dir.exists():
        for path in sorted(active_dir.glob("*.md")):
            stale = stale_plan_issue(path, args.stale_plan_days)
            if stale:
                issues.append(f"{path.relative_to(root)}: stale active plan ({stale})")

    if manifest:
        enabled = set(manifest.get("enabled_surfaces", []))
        automation = manifest.get("automation") or {}
        if "frontend" not in enabled and (root / "FRONTEND.md").exists():
            issues.append("FRONTEND.md exists but manifest does not enable frontend surface")
        if "backend" not in enabled and (root / "BACKEND.md").exists():
            issues.append("BACKEND.md exists but manifest does not enable backend surface")
        if "autonomy" not in enabled and (root / "AUTONOMY.md").exists():
            issues.append("AUTONOMY.md exists but manifest does not enable autonomy surface")
        config_path = root / "docs/generated/autonomy-config.json"
        if automation.get("enabled"):
            declared = set(automation.get("adapter_files") or [])
            for rel in declared:
                if not (root / rel).exists():
                    issues.append(f"manifest declares missing automation adapter -> {rel}")
            if not config_path.exists():
                issues.append("automation enabled but docs/generated/autonomy-config.json is missing")
            else:
                try:
                    config = json.loads(read(config_path))
                except json.JSONDecodeError:
                    issues.append("docs/generated/autonomy-config.json is invalid JSON")
                    config = {}
                if config:
                    if config.get("provider") != automation.get("provider"):
                        issues.append("autonomy-config.json provider does not match manifest automation provider")
                    if config.get("runtime") != automation.get("runtime"):
                        issues.append("autonomy-config.json runtime does not match manifest automation runtime")
                    if config.get("secrets") != automation.get("secret_refs"):
                        issues.append("autonomy-config.json secrets do not match manifest secret_refs")
            runtime = automation.get("runtime")
            if runtime in {"ci-worker", "both"}:
                expected = {
                    ".github/workflows/agent-loop.yml",
                    ".github/codex/prompts/agent-loop.md",
                    "ops/agent-runtime/queue_worker.py",
                    "ops/agent-runtime/monitor_and_maybe_rollback.py",
                }
                for rel in sorted(expected - declared):
                    issues.append(f"runtime {runtime!r} missing ci-worker adapter declaration -> {rel}")
            if runtime in {"app-server", "both"}:
                expected = {
                    "ops/agent-runtime/app_server_bridge.py",
                    "ops/agent-runtime/app_server_schema.json",
                }
                for rel in sorted(expected - declared):
                    issues.append(f"runtime {runtime!r} missing app-server adapter declaration -> {rel}")
        elif config_path.exists():
            issues.append("autonomy-config.json exists but manifest automation is not enabled")

    if issues:
        print("Drift issues:")
        for issue in issues:
            print(f"- {issue}")
        raise SystemExit(1)

    print("No harness drift detected")


if __name__ == "__main__":
    main()
