# Add AGENTS generation rules

- Status: active
- Owner/agent: Codex
- Started: 2026-05-11
- Last updated: 2026-05-11
- Trajectory role: exec-plan index

## User Request

生成agents.md时，增加 Engineering Rules、Evidence Rules、Verification、Commits and PRs、Responses 规则。

## Goal

`skills/openai-harness-engineering/scripts/init_harness.py` 生成的 `AGENTS.md` 默认包含用户要求的规则，并在当前仓库留下对应计划与验证记录。

## Non-Goals

- 扩展到未被请求的其他生成文档
- 重写现有审计规则或新增额外策略文档

## Context

- `AGENTS.md`：当前仓库的 agent map 示例
- `PLANS.md`：要求非 trivial 工作保留执行计划
- `skills/openai-harness-engineering/SKILL.md`：要求优先改脚本生成逻辑，且保持 `AGENTS.md` 为路由入口
- `skills/openai-harness-engineering/scripts/init_harness.py`：`AGENTS.md` 模板生成位置

## Context Read

- `PLANS.md` - 确认需要记录计划与收尾验证
- `skills/openai-harness-engineering/SKILL.md` - 确认此类改动属于 harness dogfooding
- `skills/openai-harness-engineering/scripts/init_harness.py` - 确认 `agents_md()` 是唯一模板入口
- `AGENTS.md` - 确认当前示例文件需要与生成规则保持一致

## Plan

1. 更新 `agents_md()` 模板，加入新规则章节。
2. 同步当前仓库 `AGENTS.md`，让 dogfood 示例与生成结果一致。
3. 运行定向验证并把结果写回本计划。

## Actions Taken

- 阅读 `PLANS.md`、`skills/openai-harness-engineering/SKILL.md`、`skills/openai-harness-engineering/scripts/init_harness.py`、`AGENTS.md`，定位最小改动面。
- 创建当前执行计划，作为本次改动的轨迹索引。
- 更新 `skills/openai-harness-engineering/scripts/init_harness.py` 的 `agents_md()`，加入 `Engineering Rules`、`Evidence Rules`、`Verification`、`Commits and PRs`、`Responses` 五个章节。
- 同步更新仓库根目录 `AGENTS.md`，让 dogfood 示例与生成模板一致。

## Decisions

- 在 `AGENTS.md` 中直接加入请求的规则章节 - 用户明确要求生成结果包含这些规则。
- 将空白 `Verification` 章节收敛为对 `QUALITY_SCORE.md` 与 `RELIABILITY.md` 的引用 - 避免空章节，同时不发明超出仓库现状的具体验证命令。

## Decision Links

- ADR: none
- Design doc/spec: none

## Validation

- [x] `python3 skills/openai-harness-engineering/scripts/init_harness.py --target /tmp/ohe-agents-check --project-name Demo --project-description Demo --tech-stack Python --domains Harness --primary-agent Codex --profile minimal` - 生成的 `AGENTS.md` 包含新增章节
- [x] `rg -n "^## (Engineering Rules|Evidence Rules|Verification|Commits and PRs|Responses)$" AGENTS.md` - 当前仓库示例包含这些章节
- [x] `python3 -m py_compile skills/openai-harness-engineering/scripts/init_harness.py` - 脚本语法有效
- [x] `wc -l AGENTS.md /tmp/ohe-agents-check/AGENTS.md` - 当前示例 75 行，生成结果 101 行，均低于审计默认上限 120

## Validation Evidence

- Validation log: none
- Summary: 生成器实跑成功；临时目录 `/tmp/ohe-agents-check/AGENTS.md` 包含全部新增章节；`init_harness.py` 通过 `py_compile`；当前与生成结果的行数均在审计阈值内。

## Incident Links

- Incident: none

## Learnings

- 仍需关注 `AGENTS.md` 长度；本次新增规则后，根目录示例为 75 行，带 managed markers 的生成结果为 101 行，仍低于审计默认上限。

## Progress Log

- 2026-05-11: Plan created.

## Open Questions

- none

## Follow-Ups

- 如后续需要更强约束，优先补脚本或审计，而不是继续膨胀 `AGENTS.md`。

## Closure Notes

- Outcome: 已完成模板扩展，并同步当前仓库 `AGENTS.md`。
- Changed files/modules: `skills/openai-harness-engineering/scripts/init_harness.py`, `AGENTS.md`
- Residual risk: 当前没有自动化断言专门覆盖 `AGENTS.md` 章节内容，后续若再扩展模板，仍主要依赖生成验证与审计。

## Next Agent Handoff

- Current state: 改动与定向验证已完成，可继续按需补更细的自动化测试或提交变更。
- Next recommended action: 若要进一步收紧回归保护，可在 `evals/` 增加对 `AGENTS.md` 章节存在性的断言。
- Blockers: none
