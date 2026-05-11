#!/usr/bin/env python3
"""Audit a repository for thin harness readiness."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


PLAN_SECTIONS = [
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
CORE_DIRS = [
    "docs/exec-plans/active",
    "docs/exec-plans/completed",
    "docs/generated",
    "docs/runbooks",
    "docs/validation",
]
OPS_DIRS = ["docs/adr", "docs/incidents"]
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}")
COMMAND_RE = re.compile(r"`([^`\n]+)`")


@dataclass
class Finding:
    kind: str
    path: str
    message: str


@dataclass
class AuditReport:
    structure_failures: list[Finding] = field(default_factory=list)
    structure_warnings: list[Finding] = field(default_factory=list)
    workflow_failures: list[Finding] = field(default_factory=list)
    workflow_warnings: list[Finding] = field(default_factory=list)

    def add(self, bucket: str, kind: str, path: str, message: str) -> None:
        getattr(self, bucket).append(Finding(kind=kind, path=path, message=message))

    def exit_code(self) -> int:
        structure = bool(self.structure_failures)
        workflow = bool(self.workflow_failures)
        if structure and workflow:
            return 3
        if structure:
            return 1
        if workflow:
            return 2
        return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit thin harness files in a repo.")
    parser.add_argument("--target", default=".", help="Repository root.")
    parser.add_argument(
        "--mode",
        choices=["structure", "workflow", "full"],
        default="full",
        help="Which audit layers to run.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root))


def markdown_links(text: str) -> list[str]:
    return [target.strip() for target in MARKDOWN_LINK_RE.findall(text)]


def local_links(text: str) -> list[str]:
    links: list[str] = []
    for target in markdown_links(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        links.append(target.split("#", 1)[0])
    return links


def link_exists(root: Path, owner: Path, target: str) -> bool:
    if not target:
        return True
    path = (owner.parent / target).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return path.exists()


def has_section(text: str, section: str) -> bool:
    return bool(re.search(rf"^## {re.escape(section)}\s*$", text, re.MULTILINE))


def load_manifest(root: Path) -> dict:
    manifest_path = root / "docs" / "generated" / "harness-manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(read(manifest_path))
    except json.JSONDecodeError:
        return {"_invalid_json": True}


def expected_files(manifest: dict) -> tuple[list[str], list[str]]:
    profile = manifest.get("profile", "standard")
    enabled = set(manifest.get("enabled_surfaces", []))
    required = ["AGENTS.md", "PLANS.md", "QUALITY_SCORE.md", "RELIABILITY.md", "docs/generated/harness-manifest.json"]
    if profile in {"standard", "full"}:
        required.extend(["ARCHITECTURE.md", "DELIVERY.md", "DESIGN.md", "PRODUCT_SENSE.md", "SECURITY.md"])
    if "frontend" in enabled:
        required.append("FRONTEND.md")
    if "backend" in enabled:
        required.append("BACKEND.md")
    if "autonomy" in enabled:
        required.extend(
            [
                "AUTONOMY.md",
                "docs/runbooks/autonomous-operations.md",
                "docs/validation/autonomy-drill-template.md",
            ]
        )
    if "ops" in enabled:
        required.extend(
            [
                "docs/adr/0001-agent-harness-constitution.md",
                "docs/incidents/incident-template.md",
                "docs/runbooks/runbook-template.md",
                "docs/runbooks/deployment.md",
                "docs/validation/validation-log-template.md",
            ]
        )
    return required, profile_required_dirs(enabled)


def profile_required_dirs(enabled: set[str]) -> list[str]:
    dirs = list(CORE_DIRS)
    if "ops" in enabled:
        dirs.extend(OPS_DIRS)
    return dirs


def check_manifest(root: Path, manifest: dict, report: AuditReport) -> None:
    manifest_path = root / "docs" / "generated" / "harness-manifest.json"
    if manifest.get("_invalid_json"):
        report.add("structure_failures", "fail", rel(root, manifest_path), "Manifest is invalid JSON")
        return
    if not manifest:
        report.add("structure_failures", "missing", "docs/generated/harness-manifest.json", "Manifest is required")
        return

    for key in (
        "profile",
        "enabled_surfaces",
        "agents_map_max_lines",
        "required_commands",
        "doc_gardening_required",
        "trajectory_model",
        "exec_plan_index_pattern",
    ):
        if key not in manifest:
            report.add("structure_failures", "fail", rel(root, manifest_path), f"Manifest is missing {key!r}")

    if manifest.get("trajectory_model") != "exec-plan-indexed":
        report.add(
            "structure_failures",
            "fail",
            rel(root, manifest_path),
            "trajectory_model must be 'exec-plan-indexed'",
        )


def check_required_paths(root: Path, manifest: dict, report: AuditReport) -> None:
    files, dirs = expected_files(manifest)
    for item in files:
        if not (root / item).exists():
            report.add("structure_failures", "missing", item, "Required by selected profile or enabled surfaces")
    for item in dirs:
        if not (root / item).is_dir():
            report.add("structure_failures", "missing", item, "Required harness directory is missing")


def check_markdown_links(root: Path, paths: list[Path], report: AuditReport, bucket: str) -> None:
    for path in paths:
        text = read(path)
        for target in local_links(text):
            if link_exists(root, path, target):
                continue
            report.add(bucket, "fail", rel(root, path), f"Broken local link: {target}")


def check_agents_map(root: Path, manifest: dict, report: AuditReport, workflow: bool) -> None:
    path = root / "AGENTS.md"
    if not path.exists():
        return
    text = read(path)
    max_lines = manifest.get("agents_map_max_lines", 120)
    line_count = len(text.splitlines())
    bucket = "workflow_failures" if workflow else "structure_warnings"
    if line_count > max_lines:
        report.add(bucket, "fail" if workflow else "warn", "AGENTS.md", f"AGENTS.md has {line_count} lines; max is {max_lines}")


def check_plans(root: Path, report: AuditReport) -> None:
    plans_md = root / "PLANS.md"
    if plans_md.exists():
        text = read(plans_md)
        if "trajectory index" not in text.lower():
            report.add("structure_failures", "fail", "PLANS.md", "PLANS.md must describe the exec-plan as a trajectory index")

    plan_paths = sorted((root / "docs" / "exec-plans" / "active").glob("*.md"))
    plan_paths += sorted((root / "docs" / "exec-plans" / "completed").glob("*.md"))
    for path in plan_paths:
        text = read(path)
        for section in PLAN_SECTIONS:
            if not has_section(text, section):
                report.add("workflow_failures", "fail", rel(root, path), f"Missing exec-plan section: {section}")


def check_placeholders(root: Path, manifest: dict, report: AuditReport) -> None:
    for rel_path in manifest.get("managed_files", []):
        path = root / rel_path
        if not path.exists():
            continue
        if path.suffix not in {".md", ".json"}:
            continue
        matches = PLACEHOLDER_RE.findall(read(path))
        if matches:
            report.add(
                "workflow_failures",
                "fail",
                rel_path,
                f"Unresolved placeholders remain: {', '.join(sorted(set(matches))[:5])}",
            )


def runnable(command: str, root: Path) -> bool:
    env = os.environ.copy()
    env["HARNESS_AUDIT_NESTED"] = "1"
    result = subprocess.run(
        ["zsh", "-lc", command],
        cwd=root,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def check_required_commands(root: Path, manifest: dict, report: AuditReport) -> None:
    commands = manifest.get("required_commands", [])
    if not commands:
        report.add("workflow_failures", "fail", "docs/generated/harness-manifest.json", "required_commands must list at least one deterministic verification path")
        return

    executable_count = 0
    for item in commands:
        if isinstance(item, dict):
            command = item.get("command", "")
            doc = item.get("doc", "docs/generated/harness-manifest.json")
            name = item.get("name", command)
        else:
            command = str(item)
            doc = "docs/generated/harness-manifest.json"
            name = command

        if PLACEHOLDER_RE.search(command):
            report.add("workflow_failures", "fail", doc, f"Required command {name!r} is still a placeholder")
            continue
        if runnable(command, root):
            executable_count += 1
            continue
        report.add("workflow_failures", "fail", doc, f"Required command failed from repo root: {command}")

    if executable_count == 0:
        report.add("workflow_failures", "fail", "docs/generated/harness-manifest.json", "No deterministic verification command executed successfully")


def check_doc_gardening(root: Path, manifest: dict, report: AuditReport) -> None:
    if not manifest.get("doc_gardening_required"):
        return
    paths = [root / "AGENTS.md", root / "RELIABILITY.md"]
    text = "\n".join(read(path) for path in paths if path.exists())
    if "drift" not in text.lower() and "stale" not in text.lower():
        report.add(
            "workflow_failures",
            "fail",
            "AGENTS.md",
            "Recurring cleanup or drift control is not reachable from the core map",
        )


def check_command_docs(root: Path, report: AuditReport) -> None:
    runbook_dir = root / "docs" / "runbooks"
    if not runbook_dir.exists():
        return
    for path in sorted(runbook_dir.glob("*.md")):
        text = read(path)
        for command in COMMAND_RE.findall(text):
            if command.startswith("./") or " " in command or command.startswith("python") or command.startswith("codex"):
                if PLACEHOLDER_RE.search(command):
                    continue
                if runnable(command, root):
                    continue
                report.add("workflow_failures", "fail", rel(root, path), f"Runbook command failed from repo root: {command}")


def render_text(report: AuditReport, mode: str) -> str:
    lines: list[str] = []
    order = []
    if mode in {"structure", "full"}:
        order.extend(
            [
                ("Structure failures", report.structure_failures),
                ("Structure warnings", report.structure_warnings),
            ]
        )
    if mode in {"workflow", "full"}:
        order.extend(
            [
                ("Workflow failures", report.workflow_failures),
                ("Workflow warnings", report.workflow_warnings),
            ]
        )
    for title, items in order:
        if not items:
            continue
        lines.append(title + ":")
        for item in items:
            prefix = f"{item.path}: " if item.path else ""
            lines.append(f"- [{item.kind}] {prefix}{item.message}")
        lines.append("")
    lines.append(
        "Summary: "
        f"{len(report.structure_failures)} structure failures, "
        f"{len(report.structure_warnings)} structure warnings, "
        f"{len(report.workflow_failures)} workflow failures, "
        f"{len(report.workflow_warnings)} workflow warnings"
    )
    return "\n".join(lines)


def render_json(report: AuditReport) -> str:
    payload = {
        "structure_failures": [item.__dict__ for item in report.structure_failures],
        "structure_warnings": [item.__dict__ for item in report.structure_warnings],
        "workflow_failures": [item.__dict__ for item in report.workflow_failures],
        "workflow_warnings": [item.__dict__ for item in report.workflow_warnings],
        "exit_code": report.exit_code(),
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def main() -> None:
    args = parse_args()
    root = Path(args.target).resolve()
    report = AuditReport()
    manifest = load_manifest(root)

    markdown_paths = sorted(root.glob("*.md"))
    markdown_paths += sorted((root / "docs").rglob("*.md")) if (root / "docs").exists() else []

    if args.mode in {"structure", "full"}:
        check_manifest(root, manifest, report)
        if manifest and not manifest.get("_invalid_json"):
            check_required_paths(root, manifest, report)
        check_markdown_links(root, markdown_paths, report, "structure_failures")
        check_plans(root, report)

    if args.mode in {"workflow", "full"} and manifest and not manifest.get("_invalid_json"):
        check_agents_map(root, manifest, report, workflow=True)
        check_markdown_links(root, markdown_paths, report, "workflow_failures")
        check_placeholders(root, manifest, report)
        check_required_commands(root, manifest, report)
        check_doc_gardening(root, manifest, report)
        if os.environ.get("HARNESS_AUDIT_NESTED") != "1":
            check_command_docs(root, report)

    output = render_json(report) if args.json else render_text(report, args.mode)
    print(output)
    raise SystemExit(report.exit_code())


if __name__ == "__main__":
    main()
