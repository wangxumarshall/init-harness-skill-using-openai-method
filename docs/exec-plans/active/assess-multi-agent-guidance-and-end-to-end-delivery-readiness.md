# Assess multi-agent guidance and end-to-end delivery readiness

- Status: active
- Owner/agent: Codex
- Started: 2026-05-11
- Last updated: 2026-05-11
- Trajectory role: exec-plan index

## User Request

研究当前 openai-harness-engineering 项目是否已经实现 OpenAI / Anthropic / Karpathy 风格的 agents guidance，以及长久持续运行直到 spec 实现、测试、验证、部署上线的目标；若有差距，制定计划并实现关键缺口。

## Goal

给出逐项目标的证据化达成表，并通过最小代码改动补齐至少一个 Anthropic 兼容缺口和一个端到端交付缺口，且仓库验证通过。

## Non-Goals

- 发明不存在的 Karpathy 官方规范
- 把当前 skill 直接扩展成部署平台或托管运行时

## Context

- `README.md` - 当前对外承诺、能力边界与引用来源
- `skills/openai-harness-engineering/SKILL.md` - skill 目标与 operate/audit 工作流
- `skills/openai-harness-engineering/scripts/init_harness.py` - 生成器与 adapter 实现
- `skills/openai-harness-engineering/scripts/audit_harness.py` - 结构/工作流验收标准
- `skills/openai-harness-engineering/scripts/check_harness_drift.py` - 长期漂移控制
- `evals/run_evals.py`, `evals/grade_evals.py`, `evals/prompts.csv` - 自动化回归证据
- OpenAI / Anthropic 官方文档 - 对照 AGENTS.md、CLAUDE.md、长程任务与 subagents guidance
- `https://github.com/forrestchang/andrej-karpathy-skills/.../karpathy-guidelines/SKILL.md` - 用户指定的 Karpathy 风格 guideline 参照

## Context Read

- `AGENTS.md` - 确认本仓库要求以证据为先，并保留非 trivial 工作轨迹
- `PLANS.md` - 确认需要把本次评估与改动记录为执行计划
- `QUALITY_SCORE.md` - 确认最低验证命令
- `RELIABILITY.md` - 确认维护循环当前尚未显式覆盖部署生命周期
- `README.md` - 确认当前已承诺持久计划、审计、漂移检查与 eval
- `skills/openai-harness-engineering/SKILL.md` - 确认这是 harness dogfooding 任务
- `skills/openai-harness-engineering/scripts/init_harness.py` - 确认已有 OpenAI/Codex/Cursor/Claude adapter 逻辑，但 Claude 入口是 slash command 文件
- `skills/openai-harness-engineering/scripts/audit_harness.py` - 确认当前未要求 deploy lifecycle 文档
- `evals/run_evals.py` 与 `evals/grade_evals.py` - 确认现有 eval 只验证命令是否运行，不验证关键生成文件
- OpenAI Harness Engineering / Codex 长程任务官方文档 - 用于判断当前项目与 OpenAI guidance 的对齐度
- Anthropic Claude Code memory / subagents 官方文档 - 用于判断当前项目与 Anthropic guidance 的对齐度
- 用户提供的 Karpathy guideline skill - 内容聚焦假设显式化、简单性、手术式改动、目标驱动验证
- 对抗性空仓初始化检查 - 确认当前 skill 原样生成后仍需人工替换占位符与接入真实命令

## Plan

1. 盘点当前项目对 OpenAI、Anthropic、Karpathy 与长程交付目标的已实现能力和缺口。
2. 以最小改动补齐一个 Anthropic 兼容缺口和一个端到端交付缺口。
3. 运行验证、记录证据，并给出逐项目标达成表与后续计划。

## Actions Taken

- 阅读仓库 map、skill、生成器、审计器、漂移检查与 eval 文件，确认现状与验收口径。 - `AGENTS.md`, `PLANS.md`, `QUALITY_SCORE.md`, `RELIABILITY.md`, `README.md`, `skills/openai-harness-engineering/SKILL.md`, `skills/openai-harness-engineering/scripts/*`, `evals/*`
- 运行基线验证，确认当前 self-harness audit/drift/evals 可用。 - 仓库根目录验证命令
- 对照 OpenAI / Anthropic 官方资料做差距分析，确认 Anthropic 入口文件与 deploy lifecycle 是最明确缺口。 - 外部官方文档与本地代码
- 读取用户提供的 Karpathy guideline skill，确认它偏行为准则，不是 unattended runtime 设计。 - GitHub 指定文件
- 更新生成器，为 standard/full profile 增加 `DELIVERY.md`，并在 ops surface 增加 `docs/runbooks/deployment.md`。 - `skills/openai-harness-engineering/scripts/init_harness.py`
- 将 Claude adapter 从 `.claude/commands/harness.md` 调整为 `CLAUDE.md`。 - `skills/openai-harness-engineering/scripts/init_harness.py`
- 更新审计与文档说明，并扩展 eval 以断言关键生成文件存在。 - `skills/openai-harness-engineering/scripts/audit_harness.py`, `README.md`, `skills/openai-harness-engineering/references/generated_files.md`, `evals/*`
- 运行完整验证并记录结果。 - `docs/validation/multi-agent-delivery-readiness-2026-05-11.md`
- 在空白测试仓库上执行 `init_harness -> audit_harness`，记录 12 个 workflow failures，作为“不能无人干预自举”的反证。 - `/tmp/ohe-adversarial-check`

## Decisions

- 把 Anthropic 兼容入口落在仓库根 `CLAUDE.md`，不再使用 `.claude/commands/harness.md` 作为主入口。 - Anthropic 官方 memory 机制以 `CLAUDE.md` 为项目级指令入口，slash command 文件不是同一层级。
- 把 spec -> implement -> test -> verify -> deploy 提升为标准/完整 profile 的一等文档 `DELIVERY.md`，并补 deployment runbook。 - 用户目标明确要求端到端交付闭环，而当前 harness 只覆盖到验证/维护。
- 在 eval 中加入文件存在性断言。 - 仅看命令返回码不足以证明新能力真实生成。
- 不把 Karpathy 目标编码为仓库硬规则，但把其行为准则用于评估。 - 用户已给出具体来源；其内容是工程行为规范，不是 provider-level runtime capability 规范。

## Decision Links

- ADR: none
- Design doc/spec: none

## Validation

- [x] `python3 -m py_compile skills/openai-harness-engineering/scripts/*.py evals/*.py` - 脚本与 eval 入口语法正确
- [x] `python3 skills/openai-harness-engineering/scripts/audit_harness.py --target . --mode full` - self-harness 仍通过完整审计
- [x] `python3 skills/openai-harness-engineering/scripts/check_harness_drift.py --target .` - 漂移检查通过
- [x] `python3 evals/run_evals.py` - 生成包含 Claude adapter 与 delivery 文件断言的最新 artifacts
- [x] `python3 evals/grade_evals.py` - 所有 eval 场景通过确定性评分
- [x] `python3 skills/openai-harness-engineering/scripts/init_harness.py --target "$TMPDIR" --project-name Demo --project-description Demo --tech-stack Python --domains Harness --primary-agent "Claude Code" --profile standard` - spot check 生成 `CLAUDE.md`、`DELIVERY.md`、`docs/runbooks/deployment.md`
- [x] `python3 skills/openai-harness-engineering/scripts/init_harness.py --target /tmp/ohe-adversarial-check ... --profile standard && python3 skills/openai-harness-engineering/scripts/audit_harness.py --target /tmp/ohe-adversarial-check --mode full` - 原样生成后出现 12 个 workflow failures，证明当前 skill 不是无人值守自举系统

## Validation Evidence

- Validation log: `docs/validation/multi-agent-delivery-readiness-2026-05-11.md`
- Summary: 关键缺口已补齐；self-harness 审计、漂移检查与扩展后的 eval 全通过；手工 spot check 证明 Claude 与 delivery/deploy 产物会被实际生成。同时，对抗性空仓检查显示该 skill 原样输出仍依赖人工接入真实命令，不能宣称可无人干预自举完成复杂任务。

## Incident Links

- Incident: none

## Learnings

- 当前项目更接近“agent 工作系统脚手架”，不是“自动部署平台”；要评估目标达成，必须把脚手架能力与运行时能力分开。
- Anthropic 兼容不能只看品牌名，要看入口文件是否和官方机制一致。
- 仅有命令执行型 eval 不足以覆盖脚手架产物质量，至少还需要文件级断言。
- Karpathy 风格 guideline 主要提升工程判断质量，但单靠这些行为规则不能补出调度、权限、外部事件、恢复执行等无人值守能力。

## Progress Log

- 2026-05-11: Plan created.
- 2026-05-11: 完成差距分析、关键补强与验证记录。

## Open Questions

- 是否需要继续把 deployment lifecycle 纳入 `audit_harness.py` 的工作流强校验，而不只是生成与 eval 断言。
- 是否需要为 OpenAI/Codex 再增加面向长程任务的更细粒度运行手册，例如队列、回滚审批、自动唤醒。

## Follow-Ups

- 为 deployment runbook 增加更具体的 release checklist 模板与环境矩阵。
- 若后续找到 Karpathy 本人的稳定一手规范，再评估是否把其原则编码进生成器或 eval。
- 可增加一个更重的 fixture，验证真实前后端项目中的 deploy verification 和 rollback 占位接入体验。

## Closure Notes

- Outcome: 已完成评估并实现两项关键补强：Anthropic 兼容入口改为 `CLAUDE.md`；standard/full harness 新增 delivery/deployment 一等文档与回归断言。
- Changed files/modules: `skills/openai-harness-engineering/scripts/init_harness.py`, `skills/openai-harness-engineering/scripts/audit_harness.py`, `README.md`, `skills/openai-harness-engineering/references/generated_files.md`, `evals/prompts.csv`, `evals/run_evals.py`, `evals/grade_evals.py`, `docs/validation/multi-agent-delivery-readiness-2026-05-11.md`
- Residual risk: 即使采用用户给出的 Karpathy guideline，这个 skill 仍缺少后台任务调度、外部事件注入、自动恢复执行、真实部署集成与审批策略，因此仍不直接负责真实应用的无人值守持续运行。

## Next Agent Handoff

- Current state: 代码与验证已完成，可直接用于汇报当前目标达成情况与剩余差距。
- Next recommended action: 若目标升级为“无人干预持续运行”，下一步应设计 automation/runtime layer，而不是继续只加文档：任务队列、事件触发、审批策略、重试/恢复、deploy adapter、post-deploy monitors。
- Blockers: none
