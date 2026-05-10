#!/usr/bin/env python3
"""Initialize or refresh a thinner OpenAI-style agent harness in a repository."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from dataclasses import dataclass
from pathlib import Path


MANAGED_HEADER = "<!-- openai-harness-engineering:managed-document -->"
SECTION_BEGIN = "<!-- openai-harness-engineering:section:"
SECTION_END = "<!-- /openai-harness-engineering:section:"
FRONTEND_MARKERS = [
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
    "vite.config.js",
    "vite.config.ts",
    "src/app",
    "src/pages",
    "app",
    "pages",
]
BACKEND_MARKERS = [
    "server",
    "api",
    "manage.py",
    "go.mod",
    "Cargo.toml",
    "pom.xml",
]
FRONTEND_PACKAGES = {"react", "next", "vue", "svelte", "@angular/core"}
BACKEND_PACKAGES = {"express", "fastify", "koa", "fastapi", "django", "flask"}
PROFILE_ROOT_FILES = {
    "minimal": ["AGENTS.md", "PLANS.md", "QUALITY_SCORE.md", "RELIABILITY.md"],
    "standard": [
        "AGENTS.md",
        "ARCHITECTURE.md",
        "DESIGN.md",
        "PLANS.md",
        "PRODUCT_SENSE.md",
        "QUALITY_SCORE.md",
        "RELIABILITY.md",
        "SECURITY.md",
    ],
    "full": [
        "AGENTS.md",
        "ARCHITECTURE.md",
        "DESIGN.md",
        "FRONTEND.md",
        "BACKEND.md",
        "PLANS.md",
        "PRODUCT_SENSE.md",
        "QUALITY_SCORE.md",
        "RELIABILITY.md",
        "SECURITY.md",
    ],
}
BASE_DIRS = [
    "docs/exec-plans/active",
    "docs/exec-plans/completed",
    "docs/generated",
    "docs/runbooks",
    "docs/validation",
]
OPS_DIRS = [
    "docs/adr",
    "docs/design-docs",
    "docs/incidents",
    "docs/product-specs",
    "docs/references",
]


@dataclass(frozen=True)
class HarnessContext:
    project_name: str
    project_description: str
    tech_stack: str
    domains: str
    primary_agent: str
    generated_on: str
    profile: str
    include_frontend: bool
    include_backend: bool
    include_ops: bool
    emit_adapters: str
    required_commands: list[dict[str, str]]

    @property
    def domain_list(self) -> list[str]:
        parts = re.split(r"[,;/\n]+", self.domains)
        cleaned = [part.strip() for part in parts if part.strip()]
        return cleaned or ["{{CORE_DOMAIN}}"]

    @property
    def domain_bullets(self) -> str:
        return "\n".join(f"- {part}" for part in self.domain_list)

    @property
    def enabled_surfaces(self) -> list[str]:
        surfaces = ["core"]
        if self.include_frontend:
            surfaces.append("frontend")
        if self.include_backend:
            surfaces.append("backend")
        if self.include_ops:
            surfaces.append("ops")
        return surfaces


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a thin, adaptive harness constitution and operating docs."
    )
    parser.add_argument("--target", default=".", help="Repository root to initialize.")
    parser.add_argument("--project-name", default="{{PROJECT_NAME}}")
    parser.add_argument("--project-description", default="{{PROJECT_DESC}}")
    parser.add_argument("--tech-stack", default="{{TECH_STACK}}")
    parser.add_argument("--domains", default="{{CORE_DOMAINS}}")
    parser.add_argument("--primary-agent", default="{{CODING_AGENT}}")
    parser.add_argument(
        "--profile",
        choices=["minimal", "standard", "full"],
        default="standard",
        help="How much harness surface to create.",
    )
    parser.add_argument(
        "--include-frontend",
        action="store_true",
        help="Force frontend-oriented docs even if detection is ambiguous.",
    )
    parser.add_argument(
        "--include-backend",
        action="store_true",
        help="Force backend-oriented docs even if detection is ambiguous.",
    )
    parser.add_argument(
        "--include-ops",
        action="store_true",
        help="Force ops-oriented docs such as ADRs and incident templates.",
    )
    parser.add_argument(
        "--emit-adapters",
        choices=["auto", "none", "all"],
        default="auto",
        help="Emit editor/agent adapter files into the target repo.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated files. Use only with explicit approval.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned changes without writing files.",
    )
    return parser.parse_args()


def make_doc(title: str, sections: list[tuple[str, str]]) -> str:
    body = [MANAGED_HEADER, f"# {title}", ""]
    for name, content in sections:
        body.append(f"{SECTION_BEGIN}{name} -->")
        body.append(f"## {name}")
        body.append("")
        body.append(content.rstrip())
        body.append(f"{SECTION_END}{name} -->")
        body.append("")
    return "\n".join(body).rstrip() + "\n"


def detect_surfaces(root: Path) -> tuple[bool, bool]:
    frontend = any((root / marker).exists() for marker in FRONTEND_MARKERS)
    backend = any((root / marker).exists() for marker in BACKEND_MARKERS)

    package_json = root / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        deps: set[str] = set()
        for key in ("dependencies", "devDependencies", "peerDependencies"):
            deps.update((data.get(key) or {}).keys())
        if deps & FRONTEND_PACKAGES:
            frontend = True
        if deps & BACKEND_PACKAGES:
            backend = True

    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8", errors="ignore").lower()
        if any(name in text for name in ("fastapi", "django", "flask")):
            backend = True

    return frontend, backend


def select_surfaces(args: argparse.Namespace, root: Path) -> tuple[bool, bool, bool]:
    detected_frontend, detected_backend = detect_surfaces(root)
    include_frontend = args.profile == "full" or args.include_frontend or (
        args.profile == "standard" and detected_frontend
    )
    include_backend = args.profile == "full" or args.include_backend or (
        args.profile == "standard" and detected_backend
    )
    include_ops = (
        args.profile == "full"
        or args.include_ops
        or args.profile == "standard"
    )
    return include_frontend, include_backend, include_ops


def default_required_commands() -> list[dict[str, str]]:
    return [
        {"name": "install", "command": "{{INSTALL_COMMAND}}", "doc": "RELIABILITY.md"},
        {"name": "validation", "command": "{{FULL_VALIDATION_COMMAND}}", "doc": "RELIABILITY.md"},
    ]


def build_context(args: argparse.Namespace, root: Path) -> HarnessContext:
    include_frontend, include_backend, include_ops = select_surfaces(args, root)
    return HarnessContext(
        project_name=args.project_name,
        project_description=args.project_description,
        tech_stack=args.tech_stack,
        domains=args.domains,
        primary_agent=args.primary_agent,
        generated_on=dt.date.today().isoformat(),
        profile=args.profile,
        include_frontend=include_frontend,
        include_backend=include_backend,
        include_ops=include_ops,
        emit_adapters=args.emit_adapters,
        required_commands=default_required_commands(),
    )


def templates(ctx: HarnessContext) -> dict[str, str]:
    files: dict[str, str] = {}
    for rel in PROFILE_ROOT_FILES[ctx.profile]:
        files[rel] = ROOT_TEMPLATE_BUILDERS[rel](ctx)

    if ctx.include_frontend:
        files["FRONTEND.md"] = frontend_md(ctx)
    if ctx.include_backend:
        files["BACKEND.md"] = backend_md(ctx)
    if ctx.include_ops:
        files["docs/runbooks/local-development.md"] = local_development_md(ctx)
        files["docs/runbooks/debugging.md"] = debugging_md(ctx)
        files["docs/runbooks/runbook-template.md"] = runbook_template_md(ctx)
        files["docs/validation/validation-log-template.md"] = validation_log_template_md(ctx)
        files["docs/incidents/incident-template.md"] = incident_template_md(ctx)
        files["docs/design-docs/core-beliefs.md"] = core_beliefs_md(ctx)
        files["docs/adr/0001-agent-harness-constitution.md"] = adr_md(ctx)

    files.update(adapter_templates(ctx))
    return files


def agents_md(ctx: HarnessContext) -> str:
    sections = [
        (
            "Start Here",
            "\n".join(
                [
                    "1. Read the user request.",
                    "2. Read the smallest relevant linked doc.",
                    "3. Check `docs/exec-plans/active/` before editing.",
                    "4. Leave behind updated plans, validation notes, and follow-ups.",
                ]
            ),
        ),
        (
            "Operating Split",
            "\n".join(
                [
                    f"- `{ctx.primary_agent}` handles interpretation, tradeoffs, and reporting.",
                    "- Scripts handle repeated deterministic mechanics.",
                    "- Repo docs hold durable state, constraints, and handoff context.",
                ]
            ),
        ),
        (
            "System of Record",
            "\n".join(
                [
                    "- [Planning Workflow](./PLANS.md)",
                    "- [Quality Gates](./QUALITY_SCORE.md)",
                    "- [Reliability & Maintenance](./RELIABILITY.md)",
                ]
                + ([ "- [Architecture & Boundaries](./ARCHITECTURE.md)" ] if ctx.profile != "minimal" else [])
                + ([ "- [Design Principles](./DESIGN.md)" ] if ctx.profile != "minimal" else [])
                + ([ "- [Product Sense](./PRODUCT_SENSE.md)" ] if ctx.profile != "minimal" else [])
                + ([ "- [Security Baseline](./SECURITY.md)" ] if ctx.profile != "minimal" else [])
                + ([ "- [Frontend Standards](./FRONTEND.md)" ] if ctx.include_frontend else [])
                + ([ "- [Backend Standards](./BACKEND.md)" ] if ctx.include_backend else [])
            ),
        ),
        (
            "Core Directories",
            "\n".join(
                [
                    "- `docs/exec-plans/active/`: current task trajectory indexes.",
                    "- `docs/exec-plans/completed/`: closed plans with outcome and evidence.",
                    "- `docs/validation/`: validation logs and smoke notes.",
                    "- `docs/runbooks/`: repeated setup, debugging, and maintenance procedures.",
                    "- `docs/generated/`: manifest and machine-readable harness metadata.",
                ]
                + ([ "- `docs/incidents/`: user-impacting failures and prevention follow-ups." ] if ctx.include_ops else [])
                + ([ "- `docs/adr/`: durable architecture and operating-model decisions." ] if ctx.include_ops else [])
            ),
        ),
        (
            "Project Facts",
            "\n".join(
                [
                    f"- Project: {ctx.project_name}",
                    f"- Description: {ctx.project_description}",
                    f"- Tech stack: {ctx.tech_stack}",
                    f"- Profile: {ctx.profile}",
                    f"- Primary agent: {ctx.primary_agent}",
                    "- Core domains:",
                    ctx.domain_bullets,
                ]
            ),
        ),
    ]
    return make_doc(f"{ctx.project_name} Agent Map", sections)


def architecture_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Architecture and Boundary Constraints",
        [
            (
                "Goal",
                f"Make `{ctx.project_name}` legible enough that a new agent can change it safely without hidden human context.",
            ),
            (
                "Boundary Rules",
                "\n".join(
                    [
                        "- Preserve clear dependency direction across types, config, services, runtime, and interfaces.",
                        "- Keep business rules out of UI glue, route handlers, and persistence adapters.",
                        "- Turn repeated boundary mistakes into structural checks or tests.",
                    ]
                ),
            ),
            (
                "Mechanical Enforcement",
                "\n".join(
                    [
                        "Preferred order: compiler -> linter -> tests -> structural checks -> CI.",
                        "Every failure should name the rule, the violating file, and the next safe fix.",
                    ]
                ),
            ),
        ],
    )


def design_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Design Principles",
        [
            (
                "Operating Principle",
                f"Use the minimum persistent structure that helps `{ctx.primary_agent}` orient, validate, or recover. Do not grow decorative docs.",
            ),
            (
                "Agent Coding Rules",
                "\n".join(
                    [
                        "1. State risky assumptions when they cannot be derived from repo context.",
                        "2. Prefer surgical changes over opportunistic refactors.",
                        "3. Turn repeated manual fixes into scripts, tests, or runbooks.",
                    ]
                ),
            ),
            (
                "Tech Stack Notes",
                "\n".join(
                    [
                        f"- Primary stack: `{ctx.tech_stack}`",
                        "- Install command: `{{INSTALL_COMMAND}}`",
                        "- Validation command: `{{FULL_VALIDATION_COMMAND}}`",
                    ]
                ),
            ),
        ],
    )


def frontend_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Frontend Standards",
        [
            (
                "Required Practices",
                "\n".join(
                    [
                        "- Validate user-visible changes in a browser.",
                        "- Keep accessibility, focus handling, and responsive text intact.",
                        "- Record at least one deterministic UI verification path.",
                    ]
                ),
            ),
            (
                "Verification",
                "\n".join(
                    [
                        "- Dev server: `{{FRONTEND_DEV_COMMAND}}`",
                        "- Checks: `{{FRONTEND_CHECK_COMMAND}}`",
                        "- Browser smoke flow: `{{FRONTEND_SMOKE_COMMAND}}`",
                    ]
                ),
            ),
        ],
    )


def backend_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Backend Standards",
        [
            (
                "Required Practices",
                "\n".join(
                    [
                        "- Validate external input at the boundary.",
                        "- Keep retries, timeouts, and idempotency explicit.",
                        "- Record at least one deterministic runtime verification path.",
                    ]
                ),
            ),
            (
                "Verification",
                "\n".join(
                    [
                        "- Server: `{{BACKEND_DEV_COMMAND}}`",
                        "- Tests: `{{BACKEND_TEST_COMMAND}}`",
                        "- Smoke: `{{BACKEND_SMOKE_COMMAND}}`",
                    ]
                ),
            ),
        ],
    )


def plans_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Planning and Persistent Execution",
        [
            (
                "Purpose",
                f"`docs/exec-plans/` is the durable trajectory index for long-running work so `{ctx.primary_agent}` can resume after compaction, handoff, or restarts.",
            ),
            (
                "When To Create a Plan",
                "\n".join(
                    [
                        "- More than one file or subsystem changes.",
                        "- Investigation is needed before implementation.",
                        "- The work may last longer than one session.",
                        "- Multiple validation steps or rollback concerns exist.",
                    ]
                ),
            ),
            (
                "Active Plan Template",
                "\n".join(
                    [
                        "- Status, owner, started date, last updated, trajectory role",
                        "- User Request, Goal, Non-Goals, Context, Context Read",
                        "- Plan, Actions Taken, Decisions, Decision Links",
                        "- Validation, Validation Evidence, Incident Links, Learnings",
                        "- Progress Log, Open Questions, Follow-Ups, Closure Notes, Next Agent Handoff",
                    ]
                ),
            ),
            (
                "Closing Work",
                "\n".join(
                    [
                        "1. Record validation commands and outcomes.",
                        "2. Record changed files or modules.",
                        "3. Move the plan from `active/` to `completed/`.",
                    ]
                ),
            ),
        ],
    )


def product_sense_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Product Sense",
        [
            ("Product Summary", ctx.project_description),
            ("Core Domains", ctx.domain_bullets),
            (
                "Decision Sources",
                "\n".join(
                    [
                        "- `docs/product-specs/`",
                        "- `docs/design-docs/`",
                        "- `docs/adr/`",
                        "- `docs/exec-plans/completed/`",
                    ]
                ),
            ),
        ],
    )


def quality_score_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Quality Score",
        [
            (
                "Goal",
                f"Quality means `{ctx.project_name}` can be changed repeatedly by agents without silent regressions or unrecoverable state.",
            ),
            (
                "Minimum Bar For Changes",
                "\n".join(
                    [
                        "- Run the narrowest meaningful validation command.",
                        "- Add or update regression coverage when behavior changes.",
                        "- Keep failure output actionable for the next agent.",
                    ]
                ),
            ),
            (
                "Validation Layers",
                "\n".join(
                    [
                        "- Formatting: `{{FORMAT_COMMAND}}`",
                        "- Linting: `{{LINT_COMMAND}}`",
                        "- Type checking: `{{TYPECHECK_COMMAND}}`",
                        "- Tests: `{{UNIT_TEST_COMMAND}}`",
                        "- Smoke: `{{SMOKE_COMMAND}}`",
                    ]
                ),
            ),
        ],
    )


def reliability_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Reliability and Maintenance",
        [
            (
                "Goal",
                f"Agents must be able to run, observe, debug, and clean up `{ctx.project_name}` without relying on conversational memory.",
            ),
            (
                "Local Runtime",
                "\n".join(
                    [
                        "- Install: `{{INSTALL_COMMAND}}`",
                        "- Start app: `{{DEV_COMMAND}}`",
                        "- Health check: `{{HEALTH_CHECK_COMMAND}}`",
                        "- Full validation: `{{FULL_VALIDATION_COMMAND}}`",
                    ]
                ),
            ),
            (
                "Harness Maintenance Loop",
                "\n".join(
                    [
                        "- Run a doc drift scan regularly.",
                        "- Clear unresolved placeholders before calling the harness complete.",
                        "- Review stale active plans and either update or close them.",
                    ]
                ),
            ),
        ],
    )


def security_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Security Baseline",
        [
            (
                "Required Practices",
                "\n".join(
                    [
                        "- Never commit secrets, tokens, private keys, or real user data.",
                        "- Keep auth and authorization close to protected operations.",
                        "- Avoid logging sensitive payloads into plans, validation logs, or incidents.",
                    ]
                ),
            ),
            (
                "Verification",
                "\n".join(
                    [
                        "- Dependency audit: `{{DEPENDENCY_AUDIT_COMMAND}}`",
                        "- Secret scan: `{{SECRET_SCAN_COMMAND}}`",
                        "- Security checks: `{{SECURITY_TEST_COMMAND}}`",
                    ]
                ),
            ),
        ],
    )


def core_beliefs_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Core Beliefs",
        [
            ("Agent-First Development", "Agent = Model + Harness. Keep the harness thin, legible, and executable."),
            ("Repository Is Truth", "Important decisions, validation paths, and recovery knowledge must live in repo-readable files."),
            ("Feedback Beats Memory", "Prefer scripts and checks that fail loudly over prose that agents must reinterpret."),
        ],
    )


def local_development_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Local Development Runbook",
        [
            (
                "Setup",
                "\n".join(
                    [
                        "1. Install dependencies: `{{INSTALL_COMMAND}}`",
                        "2. Start dependencies: `{{DEPENDENCIES_COMMAND}}`",
                        "3. Start the app: `{{DEV_COMMAND}}`",
                    ]
                ),
            ),
            (
                "Health Check",
                "\n".join(
                    [
                        "- Command or URL: `{{HEALTH_CHECK_COMMAND_OR_URL}}`",
                        "- Expected result: `{{EXPECTED_HEALTH_RESULT}}`",
                    ]
                ),
            ),
        ],
    )


def debugging_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Debugging Runbook",
        [
            (
                "First Response",
                "\n".join(
                    [
                        "1. Reproduce the issue with the smallest command or flow.",
                        "2. Capture exact inputs, environment, logs, and versions.",
                        "3. Create or update an exec-plan if the fix is not trivial.",
                    ]
                ),
            ),
            (
                "Fix Discipline",
                "\n".join(
                    [
                        "- Fix the cause, not only the symptom.",
                        "- Add a regression check when practical.",
                        "- Leave behind a runbook update if diagnosis was non-obvious.",
                    ]
                ),
            ),
        ],
    )


def validation_log_template_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Validation Log Template",
        [
            (
                "Template",
                "\n".join(
                    [
                        "- Date: {{YYYY-MM-DD}}",
                        f"- Agent: {ctx.primary_agent}",
                        "- Related exec-plan: {{EXEC_PLAN_PATH}}",
                        "- Commands and pass/fail notes",
                        "- Manual checks, artifacts, and residual risk",
                    ]
                ),
            )
        ],
    )


def incident_template_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Incident Record Template",
        [
            (
                "Template",
                "\n".join(
                    [
                        "- Status, opened date, owner, severity",
                        "- Related exec-plan",
                        "- Impact, timeline, root cause, fix",
                        "- Validation evidence and prevention follow-ups",
                    ]
                ),
            )
        ],
    )


def runbook_template_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Runbook Template",
        [
            (
                "Template",
                "\n".join(
                    [
                        "- Purpose, prerequisites, procedure, validation, rollback, common failures",
                        "- Related exec-plan and incident when relevant",
                    ]
                ),
            )
        ],
    )


def adr_md(ctx: HarnessContext) -> str:
    return make_doc(
        "ADR 0001: Thin Harness Constitution",
        [
            ("Context", f"`{ctx.project_name}` needs durable project context and executable checks for long-running agent work."),
            ("Decision", "Adopt a thin harness: short map, focused docs, deterministic scripts, and persistent trajectory records."),
            ("Consequences", "\n".join(["- Keep AGENTS.md short.", "- Prefer scripts over repeated prose.", "- Run recurring drift checks."])),
        ],
    )


ROOT_TEMPLATE_BUILDERS = {
    "AGENTS.md": agents_md,
    "ARCHITECTURE.md": architecture_md,
    "DESIGN.md": design_md,
    "FRONTEND.md": frontend_md,
    "BACKEND.md": backend_md,
    "PLANS.md": plans_md,
    "PRODUCT_SENSE.md": product_sense_md,
    "QUALITY_SCORE.md": quality_score_md,
    "RELIABILITY.md": reliability_md,
    "SECURITY.md": security_md,
}


def adapter_templates(ctx: HarnessContext) -> dict[str, str]:
    if ctx.emit_adapters == "none":
        return {}

    targets: set[str] = set()
    if ctx.emit_adapters == "all":
        targets = {
            ".cursor/rules/harness.mdc",
            ".trae/rules/harness.md",
            ".claude/commands/harness.md",
            ".codex/skills/openai-harness-engineering/SKILL.md",
        }
    elif ctx.primary_agent.lower() == "cursor":
        targets.add(".cursor/rules/harness.mdc")
    elif ctx.primary_agent.lower() == "trae":
        targets.add(".trae/rules/harness.md")
    elif ctx.primary_agent.lower() in {"claude", "claude code"}:
        targets.add(".claude/commands/harness.md")
    elif ctx.primary_agent.lower() == "codex":
        targets.add(".codex/skills/openai-harness-engineering/SKILL.md")

    content = (
        "# Harness Adapter\n\n"
        "Read `AGENTS.md` first, then follow `PLANS.md`, `QUALITY_SCORE.md`, and "
        "`RELIABILITY.md`. Do not duplicate the harness constitution here.\n"
    )
    return {path: content for path in targets}


def manifest_dirs(ctx: HarnessContext) -> list[str]:
    dirs = list(BASE_DIRS)
    if ctx.include_ops:
        dirs.extend(OPS_DIRS)
    return dirs


def ensure_dirs(root: Path, ctx: HarnessContext, dry_run: bool) -> list[str]:
    created: list[str] = []
    for rel in manifest_dirs(ctx):
        path = root / rel
        if path.exists():
            continue
        created.append(rel + "/")
        if not dry_run:
            path.mkdir(parents=True, exist_ok=True)
    return created


def split_sections(text: str) -> dict[str, str]:
    pattern = re.compile(
        rf"{re.escape(SECTION_BEGIN)}(?P<name>.+?) -->\n(?P<body>.*?){re.escape(SECTION_END)}(?P=name) -->",
        re.DOTALL,
    )
    sections: dict[str, str] = {}
    for match in pattern.finditer(text):
        sections[match.group("name")] = match.group("body").rstrip()
    return sections


def merge_managed(existing: str, generated: str) -> str | None:
    if MANAGED_HEADER not in existing:
        return None

    existing_sections = split_sections(existing)
    generated_sections = split_sections(generated)
    missing = [name for name in generated_sections if name not in existing_sections]
    if not missing:
        return existing

    merged = existing.rstrip() + "\n\n"
    for name in missing:
        merged += f"{SECTION_BEGIN}{name} -->\n{generated_sections[name]}\n{SECTION_END}{name} -->\n\n"
    return merged.rstrip() + "\n"


def write_files(
    root: Path,
    files: dict[str, str],
    *,
    force: bool,
    dry_run: bool,
) -> tuple[list[str], list[str], list[str]]:
    created: list[str] = []
    updated: list[str] = []
    skipped: list[str] = []

    for rel, content in files.items():
        path = root / rel
        if path.exists():
            existing = path.read_text(encoding="utf-8", errors="ignore")
            if existing == content:
                skipped.append(rel + " (unchanged)")
                continue

            merged = merge_managed(existing, content)
            if merged is not None and merged != existing:
                updated.append(rel + " (appended managed sections)")
                if not dry_run:
                    path.write_text(merged, encoding="utf-8")
                continue

            if not force:
                skipped.append(rel + " (exists; preserved)")
                continue
            updated.append(rel)
        else:
            created.append(rel)

        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    return created, updated, skipped


def write_gitkeeps(root: Path, ctx: HarnessContext, dry_run: bool) -> list[str]:
    created: list[str] = []
    for rel in manifest_dirs(ctx):
        keep = root / rel / ".gitkeep"
        if keep.exists():
            continue
        created.append(f"{rel}/.gitkeep")
        if not dry_run:
            keep.parent.mkdir(parents=True, exist_ok=True)
            keep.write_text("", encoding="utf-8")
    return created


def write_manifest(
    root: Path,
    ctx: HarnessContext,
    managed_files: list[str],
    *,
    force: bool,
    dry_run: bool,
) -> tuple[str, str | None]:
    rel = "docs/generated/harness-manifest.json"
    manifest = {
        "project_name": ctx.project_name,
        "project_description": ctx.project_description,
        "tech_stack": ctx.tech_stack,
        "domains": ctx.domain_list,
        "primary_agent": ctx.primary_agent,
        "generated_on": ctx.generated_on,
        "profile": ctx.profile,
        "enabled_surfaces": ctx.enabled_surfaces,
        "agents_map_max_lines": 120,
        "required_commands": ctx.required_commands,
        "doc_gardening_required": True,
        "trajectory_model": "exec-plan-indexed",
        "exec_plan_index_pattern": "docs/exec-plans/active/<task>.md -> docs/exec-plans/completed/<task>.md",
        "trajectory_related_dirs": {
            "plans": ["docs/exec-plans/active/", "docs/exec-plans/completed/"],
            "validation": ["docs/validation/"],
            "runbooks": ["docs/runbooks/"],
            "generated": ["docs/generated/"],
        },
        "managed_root_files": sorted(PROFILE_ROOT_FILES[ctx.profile]),
        "managed_files": sorted(managed_files + [rel]),
    }
    content = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    path = root / rel
    existed = path.exists()
    if existed and path.read_text(encoding="utf-8", errors="ignore") == content:
        return "skipped", rel + " (unchanged)"
    if existed and not force:
        return "skipped", rel + " (exists; preserved)"
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return ("updated" if existed else "created"), rel


def print_summary(
    dirs: list[str],
    created: list[str],
    updated: list[str],
    skipped: list[str],
    gitkeeps: list[str],
    manifest_result: tuple[str, str | None],
    dry_run: bool,
) -> None:
    print("Dry run complete" if dry_run else "Harness initialization complete")
    if dirs:
        print("\nDirectories:")
        for item in dirs:
            print(f"  created {item}")

    manifest_status, manifest_path = manifest_result
    if manifest_path:
        if manifest_status == "created":
            created.append(manifest_path)
        elif manifest_status == "updated":
            updated.append(manifest_path)
        else:
            skipped.append(manifest_path)

    if gitkeeps:
        created.extend(gitkeeps)

    if created:
        print("\nCreated:")
        for item in created:
            print(f"  {item}")
    if updated:
        print("\nUpdated:")
        for item in updated:
            print(f"  {item}")
    if skipped:
        print("\nSkipped:")
        for item in skipped:
            print(f"  {item}")


def main() -> None:
    args = parse_args()
    root = Path(args.target).resolve()
    ctx = build_context(args, root)
    files = templates(ctx)
    dirs = ensure_dirs(root, ctx, args.dry_run)
    created, updated, skipped = write_files(root, files, force=args.force, dry_run=args.dry_run)
    gitkeeps = write_gitkeeps(root, ctx, args.dry_run)
    manifest_result = write_manifest(
        root,
        ctx,
        list(files.keys()),
        force=args.force,
        dry_run=args.dry_run,
    )
    print_summary(dirs, created, updated, skipped, gitkeeps, manifest_result, args.dry_run)


if __name__ == "__main__":
    main()
