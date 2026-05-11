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
        "DELIVERY.md",
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
        "DELIVERY.md",
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
    "ops/agent-runtime",
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
    include_autonomy: bool
    emit_adapters: str
    automation_provider: str
    automation_runtime: str
    emit_automation_adapters: str
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
        if self.include_autonomy:
            surfaces.append("autonomy")
        return surfaces

    @property
    def automation_enabled(self) -> bool:
        return self.include_autonomy and self.automation_provider != "none"

    @property
    def automation_adapter_files(self) -> list[str]:
        if not self.automation_enabled or self.emit_automation_adapters == "none":
            return []
        files = [
            "docs/generated/autonomy-config.json",
        ]
        if self.automation_runtime in {"ci-worker", "both"}:
            files.extend(
                [
                    ".github/workflows/agent-loop.yml",
                    ".github/codex/prompts/agent-loop.md",
                    "ops/agent-runtime/queue_worker.py",
                    "ops/agent-runtime/monitor_and_maybe_rollback.py",
                ]
            )
        if self.automation_runtime in {"app-server", "both"}:
            files.extend(
                [
                    "ops/agent-runtime/app_server_bridge.py",
                    "ops/agent-runtime/app_server_schema.json",
                ]
            )
        return files


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
        "--include-autonomy",
        action="store_true",
        help="Add unattended-operation docs, policies, and readiness checks.",
    )
    parser.add_argument(
        "--emit-adapters",
        choices=["auto", "none", "all"],
        default="auto",
        help="Emit editor/agent adapter files into the target repo.",
    )
    parser.add_argument(
        "--automation-provider",
        choices=["codex", "none"],
        default="codex",
        help="Automation adapter provider for unattended runtime scaffolding.",
    )
    parser.add_argument(
        "--automation-runtime",
        choices=["ci-worker", "app-server", "both"],
        default="both",
        help="Automation runtime surface to generate when autonomy is enabled.",
    )
    parser.add_argument(
        "--emit-automation-adapters",
        choices=["auto", "none", "all"],
        default="auto",
        help="Emit runnable automation adapter files when autonomy is enabled.",
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


def select_surfaces(args: argparse.Namespace, root: Path) -> tuple[bool, bool, bool, bool]:
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
        or args.include_autonomy
        or args.profile == "standard"
    )
    include_autonomy = args.profile == "full" or args.include_autonomy
    return include_frontend, include_backend, include_ops, include_autonomy


def default_required_commands(include_autonomy: bool) -> list[dict[str, str]]:
    commands = [
        {"name": "install", "command": "{{INSTALL_COMMAND}}", "doc": "RELIABILITY.md"},
        {"name": "validation", "command": "{{FULL_VALIDATION_COMMAND}}", "doc": "RELIABILITY.md"},
    ]
    if include_autonomy:
        commands.extend(
            [
                {"name": "deploy", "command": "{{DEPLOY_COMMAND}}", "doc": "DELIVERY.md"},
                {"name": "deploy-verify", "command": "{{DEPLOY_VERIFY_COMMAND}}", "doc": "DELIVERY.md"},
                {"name": "rollback", "command": "{{ROLLBACK_COMMAND}}", "doc": "DELIVERY.md"},
                {"name": "monitor", "command": "{{MONITOR_COMMAND}}", "doc": "AUTONOMY.md"},
                {"name": "autonomy-loop", "command": "{{AUTONOMY_LOOP_COMMAND}}", "doc": "AUTONOMY.md"},
            ]
        )
    return commands


def normalize_automation_settings(args: argparse.Namespace, include_autonomy: bool) -> tuple[str, str, str]:
    if not include_autonomy:
        return "none", args.automation_runtime, "none"
    provider = args.automation_provider
    runtime = args.automation_runtime
    emit = args.emit_automation_adapters if provider != "none" else "none"
    return provider, runtime, emit


def finalize_required_commands(include_autonomy: bool, automation_enabled: bool) -> list[dict[str, str]]:
    commands = default_required_commands(include_autonomy)
    if not automation_enabled:
        return commands
    updated: list[dict[str, str]] = []
    for item in commands:
        item = dict(item)
        if item["name"] == "autonomy-loop":
            item["command"] = "python3 ops/agent-runtime/queue_worker.py --task-file docs/generated/autonomy-task.json"
            item["doc"] = "docs/generated/autonomy-config.json"
        updated.append(item)
    return updated


def build_context(args: argparse.Namespace, root: Path) -> HarnessContext:
    include_frontend, include_backend, include_ops, include_autonomy = select_surfaces(args, root)
    automation_provider, automation_runtime, emit_automation_adapters = normalize_automation_settings(
        args, include_autonomy
    )
    automation_enabled = include_autonomy and automation_provider != "none"
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
        include_autonomy=include_autonomy,
        emit_adapters=args.emit_adapters,
        automation_provider=automation_provider,
        automation_runtime=automation_runtime,
        emit_automation_adapters=emit_automation_adapters,
        required_commands=finalize_required_commands(include_autonomy, automation_enabled),
    )


def templates(ctx: HarnessContext) -> dict[str, str]:
    files: dict[str, str] = {}
    for rel in PROFILE_ROOT_FILES[ctx.profile]:
        files[rel] = ROOT_TEMPLATE_BUILDERS[rel](ctx)

    if ctx.include_autonomy and "DELIVERY.md" not in files:
        files["DELIVERY.md"] = delivery_md(ctx)
    if ctx.include_frontend:
        files["FRONTEND.md"] = frontend_md(ctx)
    if ctx.include_backend:
        files["BACKEND.md"] = backend_md(ctx)
    if ctx.include_autonomy:
        files["AUTONOMY.md"] = autonomy_md(ctx)
    if ctx.include_ops:
        files["docs/runbooks/local-development.md"] = local_development_md(ctx)
        files["docs/runbooks/debugging.md"] = debugging_md(ctx)
        files["docs/runbooks/deployment.md"] = deployment_md(ctx)
        if ctx.include_autonomy:
            files["docs/runbooks/autonomous-operations.md"] = autonomous_operations_md(ctx)
            files["docs/validation/autonomy-drill-template.md"] = autonomy_drill_template_md(ctx)
        files["docs/runbooks/runbook-template.md"] = runbook_template_md(ctx)
        files["docs/validation/validation-log-template.md"] = validation_log_template_md(ctx)
        files["docs/incidents/incident-template.md"] = incident_template_md(ctx)
        files["docs/design-docs/core-beliefs.md"] = core_beliefs_md(ctx)
        files["docs/adr/0001-agent-harness-constitution.md"] = adr_md(ctx)
    if ctx.automation_enabled:
        files["docs/generated/autonomy-config.json"] = autonomy_config_json(ctx)

    files.update(adapter_templates(ctx))
    files.update(automation_adapter_templates(ctx))
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
                + ([ "- [Autonomy Policy](./AUTONOMY.md)" ] if ctx.include_autonomy else [])
                + ([ "- [Design Principles](./DESIGN.md)" ] if ctx.profile != "minimal" else [])
                + ([ "- [Delivery Lifecycle](./DELIVERY.md)" ] if ctx.profile != "minimal" else [])
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
        (
            "Engineering Rules",
            "\n".join(
                [
                    "- Inspect the existing code path before adding abstractions.",
                    "- Match current architecture before inventing a new layer.",
                    "- Keep edits surgical; do not refactor unrelated code.",
                    "- Prefer the minimum code that solves the verified problem.",
                    "- Keep docs, scripts, and tests aligned when workflow or behavior changes.",
                    "- Add automated tests for new features.",
                    "- Use structured APIs or parsers when available.",
                    "- Code comments must be English.",
                    "- Never hand-edit generated code.",
                    "- Never add compatibility shims, dual-write logic, fallback paths, or legacy adapters unless explicitly asked.",
                    "- Prefer deleting obsolete paths over preserving both old and new behavior.",
                    "- Never introduce ad-hoc `console.*`; use existing logger modules.",
                    "- Never hardcode secrets, tokens, cookies, database credentials, or provider keys.",
                    "- Never modify, rotate, or commit production credentials from this repository.",
                ]
            ),
        ),
        (
            "Evidence Rules",
            "\n".join(
                [
                    "- Do not guess. Back claims with code, tests, logs, command output, or documented source files.",
                    "- If evidence is insufficient, say so and continue gathering evidence.",
                    "- If multiple interpretations exist, state them before choosing.",
                    "- Surface tradeoffs and push back when the simpler or safer path is clear.",
                ]
            ),
        ),
        (
            "Verification",
            "\n".join(
                [
                    "- Follow `QUALITY_SCORE.md` and `RELIABILITY.md` for required verification commands and release gates.",
                    "- Do not claim completion without recording the exact commands run and their results.",
                ]
            ),
        ),
        (
            "Commits and PRs",
            "\n".join(
                [
                    "- Keep commits atomic and grouped by logical intent.",
                    "- Use Conventional Commits such as `feat(web): ...`, `fix(server): ...`, `refactor(daemon): ...`, `test(e2e): ...`, `docs: ...`.",
                    "- Never commit code that still fails required lint, typecheck, or tests.",
                    "- PRs should include a short summary and exact verification commands; include screenshots for UI changes.",
                ]
            ),
        ),
        (
            "Responses",
            "\n".join(
                [
                    "- Reply in Chinese.",
                    "- Be concise.",
                    "- State result before cause when practical.",
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


def delivery_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Delivery Lifecycle",
        [
            (
                "Definition Of Done",
                "\n".join(
                    [
                        "1. The active spec or request is linked from an exec-plan or `docs/product-specs/`.",
                        "2. Implementation lands with the narrowest meaningful code and test changes.",
                        "3. Deterministic validation passes and the exact commands are recorded.",
                        "4. Deployment or release procedure is executed or explicitly handed off with a blocker.",
                        "5. Post-deploy verification and rollback expectations are recorded before closure.",
                    ]
                ),
            ),
            (
                "Required Evidence",
                "\n".join(
                    [
                        "- Spec or request path: `{{SPEC_PATH_OR_REQUEST_LINK}}`",
                        "- Implementation validation: `{{FULL_VALIDATION_COMMAND}}`",
                        "- Release/deploy command: `{{DEPLOY_COMMAND}}`",
                        "- Post-deploy verification: `{{DEPLOY_VERIFY_COMMAND}}`",
                        "- Rollback path: `{{ROLLBACK_COMMAND}}`",
                    ]
                ),
            ),
            (
                "Closure Rule",
                "Do not mark work complete until implementation, tests, verification, and deployment state are all either complete with evidence or explicitly blocked with the owner recorded.",
            ),
        ],
    )


def autonomy_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Autonomy Policy",
        [
            (
                "Mission Profile",
                "\n".join(
                    [
                        "- Primary objective: `{{AUTONOMY_OBJECTIVE}}`",
                        "- Trigger mode: `{{AUTONOMY_TRIGGER_MODE}}`",
                        "- Checkpoint store: `{{AUTONOMY_STATE_STORE}}`",
                        "- Human escalation path: `{{AUTONOMY_ESCALATION_PATH}}`",
                    ]
                ),
            ),
            (
                "Unattended Loop",
                "\n".join(
                    [
                        "1. Load the active spec, backlog, and latest exec-plan.",
                        "2. Run autonomy loop command: `{{AUTONOMY_LOOP_COMMAND}}`",
                        "3. Record checkpoints, validation, and incidents before the next cycle.",
                        "4. Stop or escalate when approval, safety, or rollback gates are hit.",
                    ]
                ),
            ),
            (
                "Approval Policy",
                "\n".join(
                    [
                        "- Allowed without human approval: `{{AUTONOMY_ALLOWED_ACTIONS}}`",
                        "- Requires approval: `{{AUTONOMY_APPROVAL_REQUIRED_ACTIONS}}`",
                        "- Immediate stop conditions: `{{AUTONOMY_STOP_CONDITIONS}}`",
                    ]
                ),
            ),
            (
                "Readiness Commands",
                "\n".join(
                    [
                        "- Monitor: `{{MONITOR_COMMAND}}`",
                        "- Deploy: `{{DEPLOY_COMMAND}}`",
                        "- Post-deploy verify: `{{DEPLOY_VERIFY_COMMAND}}`",
                        "- Rollback: `{{ROLLBACK_COMMAND}}`",
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
                        "- Keep deployment and rollback steps current with real production behavior.",
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


def deployment_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Deployment Runbook",
        [
            (
                "Release Path",
                "\n".join(
                    [
                        "1. Confirm the active spec, plan, and validation evidence are up to date.",
                        "2. Run deploy command: `{{DEPLOY_COMMAND}}`",
                        "3. Capture deploy artifact, environment, and version: `{{DEPLOY_ARTIFACT_NOTE}}`",
                    ]
                ),
            ),
            (
                "Verification",
                "\n".join(
                    [
                        "- Post-deploy check: `{{DEPLOY_VERIFY_COMMAND}}`",
                        "- Expected result: `{{DEPLOY_EXPECTED_RESULT}}`",
                    ]
                ),
            ),
            (
                "Rollback",
                "\n".join(
                    [
                        "- Trigger: `{{ROLLBACK_TRIGGER}}`",
                        "- Command or procedure: `{{ROLLBACK_COMMAND}}`",
                    ]
                ),
            ),
        ],
    )


def autonomous_operations_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Autonomous Operations Runbook",
        [
            (
                "Prerequisites",
                "\n".join(
                    [
                        "- Active spec linked from an exec-plan or `docs/product-specs/`.",
                        "- Real commands wired for validation, deploy, verify, rollback, and monitor.",
                        "- Approval and escalation contacts documented in `AUTONOMY.md`.",
                    ]
                ),
            ),
            (
                "Loop Procedure",
                "\n".join(
                    [
                        "1. Refresh state from the checkpoint store: `{{AUTONOMY_STATE_SYNC_COMMAND}}`",
                        "2. Execute unattended loop: `{{AUTONOMY_LOOP_COMMAND}}`",
                        "3. Run health or monitor checks: `{{MONITOR_COMMAND}}`",
                        "4. Append outcomes to validation and incident records before the next cycle.",
                    ]
                ),
            ),
            (
                "Failure Branches",
                "\n".join(
                    [
                        "- Retry policy: `{{AUTONOMY_RETRY_POLICY}}`",
                        "- Escalation trigger: `{{AUTONOMY_ESCALATION_TRIGGER}}`",
                        "- Failsafe shutdown: `{{AUTONOMY_SHUTDOWN_COMMAND}}`",
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


def autonomy_drill_template_md(ctx: HarnessContext) -> str:
    return make_doc(
        "Autonomy Drill Template",
        [
            (
                "Template",
                "\n".join(
                    [
                        "- Date: {{YYYY-MM-DD}}",
                        "- Objective exercised: {{AUTONOMY_OBJECTIVE}}",
                        "- Commands run: {{AUTONOMY_LOOP_COMMAND}}, {{MONITOR_COMMAND}}, {{DEPLOY_VERIFY_COMMAND}}",
                        "- Recovery branch tested: {{ROLLBACK_COMMAND_OR_NONE}}",
                        "- Result, residual risk, and escalation notes",
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


def autonomy_config_json(ctx: HarnessContext) -> str:
    config = {
        "version": 1,
        "provider": ctx.automation_provider,
        "runtime": ctx.automation_runtime,
        "task_sources": ["schedule", "repo_dispatch", "queue", "thread"],
        "state": {
            "checkpoint_path": "docs/generated/autonomy-state.json",
            "thread_id_path": "docs/generated/autonomy-thread.json",
            "run_log_path": "docs/validation/autonomy-run-log.jsonl",
        },
        "commands": {
            "install": "{{INSTALL_COMMAND}}",
            "validation": "{{FULL_VALIDATION_COMMAND}}",
            "deploy": "{{DEPLOY_COMMAND}}",
            "deploy_verify": "{{DEPLOY_VERIFY_COMMAND}}",
            "rollback": "{{ROLLBACK_COMMAND}}",
            "monitor": "{{MONITOR_COMMAND}}",
            "autonomy_loop": "python3 ops/agent-runtime/queue_worker.py --task-file docs/generated/autonomy-task.json",
            "executor": "{{AUTOMATION_EXECUTOR_COMMAND}}",
            "app_server_start": "{{APP_SERVER_START_COMMAND}}",
            "app_server_read": "{{APP_SERVER_READ_COMMAND}}",
            "app_server_inject": "{{APP_SERVER_INJECT_COMMAND}}",
        },
        "approval": {
            "policy": "{{AUTONOMY_APPROVAL_POLICY}}",
            "allowed_actions": "{{AUTONOMY_ALLOWED_ACTIONS}}",
            "approval_required_actions": "{{AUTONOMY_APPROVAL_REQUIRED_ACTIONS}}",
            "escalation_path": "{{AUTONOMY_ESCALATION_PATH}}",
        },
        "rollback_policy": {
            "on_verify_failure": True,
            "on_monitor_failure": True,
            "max_attempts": 1,
            "command": "{{ROLLBACK_COMMAND}}",
        },
        "monitor_policy": {
            "command": "{{MONITOR_COMMAND}}",
            "failure_signal": "nonzero_exit",
        },
        "limits": {
            "concurrency": 1,
            "max_retries": 2,
            "timeout_minutes": 30,
            "max_turns": 12,
        },
        "secrets": ["OPENAI_API_KEY", "CODEX_HOME"],
    }
    return json.dumps(config, indent=2, ensure_ascii=False) + "\n"


def automation_adapter_templates(ctx: HarnessContext) -> dict[str, str]:
    if not ctx.automation_enabled or ctx.emit_automation_adapters == "none":
        return {}

    files: dict[str, str] = {}
    if ctx.automation_runtime in {"ci-worker", "both"}:
        files[".github/workflows/agent-loop.yml"] = agent_loop_workflow_yml(ctx)
        files[".github/codex/prompts/agent-loop.md"] = agent_loop_prompt_md(ctx)
        files["ops/agent-runtime/queue_worker.py"] = queue_worker_py()
        files["ops/agent-runtime/monitor_and_maybe_rollback.py"] = monitor_and_maybe_rollback_py()
    if ctx.automation_runtime in {"app-server", "both"}:
        files["ops/agent-runtime/app_server_bridge.py"] = app_server_bridge_py()
        files["ops/agent-runtime/app_server_schema.json"] = app_server_schema_json()
    return files


def agent_loop_workflow_yml(ctx: HarnessContext) -> str:
    use_action = ctx.automation_provider == "codex"
    codex_step = (
        "      - name: Run Codex action\n"
        "        uses: openai/codex-action@v1\n"
        "        with:\n"
        "          prompt-file: .github/codex/prompts/agent-loop.md\n"
        "          output-file: docs/generated/codex-action-output.json\n"
        if use_action
        else
        "      - name: Run Codex CLI\n"
        "        run: |\n"
        "          codex exec --json \"$(cat .github/codex/prompts/agent-loop.md)\" > docs/generated/codex-action-output.jsonl\n"
    )
    return "\n".join(
        [
            "name: agent-loop",
            "",
            "on:",
            "  workflow_dispatch:",
            "  schedule:",
            "    - cron: '{{AUTOMATION_SCHEDULE}}'",
            "  repository_dispatch:",
            "    types: [agent-loop]",
            "",
            "concurrency:",
            "  group: agent-loop-${{ github.ref }}",
            "  cancel-in-progress: false",
            "",
            "jobs:",
            "  unattended-loop:",
            "    runs-on: ubuntu-latest",
            "    timeout-minutes: 30",
            "    env:",
            "      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}",
            "      CODEX_HOME: ${{ secrets.CODEX_HOME }}",
            "    steps:",
            "      - uses: actions/checkout@v4",
            "      - uses: actions/setup-python@v5",
            "        with:",
            "          python-version: '3.11'",
            "      - name: Prepare task payload",
            "        run: |",
            "          mkdir -p docs/generated docs/validation",
            "          printf '{\"task_id\":\"github-actions-loop\",\"source\":\"github-actions\",\"objective\":\"{{AUTONOMY_OBJECTIVE}}\"}\\n' > docs/generated/autonomy-task.json",
            codex_step.rstrip(),
            "      - name: Queue worker checkpoint",
            "        run: |",
            "          python3 ops/agent-runtime/queue_worker.py --task-file docs/generated/autonomy-task.json",
            "      - name: Monitor and rollback fixture",
            "        if: always()",
            "        run: |",
            "          python3 ops/agent-runtime/monitor_and_maybe_rollback.py --reason github-actions",
            "      - name: Upload artifacts",
            "        if: always()",
            "        uses: actions/upload-artifact@v4",
            "        with:",
            "          name: agent-loop-artifacts",
            "          path: |",
            "            docs/generated/",
            "            docs/validation/",
        ]
    ) + "\n"


def agent_loop_prompt_md(ctx: HarnessContext) -> str:
    return "\n".join(
        [
            f"# {ctx.project_name} Agent Loop",
            "",
            "Use the repository harness as the source of truth.",
            "Read `AGENTS.md`, `PLANS.md`, `QUALITY_SCORE.md`, `RELIABILITY.md`, and `AUTONOMY.md` first.",
            "",
            "Goal:",
            "- `{{AUTONOMY_OBJECTIVE}}`",
            "",
            "Required behavior:",
            "- Continue or create an exec-plan for non-trivial work.",
            "- Run deterministic validation before reporting completion.",
            "- Leave machine-readable artifacts under `docs/generated/` and `docs/validation/`.",
            "- Stop and record escalation if approval or rollback gates are hit.",
        ]
    ) + "\n"


def queue_worker_py() -> str:
    return """#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Codex-first autonomy queue task.")
    parser.add_argument("--config", default="docs/generated/autonomy-config.json")
    parser.add_argument("--task-file")
    parser.add_argument("--task-json")
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_task(args: argparse.Namespace) -> dict:
    if args.task_json:
        return json.loads(args.task_json)
    if args.task_file:
        return read_json(Path(args.task_file))
    if not sys.stdin.isatty():
        payload = sys.stdin.read().strip()
        if payload:
            return json.loads(payload)
    env_payload = os.environ.get("AUTONOMY_TASK_JSON", "").strip()
    if env_payload:
        return json.loads(env_payload)
    return {"task_id": "default-task", "source": "unknown", "objective": "unspecified"}


def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\\n")


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    root = config_path.resolve().parents[2]
    config = read_json(config_path)
    task = load_task(args)
    state = config["state"]
    command = task.get("command") or config["commands"]["executor"]
    started_at = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(
        ["zsh", "-lc", command],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
        env=os.environ.copy(),
    )
    checkpoint_path = root / state["checkpoint_path"]
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "task": task,
        "executor_command": command,
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
    append_jsonl(root / state["run_log_path"], checkpoint)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
"""


def monitor_and_maybe_rollback_py() -> str:
    return """#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deploy verification, monitor, and rollback if needed.")
    parser.add_argument("--config", default="docs/generated/autonomy-config.json")
    parser.add_argument("--reason", default="manual")
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_command(root: Path, command: str) -> dict:
    result = subprocess.run(
        ["zsh", "-lc", command],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
        env=os.environ.copy(),
    )
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    root = config_path.resolve().parents[2]
    config = read_json(config_path)
    commands = config["commands"]
    verify = run_command(root, commands["deploy_verify"])
    monitor = run_command(root, commands["monitor"])
    rolled_back = False
    rollback_result = None
    if verify["returncode"] != 0 or monitor["returncode"] != 0:
        rolled_back = bool(config["rollback_policy"].get("on_verify_failure", True) or config["rollback_policy"].get("on_monitor_failure", True))
        if rolled_back:
            rollback_result = run_command(root, commands["rollback"])
    outcome = {
        "reason": args.reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verify": verify,
        "monitor": monitor,
        "rolled_back": rolled_back,
        "rollback": rollback_result,
    }
    outcome_path = root / "docs/generated/monitor-outcome.json"
    outcome_path.parent.mkdir(parents=True, exist_ok=True)
    outcome_path.write_text(json.dumps(outcome, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
    if rollback_result and rollback_result["returncode"] != 0:
        raise SystemExit(2)
    if verify["returncode"] != 0 or monitor["returncode"] != 0:
        raise SystemExit(0 if rolled_back else 1)


if __name__ == "__main__":
    main()
"""


def app_server_bridge_py() -> str:
    return """#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Thin bridge for Codex app-server style thread lifecycle.")
    parser.add_argument("mode", choices=["start", "resume", "read", "inject"])
    parser.add_argument("--config", default="docs/generated/autonomy-config.json")
    parser.add_argument("--items-file")
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_command(root: Path, command: str, extra_env: dict[str, str] | None = None) -> dict:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        ["zsh", "-lc", command],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    payload = {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    if result.stdout.strip():
        try:
            payload["json"] = json.loads(result.stdout)
        except json.JSONDecodeError:
            pass
    return payload


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    root = config_path.resolve().parents[2]
    config = read_json(config_path)
    commands = config["commands"]
    state = config["state"]
    thread_path = root / state["thread_id_path"]
    thread_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path = root / "docs/generated/app-server-last-turn.json"
    items_file = args.items_file or ""

    if args.mode == "start":
        result = run_command(root, commands["app_server_start"], {"CODEX_THREAD_REQUEST_FILE": items_file})
        thread_id = result.get("json", {}).get("thread_id", "thread-demo")
        thread_path.write_text(json.dumps({"thread_id": thread_id}, indent=2) + "\\n", encoding="utf-8")
        metadata_path.write_text(json.dumps({"mode": "start", "result": result, "timestamp": datetime.now(timezone.utc).isoformat()}, indent=2) + "\\n", encoding="utf-8")
        raise SystemExit(result["returncode"])

    if not thread_path.exists():
        raise SystemExit("missing thread state; run start first")

    thread_id = read_json(thread_path)["thread_id"]
    env = {"CODEX_THREAD_ID": thread_id, "CODEX_THREAD_REQUEST_FILE": items_file}
    command_name = {
        "resume": "app_server_read",
        "read": "app_server_read",
        "inject": "app_server_inject",
    }[args.mode]
    result = run_command(root, commands[command_name], env)
    metadata_path.write_text(json.dumps({"mode": args.mode, "thread_id": thread_id, "result": result, "timestamp": datetime.now(timezone.utc).isoformat()}, indent=2) + "\\n", encoding="utf-8")
    raise SystemExit(result["returncode"])


if __name__ == "__main__":
    main()
"""


def app_server_schema_json() -> str:
    schema = {
        "version": 1,
        "jsonrpc": "2.0",
        "methods": {
            "thread/start": {"request": {"items_file": "string"}, "response": {"thread_id": "string"}},
            "thread/read": {"request": {"thread_id": "string"}, "response": {"messages": "array"}},
            "thread/inject_items": {"request": {"thread_id": "string", "items_file": "string"}, "response": {"accepted": "boolean"}},
        },
    }
    return json.dumps(schema, indent=2, ensure_ascii=False) + "\n"


ROOT_TEMPLATE_BUILDERS = {
    "AGENTS.md": agents_md,
    "ARCHITECTURE.md": architecture_md,
    "AUTONOMY.md": autonomy_md,
    "DESIGN.md": design_md,
    "DELIVERY.md": delivery_md,
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
            "CLAUDE.md",
            ".codex/skills/openai-harness-engineering/SKILL.md",
        }
    elif ctx.primary_agent.lower() == "cursor":
        targets.add(".cursor/rules/harness.mdc")
    elif ctx.primary_agent.lower() == "trae":
        targets.add(".trae/rules/harness.md")
    elif ctx.primary_agent.lower() in {"claude", "claude code"}:
        targets.add("CLAUDE.md")
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
        "autonomy": {
            "enabled": ctx.include_autonomy,
            "trigger_mode": "{{AUTONOMY_TRIGGER_MODE}}" if ctx.include_autonomy else "",
            "state_store": "{{AUTONOMY_STATE_STORE}}" if ctx.include_autonomy else "",
            "approval_policy": "{{AUTONOMY_APPROVAL_POLICY}}" if ctx.include_autonomy else "",
            "escalation_path": "{{AUTONOMY_ESCALATION_PATH}}" if ctx.include_autonomy else "",
        },
        "automation": {
            "enabled": ctx.automation_enabled,
            "provider": ctx.automation_provider,
            "runtime": ctx.automation_runtime if ctx.automation_enabled else "none",
            "adapter_files": ctx.automation_adapter_files,
            "trigger_modes": ["schedule", "repo_dispatch", "queue", "thread"] if ctx.automation_enabled else [],
            "checkpoint_store": "docs/generated/autonomy-state.json" if ctx.automation_enabled else "",
            "approval_policy": "{{AUTONOMY_APPROVAL_POLICY}}" if ctx.automation_enabled else "",
            "secret_refs": ["OPENAI_API_KEY", "CODEX_HOME"] if ctx.automation_enabled else [],
            "command_map": {
                "deploy": "{{DEPLOY_COMMAND}}" if ctx.automation_enabled else "",
                "verify": "{{DEPLOY_VERIFY_COMMAND}}" if ctx.automation_enabled else "",
                "rollback": "{{ROLLBACK_COMMAND}}" if ctx.automation_enabled else "",
                "monitor": "{{MONITOR_COMMAND}}" if ctx.automation_enabled else "",
                "autonomy_loop": "python3 ops/agent-runtime/queue_worker.py --task-file docs/generated/autonomy-task.json"
                if ctx.automation_enabled
                else "",
            },
        },
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
