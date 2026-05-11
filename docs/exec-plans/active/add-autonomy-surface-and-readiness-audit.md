# Add autonomy surface and readiness audit

- Status: active
- Owner/agent: Codex
- Started: 2026-05-11
- Last updated: 2026-05-11
- Trajectory role: exec-plan index

## User Request

改进 `openai-harness-engineering` skill，使其能够为目标项目提供“长久持续运行、无人干预、独立完成复杂任务”所需的 autonomy harness。

## Goal

生成器可输出 autonomy surface，仓库可用确定性脚本审计 unattended readiness，并有 eval 覆盖该能力。

## Non-Goals

- 把本仓库直接变成一个完整的部署平台或后台任务系统
- 跳过目标仓库对真实 deploy/monitor/approval 命令的接入

## Context

- `skills/openai-harness-engineering/scripts/init_harness.py` - 生成器主入口
- `skills/openai-harness-engineering/scripts/audit_harness.py` - 当前通用审计能力
- `skills/openai-harness-engineering/scripts/check_harness_drift.py` - 漂移扫描
- `README.md`, `skills/openai-harness-engineering/SKILL.md`, `references/generated_files.md` - 对外能力说明
- `evals/prompts.csv`, `evals/run_evals.py`, `evals/grade_evals.py` - 回归验证链
- OpenAI harness engineering 文章与用户提供的 Karpathy guideline - 目标能力与工程准则参考

## Context Read

- `task_plan.md`, `findings.md`, `progress.md` - 当前多阶段实现计划与发现
- `README.md` - 当前功能说明尚未覆盖 autonomy layer
- `skills/openai-harness-engineering/SKILL.md` - 需要把 autonomy 纳入初始化/审计工作流
- `skills/openai-harness-engineering/scripts/init_harness.py` - 适合扩展 surface、manifest 与 required commands
- `evals/run_evals.py` 与 `grade_evals.py` - 可扩展成 autonomy fixture 回归

## Plan

1. 设计 autonomy surface、manifest 字段与 opt-in flag。
2. 实现生成器、readiness checker、drift/audit 对应更新。
3. 扩展 eval 和 dogfood 证据，验证 autonomy capability。

## Actions Taken

- 新增 `--include-autonomy` flag，并让 autonomy surface 自动带上所需 ops 支撑。 - `skills/openai-harness-engineering/scripts/init_harness.py`
- 为启用 autonomy 的目标仓库生成 `AUTONOMY.md`、`docs/runbooks/autonomous-operations.md`、`docs/validation/autonomy-drill-template.md`。 - `skills/openai-harness-engineering/scripts/init_harness.py`
- 在 manifest 中加入 autonomy 元数据与 deploy/verify/rollback/monitor/autonomy-loop required commands。 - `skills/openai-harness-engineering/scripts/init_harness.py`
- 新增 `check_autonomy_readiness.py`，用于 unattended readiness 的强校验。 - `skills/openai-harness-engineering/scripts/check_autonomy_readiness.py`
- 更新通用 audit、drift、README、skill 文档与 generated-files reference。 - `skills/openai-harness-engineering/scripts/audit_harness.py`, `skills/openai-harness-engineering/scripts/check_harness_drift.py`, `README.md`, `skills/openai-harness-engineering/SKILL.md`, `skills/openai-harness-engineering/references/generated_files.md`
- 扩展 eval，加入 autonomy surface 场景和 autonomy-ready fixture。 - `evals/prompts.csv`, `evals/run_evals.py`, `evals/grade_evals.py`, `evals/harness-skill-evals.md`
- 创建本次验证日志。 - `docs/validation/autonomy-layer-2026-05-11.md`

## Decisions

- 用 opt-in autonomy surface，而不是默认给所有标准仓库生成。 - 保持 thin harness，避免把所有项目都推向更重的占位和策略配置。
- 把 unattended readiness 做成单独脚本，而不是塞进 base audit。 - 基础 harness 审计与 autonomy 强校验的契约不同。
- 用 eval fixture 证明 readiness checker 可通过最小真实接线。 - 仅验证文件生成不足以说明 capability 落地。

## Decision Links

- ADR: none
- Design doc/spec: none

## Validation

- [x] `python3 -m py_compile skills/openai-harness-engineering/scripts/*.py evals/*.py` - 代码语法正确
- [x] `python3 skills/openai-harness-engineering/scripts/audit_harness.py --target . --mode full` - self-harness 完整审计通过
- [x] `python3 skills/openai-harness-engineering/scripts/check_harness_drift.py --target .` - 漂移扫描通过
- [x] `python3 evals/run_evals.py` - 生成 autonomy 扩展后的 artifacts
- [x] `python3 evals/grade_evals.py` - autonomy 扩展后的 eval 全通过
- [x] `python3 skills/openai-harness-engineering/scripts/check_autonomy_readiness.py --target "$TMPDIR"` - 接入真实命令后的 fixture 通过 unattended readiness

## Validation Evidence

- Validation log: `docs/validation/autonomy-layer-2026-05-11.md`
- Summary: skill 现在能为目标仓库生成 autonomy policy / runbook / drill surface，并能用确定性脚本区分“只是生成了文档”和“已经接好无人值守运行所需命令”的状态。

## Incident Links

- Incident: none

## Learnings

- 要让 skill 更接近“无人干预复杂任务”，关键不是继续堆叠说明文档，而是给目标仓库增加 machine-readable policy 和 stronger readiness checks。
- blank repo 依旧不会自动变成 autonomous runtime；但现在这个 skill 至少能把缺口明确定义出来，并用工具检出。

## Progress Log

- 2026-05-11: Plan created.
- 2026-05-11: 完成 autonomy surface、readiness checker、eval 扩展与验证。

## Open Questions

- 是否要继续为 autonomy surface 增加 provider-specific adapters，例如 Codex automation、GitHub Actions、Cron 或队列 worker 模板。
- 是否要把 autonomy readiness 的部分结果并入 base audit 的 warning 层。

## Follow-Ups

- 为 target repo 设计可选的 automation adapter surface，例如 `.github/workflows/agent-loop.yml` 或 `docs/generated/autonomy-config.json`。
- 增加更接近真实部署的 fixture，验证 post-deploy monitor 和 rollback 分支。

## Closure Notes

- Outcome: 已为 skill 增加 autonomy surface 与 unattended readiness audit，并通过 eval 和手工 fixture 验证。
- Changed files/modules: `skills/openai-harness-engineering/scripts/init_harness.py`, `skills/openai-harness-engineering/scripts/audit_harness.py`, `skills/openai-harness-engineering/scripts/check_harness_drift.py`, `skills/openai-harness-engineering/scripts/check_autonomy_readiness.py`, `README.md`, `skills/openai-harness-engineering/SKILL.md`, `skills/openai-harness-engineering/references/generated_files.md`, `evals/*`, `docs/validation/autonomy-layer-2026-05-11.md`
- Residual risk: 这个 skill 仍是 harness / readiness 层，不会替目标仓库自动提供真实 secrets、scheduler、deployment backend 或审批系统。

## Next Agent Handoff

- Current state: 改动和验证已完成，可继续做 provider-specific automation adapters。
- Next recommended action: 若目标是更接近真正无人值守运行，优先补自动化执行 adapter，而不是再增加抽象文档。
- Blockers: none
