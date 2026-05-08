# Init Harness Engineering Skill 🤖

A unified, multi-agent skill that brings the **OpenAI Harness Engineering** architecture and **Andrej Karpathy's LLM Guidelines** directly into your coding environment. This skill automatically generates a machine-readable "Constitution" for your repository, making your codebase highly legible for AI agents and enforcing strict developmental discipline.

> **Read the origin of these concepts:** 
> [Harness engineering: leveraging Codex in an agent-first world | OpenAI](https://openai.com/index/harness-engineering/)

---

## 📖 The Philosophy

As AI coding agents (Claude Code, Cursor, Trae, Gemini, OpenCode, etc.) become more autonomous, the primary bottleneck for developers shifts from *writing code* to *managing the AI's environment*. 

### Core Equation: Agent = Model + Harness

Based on OpenAI's findings, when humans aim for **0 lines of manually-written code**, their job becomes designing environments, specifying intent, and building feedback loops. Without a strict Harness, agents tend to overcomplicate things, make dangerous assumptions, hallucinate data boundaries, and silently rewrite working code.

This skill solves that by generating an **Agent Constitution**—a set of foundational markdown files that act as the supreme law of the repository.

---

## ✨ Features

When invoked, the `init-harness-engineering` skill acts conversationally. It asks for your project details (Name, Tech Stack, Primary Agent) and then generates the following "System of Record":

### 1. Progressive Disclosure (`AGENTS.md`)
Instead of a monolithic prompt file that rots over time, it generates a lightweight `AGENTS.md` that serves purely as a Table of Contents. It directs your AI to deep-dive into specific `docs/` folders for context, preventing prompt overload.

### 2. Mechanical Enforcement (`ARCHITECTURE.md`)
Enforces strict unidirectional domain layering (e.g., `Types -> Config -> Repo -> Service -> Runtime -> UI`). It mandates that all architectural boundaries be checked by CI Linters, and critically requires that custom linters **inject remediation instructions** directly into their error output so the agent can self-correct.

### 3. Agent-First Core Beliefs (`docs/design-docs/core-beliefs.md`)
- **No Manual Code**: Humans steer, agents execute.
- **Repository is Truth**: If knowledge isn't in the repo (e.g., Slack threads), it doesn't exist for the agent.
- **Parse at the Boundary**: Forbids YOLO-style guessing; forces the agent to use explicit validation (like Zod).
- **Anti-Entropy**: Forces the agent to use shared Utility Packages rather than hand-rolling ad-hoc helpers everywhere.

### 4. Andrej Karpathy's LLM Guidelines (in `DESIGN.md`)
Seamlessly integrates the 4 core rules for LLM coding behavior:
1. **Think Before Coding**: Surface assumptions, don't hide confusion.
2. **Simplicity First**: Minimum code to solve the problem. Rewrite 200 lines to 50 if possible.
3. **Surgical Changes**: Touch only what you must. Don't "improve" adjacent code formatting.
4. **Goal-Driven Execution**: Define verifiable success criteria (e.g., writing tests first) and loop until verified.

---

## 🚀 Installation & Usage

This skill is designed to be cross-platform and natively compatible with the most popular coding agents.

### Option A: Claude Code (Plugin Marketplace)
In Claude Code, add the plugin marketplace and install:
```bash
/plugin marketplace add wangxumarshall/init-harness-skill-using-openai-method
/plugin install init-harness-skill-using-openai-method@harness-engineering-skills
```
**Usage**: Simply type: *"Run init-harness-engineering"* in your Claude Code prompt. The agent will ask you for your project details and generate the framework.

### Option B: Cursor Users (MDC Rules)
This repository contains a pre-committed Cursor rule. You can install it directly into your project:
```bash
mkdir -p .cursor/rules
curl -o .cursor/rules/init-harness-engineering.mdc https://raw.githubusercontent.com/wangxumarshall/init-harness-skill-using-openai-method/main/.cursor/rules/init-harness-engineering.mdc
```
**Usage**: Just ask Cursor (Cmd+L or Cmd+K) to: *"Initialize the harness scaffolding for this project."* Cursor will automatically read the `.mdc` file and trigger the interactive process.

### Option C: Manual Setup (Trae, Gemini, OpenCode, etc.)
You can copy the raw skill prompt and paste it into any agent's context:
1. Copy the contents of [`skills/init-harness-engineering/SKILL.md`](./skills/init-harness-engineering/SKILL.md).
2. Paste it into your agent's system prompt or chat interface.

---

## 📜 License
MIT License. Feel free to fork, modify, and build the ultimate harness for your own AI agents!
