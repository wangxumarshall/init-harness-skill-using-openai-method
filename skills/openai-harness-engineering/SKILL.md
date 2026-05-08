---
name: openai-harness-engineering
description: Initializes an Agent-First scaffolding and knowledge base template (Constitution Framework) for a new or existing project, based on OpenAI's Harness Engineering concepts and Andrej Karpathy's LLM Guidelines.
license: MIT
---

# 🤖 OpenAI Harness Engineering Skill

## Core Beliefs

This Skill is based on the **Harness Engineering** concept proposed by the OpenAI team in their article "Harness engineering: leveraging Codex in an agent-first world", fused with **Andrej Karpathy's LLM Coding Guidelines**.

Core Equation: **Agent = Model + Harness**
Core Philosophy: **"Humans steer. Agents execute."**

To transition from "humans writing code" to "humans designing agent environments", the project repository must be optimized for **Agent Legibility** from the very beginning. Furthermore, the generated scaffolding deeply integrates Karpathy's wisdom to prevent the coding agent from overcomplicating things, making wrong assumptions, or performing unsolicited refactoring.

## 📋 Your Task

When invoked, act as an Architect to initialize a complete, strictly enforced **Agent Constitution and Knowledge Structure (Harness Framework)** based on the user's project description, plans, or product specs. If specific details are missing, use placeholders like `{{PROJECT_NAME}}`, `{{SPEC}}`, `{{CONTENT}}`, etc.

### Step 1: Information Gathering & Interaction (Conversational)
When the user invokes this Skill, **DO NOT start generating files immediately** (unless all necessary information was provided in the initial command).
You must proactively initiate a conversation, asking for the following core information in a natural, interactive way:

1. **Project Name (`{{PROJECT_NAME}}`)**
2. **Project Description (`{{PROJECT_DESC}}`)**
3. **Core Tech Stack (`{{TECH_STACK}}`)**
4. **Core Business Domains (`{{CORE_DOMAINS}}`)**
5. **Primary Coding Agent (`{{CODING_AGENT}}`, e.g., Cursor, Claude Code, OpenCode, Trae, Gemini, Codex, etc.)**

**Prompt Example**: "Hello! To generate the best Harness Constitution for your project, we need to clarify a few key points. What is your [Project Name]? What [Tech Stack] do you plan to use? Also, which [Coding Agent] (e.g., Cursor, Claude Code, Gemini, Trae) will you primarily use to assist in development?"

Wait for the user's response. Only proceed to generate files when you have gathered this basic info, or if the user explicitly says "skip, just use placeholders."

### Step 2: Generate Knowledge Base Directory Structure
Create the following "System of Record" directory structure in the project root using `run_command` (mkdir) or by writing files directly:
```text
docs/
├── design-docs/
├── exec-plans/
│   ├── active/
│   └── completed/
├── generated/
├── product-specs/
└── references/
```

### Step 3: Write Harness Core Constitution Files

Generate the following files one by one. Embody the **Progressive Disclosure** philosophy: avoid dumping all rules into a single file.

#### 1. `AGENTS.md` (Entry Point & Map)
> **Note**: This is not a giant instruction manual; it's a Table of Contents. Prevent it from rotting.
**Must include (can be expanded)**:
```markdown
# {{PROJECT_NAME}} Agent Map

Welcome to {{PROJECT_NAME}}. This repository is agent-generated and agent-maintained.
This file is the table of contents for Agent operations. **DO NOT put detailed instructions here.**

## System of Record
- [Architecture & Layers](./ARCHITECTURE.md)
- [Design Principles](./DESIGN.md)
- [Product Sense](./PRODUCT_SENSE.md)
- [Quality & Linting](./QUALITY_SCORE.md)

## Core Directories
- `docs/design-docs/`: Core architecture design and Core Beliefs.
- `docs/exec-plans/`: Active execution plans and Tech Debt Tracker.
- `docs/product-specs/`: Requirements and product specs.
```

#### 2. `ARCHITECTURE.md` (Architecture & Boundaries)
**Must include**:
```markdown
# Architectural Principles and Boundary Constraints

## Strict Layered Domain Architecture
In `{{PROJECT_NAME}}`, any business domain must follow a strict **unidirectional dependency**:
`Types -> Config -> Repo -> Service -> Runtime -> UI`

Cross-cutting concerns (e.g., Auth, Telemetry, Feature Flags) must only be injected through a single explicit interface (Providers). Deviations from this rule are prohibited.

## Mechanical Enforcement
All architectural boundaries and code taste preferences must ultimately be translated into CI Linters or structural tests. If a format is specified in docs, it must be automatically validated in code.
**CRITICAL**: Custom Linters must be designed to inject **remediation instructions** directly into their error output. This allows `{{CODING_AGENT}}` to understand the error context and fix it automatically.

## Agent Legibility
All architectural decisions prioritize the Agent's ability to read, validate, and modify code directly within the repo.
- Favor dependencies that can be fully internalized and digested within the codebase.
- Reject designs that rely on implicit "human knowledge" (e.g., Slack threads, verbal agreements). Knowledge not in the repo effectively does not exist for the Agent.
```

#### 3. `docs/design-docs/core-beliefs.md` (Core Beliefs)
**Must include**:
```markdown
# Core Beliefs (Agent-First Team Philosophy)

1. **No Manually-Written Code**: Strive for 0 lines of human-written code. Humans leverage the capabilities of `{{CODING_AGENT}}` (whether you use Cursor, Claude Code, OpenCode, Trae, or Gemini) by designing environments, providing context, and building feedback loops. This constitution applies to all mainstream agents.
2. **Repository is the Source of Truth**: The repo is the sole truth. Knowledge outside the repo does not exist to `{{CODING_AGENT}}`. Convert all chat decisions and architectural intent into Markdown and commit them.
3. **Golden Principles & GC**: Bad code must be promptly cleaned up by background agent tasks (Garbage Collection). You must **Parse shapes at the boundary**—YOLO-style guessing is forbidden; use explicit validation (e.g., Zod). **Mandatory**: Prioritize using shared Utility Packages rather than having the Agent hand-roll helpers each time, to ensure consistency.
4. **Fast Merges & Agent Review**: At high throughput, human QA is a bottleneck. The repo uses minimal blocking merge gates and short-lived PRs. Minor flaws can be fixed in follow-up PRs, driving a continuous agent-to-agent verification loop.
```

#### 4. Generate Other Core Constitution Skeletons
Generate skeleton Markdown files (with `{{PLACEHOLDERS}}`) for the following in the root directory:
- `DESIGN.md`: Design guidelines for the specific `{{TECH_STACK}}`. **MUST INCLUDE** the following 4 core Andrej Karpathy guidelines for LLM Coding behavior:
    - **1. Think Before Coding**: Don't assume. Surface tradeoffs. State assumptions explicitly. If unclear, stop and ask.
    - **2. Simplicity First**: Minimum code that solves the problem. No speculative features or abstractions. Rewrite 200 lines to 50 if possible.
    - **3. Surgical Changes**: Touch only what you must. Clean up your own mess. Don't "improve" adjacent code or refactor unbroken things.
    - **4. Goal-Driven Execution**: Define success criteria. Transform tasks into verifiable goals and loop until verified.
- `FRONTEND.md` / `BACKEND.md`: Frontend/Backend-specific coding standards.
- `PLANS.md`: Defines how to use `docs/exec-plans/` for task breakdown, emphasizing short-lived PRs.
- `PRODUCT_SENSE.md`: Records product goals and core user journeys for `{{CORE_DOMAINS}}`.
- `QUALITY_SCORE.md`: Defines how to grade module quality and test coverage.
- `RELIABILITY.md`: Defines standards for local Ephemeral Worktrees and Observability (logs, metrics, Chrome DevTools), enabling `{{CODING_AGENT}}` to run instances in isolated environments, reproduce bugs, and complete validation without human intervention.
- `SECURITY.md`: Baseline security requirements.

### Step 4: Output Execution Summary
Once all templates are generated, output a summary to the user:
1. List the created document structure.
2. Confirm that Harness initialization is complete.
3. Advise the user to use other planning agents (e.g., `planning-with-files`) to populate `docs/exec-plans/` and start automated iterations.

## Critical Rules for You
1. **NEVER** stuff `AGENTS.md` with detailed business instructions.
2. **MUST EMPHASIZE** mechanical enforcement of architecture (Linters/Tests > Plain text instructions).
3. Write generated documents in Markdown format directly to the user's current working directory.
4. Language Requirement: ALL interactions with the user and the contents of the generated templates MUST be in **English**.
