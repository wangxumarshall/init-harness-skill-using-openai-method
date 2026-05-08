---
name: init-harness-engineering
description: 根据 OpenAI 的 Harness Engineering 理念，为一个新项目或现有项目初始化 Agent-First 的脚手架和知识库模版（宪法结构）。
---
# 🤖 Init Harness Engineering Skill
## 🌟 核心理念 (Core Beliefs)
本 Skill 基于 OpenAI 团队在其《Harness engineering: leveraging Codex in an agent-first world》文章中提出的 **Harness Engineering**（线束工程）理念。
核心公式：**Agent = Model + Harness**
核心哲学：**"Humans steer. Agents execute."**（人类掌舵，Agent执行。）
为了实现从“人写代码”到“人设计Agent环境”的转变，项目仓库（Repository）必须从一开始就针对 **Agent 可读性 (Agent Legibility)** 进行优化。
## 📋 你的任务 (Your Task)
在被调用执行本 Skill 时，你需要作为一个架构师，根据用户提供的项目描述、计划 (Plan) 或前置产品规格，初始化一套完整的、具有强制约束力的 **Agent 宪法与知识结构 (Harness Framework)**。如果具体的项目名称、规格说明等信息未知，请使用 `{{PROJECT_NAME}}`, `{{SPEC}}`, `{{CONTENT}}` 等占位符。
### 第一步：信息收集与交互 (交互式对话)
当用户调用本 Skill 时，**不要直接开始生成文件**（除非用户在初始命令中已经提供了所有必要信息）。
你需要主动向用户发起对话，以自然、交互的方式询问以下核心信息：
1. **项目名称 (`{{PROJECT_NAME}}`)**
2. **项目描述 (`{{PROJECT_DESC}}`)**
3. **核心技术栈 (`{{TECH_STACK}}`)**
4. **核心业务领域 (`{{CORE_DOMAINS}}`)**
5. **主要使用的 Coding Agent (`{{CODING_AGENT}}`，如 Cursor, Claude Code, OpenCode, Trae, Gemini, Codex 等)**
**话术参考**：“您好！为了生成最贴合您项目的 Harness 宪法结构，我们需要先明确几个关键点。请问您的【项目名称】是什么？【核心技术栈】打算用什么？另外，您主要使用哪款【Coding Agent】（例如 Cursor、Claude Code、Gemini、Trae 等）来进行辅助开发？”
请等待用户的回复。只有当收集齐基本信息，或者用户明确要求“跳过，直接使用占位符”时，才可以进入下一步生成文件。
### 第二步：生成知识库目录结构
你需要使用 `run_command` (mkdir) 或直接依靠写入文件来在当前项目根目录创建以下“单一真相来源 (System of Record)”的目录结构：
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
### 第三步：写入 Harness 核心宪法文件 (The Constitution)
逐一生成以下文件。注意体现**渐进式披露 (Progressive disclosure)** 理念：避免在一个文件里堆砌所有规则。
#### 1. `AGENTS.md` (入口与地图)
> **注意**：这不是一个巨大的操作手册，而是一个索引表（Table of Contents）。避免它腐烂。
**必须包含的内容（可扩充）**：
```markdown
# {{PROJECT_NAME}} Agent Map
Welcome to {{PROJECT_NAME}}. This repository is agent-generated and agent-maintained.
This file is the table of contents for Agent operations. **DO NOT put detailed instructions here.**
## 🗺️ System of Record (知识库地图)
- [Architecture & Layers](./ARCHITECTURE.md)
- [Design Principles](./DESIGN.md)
- [Product Sense](./PRODUCT_SENSE.md)
- [Quality & Linting](./QUALITY_SCORE.md)
## 📁 核心目录 (Core Directories)
- `docs/design-docs/`: 核心架构设计与核心理念 (Core Beliefs).
- `docs/exec-plans/`: 正在执行的执行计划 (Execution Plans) 与技术债务追踪.
- `docs/product-specs/`: 需求与产品规格.
```
#### 2. `ARCHITECTURE.md` (架构与边界约束)
**必须包含的内容**：
```markdown
# 架构原则与边界约束
## 严格的分层架构 (Layered Domain Architecture)
在 `{{PROJECT_NAME}}` 中，任何业务领域必须遵循严格的**单向依赖**：
`Types -> Config -> Repo -> Service -> Runtime -> UI`
跨领域关注点（如 Auth, Telemetry, Feature Flags）只能通过单一的显式接口（Providers）注入。不允许任何偏离此规则的依赖。
## 机械强制 (Mechanical Enforcement)
所有的架构边界和口味（Taste）必须最终转化为 CI 中的 Linters 或结构测试。如果文档中规定了某种格式，它必须在代码中被自动校验。
**极其重要**：自定义 Linters 的错误输出必须经过设计，将修复指导（Remediation instructions）直接注入到报错信息中，以便 `{{CODING_AGENT}}` 能自动看懂报错并修复。
## 可读性优化 (Agent Legibility)
一切架构决策优先考虑 Agent 能够直接在仓库内阅读、验证和修改。
- 倾向于能在代码库内完全消化的依赖。
- 拒绝需要隐式“人类知识”（如 Slack 讨论、口头约定）的设计。不在仓库中的知识，对 Agent 就是不存在的。
```
#### 3. `docs/design-docs/core-beliefs.md` (核心理念)
**必须包含的内容**：
```markdown
# Core Beliefs (Agent-First 团队信条)
1. **No Manually-Written Code**: 尽量保持 0 行人类手写代码。人类通过设计环境、提供上下文和建立反馈循环来杠杆化 `{{CODING_AGENT}}` (无论您使用的是 Cursor, Claude Code, OpenCode, Trae, 还是 Gemini) 的能力。这套宪法结构对所有主流 Agent 通用。
2. **Repository is the Source of Truth**: 仓库是唯一的真相。不在仓库中的知识，对 `{{CODING_AGENT}}` 就是不存在的。把沟通群里的决策、架构意图全部转化为 Markdown 写入仓库。
3. **Golden Principles & GC**: 烂代码需要及时被背景任务清理（Garbage Collection）。在系统边界处必须强制校验数据结构（Parse shapes at the boundary），不允许 YOLO 风格的瞎猜探测，必须使用显式校验（如 Zod）。在实现功能时，**强制优先使用**共享的 Utility Packages，而不是让 Agent 每次都手写 Helper，以保证一致性。
4. **Fast Merges & Agent Review**: 高吞吐量下，人类 QA 会成为瓶颈。仓库采用极简的非阻塞合并策略（Minimal blocking merge gates）和短生命周期的 PR。允许通过后续的补充运行来修复轻微缺陷，推动 Agent 间的相互验证循环。
```
#### 4. 生成其他核心宪法文件 (补充骨架内容)
你还需要在根目录生成以下 Markdown 文件的骨架（带 `{{占位符}}`）：
- `DESIGN.md`: 涵盖具体的技术栈 `{{TECH_STACK}}` 的设计准则。
- `FRONTEND.md` / `BACKEND.md`: 前端/后端具体的代码规范。
- `PLANS.md`: 定义如何使用 `docs/exec-plans/` 进行任务分解，强调短生命周期的 PR。
- `PRODUCT_SENSE.md`: 记录产品目标与 `{{CORE_DOMAINS}}` 核心用户旅程。
- `QUALITY_SCORE.md`: 定义如何给各模块的质量、测试覆盖率打分。
- `RELIABILITY.md`: 定义本地临时环境（Ephemeral Worktrees）和 Observability（日志、指标、Chrome DevTools）的标准，使 `{{CODING_AGENT}}` 能够在隔离环境中运行实例、重现 Bug 并在没有人类干预的情况下完成验证。
- `SECURITY.md`: 安全防护底线。
### 第四步：输出执行总结
当所有模版生成完毕后，向用户输出总结：
1. 列出创建的文档结构。
2. 说明 Harness 已经初始化完成。
3. 提示用户可以通过其他规划类的 Agent（如 `planning-with-files`）去填充 `docs/exec-plans/`，从而开始自动化迭代。
## 🚨 核心纪律 (Critical Rules for you)
1. **绝不** 在 `AGENTS.md` 里塞满具体的业务指令。
2. **必须强调** 架构的机械强制性（Linters/Tests > 纯文本指导）。
3. 生成的文档建议以 Markdown 格式直接写入用户当前的工作目录。
4. 语言要求：你生成的文档模板中可以采用中英文结合（标题英文，关键概念带英文），但针对用户的输出说明必须是**中文**。
