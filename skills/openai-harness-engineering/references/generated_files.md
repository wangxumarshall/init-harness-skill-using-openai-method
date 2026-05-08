# Generated Harness Files

Use this reference when deciding what the initializer creates or updates.

## Root Files

- `AGENTS.md`: Short entry point and table of contents. It should stay small.
- `ARCHITECTURE.md`: Layering, module boundaries, dependency rules, and enforcement strategy.
- `DESIGN.md`: Coding taste, simplicity rules, design constraints, and agent behavior.
- `FRONTEND.md`: Frontend-specific standards, accessibility, browser testing, and UI verification.
- `BACKEND.md`: Backend-specific standards, API contracts, validation, persistence, and jobs.
- `PLANS.md`: Planning workflow for active work, completed plans, and session continuity.
- `PRODUCT_SENSE.md`: Product goals, user journeys, domains, non-goals, and decision log links.
- `QUALITY_SCORE.md`: Quality rubric, test expectations, coverage standards, and review checks.
- `RELIABILITY.md`: Local environments, observability, debugging, health checks, and incident records.
- `SECURITY.md`: Baseline security requirements, secrets handling, auth, data protection, and dependencies.

## Docs Tree

```text
docs/
├── adr/
├── design-docs/
├── exec-plans/
│   ├── active/
│   └── completed/
├── generated/
├── incidents/
├── product-specs/
├── references/
├── runbooks/
└── validation/
```

## Optional Agent Adapter Files

Create only when requested or useful for the user's primary agent:

- `.cursor/rules/harness.mdc`
- `.trae/rules/harness.md`
- `.codex/skills/openai-harness-engineering/SKILL.md`
- `.claude/commands/harness.md`

Adapters should point back to the source docs. Do not duplicate the full constitution.

## File Ownership Rules

- Preserve existing files by default. If a generated file already exists, append missing managed sections only when clearly safe.
- Do not overwrite product facts, architecture choices, or prior decisions unless the user explicitly asks for a refresh.
- Generated files should include placeholders for unknown facts instead of invented details.
- Every "must" should name a verification mechanism, or explicitly say that enforcement is pending.
