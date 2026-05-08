# Harness Engineering Skills

A unified skill set that brings **OpenAI's Harness Engineering** architecture and **Andrej Karpathy's LLM Guidelines** into your coding environment. This makes your repo "Agent-First", highly legible for AI, and strongly disciplined.

## The Problem
As AI coding agents (Claude Code, Cursor, Trae, etc.) become more capable, the bottleneck shifts from writing code to *managing the AI's environment*. Agents often overcomplicate things, make wrong assumptions, hallucinate data shapes, or break architectural boundaries when they lack a strict, machine-readable constitution.

## The Solution
This plugin provides the `init-harness-engineering` skill. When invoked, it interactively creates a complete "Harness Constitution" for your project.

### What it generates:
1. **Agent Map (`AGENTS.md`)**: A lightweight table of contents pointing to your single sources of truth.
2. **Architecture Constraints (`ARCHITECTURE.md`)**: Enforces strict unidirectional dependencies and requires all linters to inject *remediation instructions* for agents.
3. **Core Beliefs (`docs/design-docs/core-beliefs.md`)**: Mandates 0 manual code, shared utilities over ad-hoc helpers, and explicit boundary parsing (e.g., using Zod instead of YOLO-guessing).
4. **Karpathy Guidelines (in `DESIGN.md`)**: Injects Andrej Karpathy's 4 core rules:
   - **Think Before Coding**: Surface assumptions.
   - **Simplicity First**: Minimum code, rewrite 200 lines to 50.
   - **Surgical Changes**: Touch only what you must.
   - **Goal-Driven Execution**: Define verifiable success criteria.

## Installation

### Option A: Claude Code Plugin (Recommended)
In Claude Code, first add the plugin marketplace:
```bash
/plugin marketplace add wangxumarshall/init-harness-skill-using-openai-method
```

Then install the plugin:
```bash
/plugin install init-harness-skill-using-openai-method@harness-engineering-skills
```
Once installed, you can simply say: "Run init-harness-engineering" and Claude will conversationally guide you to set up your project.

### Option B: For Cursor Users
This repository contains a pre-committed Cursor rule. Copy it to your project:
```bash
mkdir -p .cursor/rules
curl -o .cursor/rules/init-harness-engineering.mdc https://raw.githubusercontent.com/wangxumarshall/init-harness-skill-using-openai-method/main/.cursor/rules/init-harness-engineering.mdc
```

### Option C: Manual Setup (Any Agent)
Copy the `SKILL.md` file from `skills/init-harness-engineering/SKILL.md` and paste it into your prompt or your agent's system instructions.

## License
MIT
