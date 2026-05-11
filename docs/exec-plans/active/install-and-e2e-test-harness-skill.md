# Install and e2e test harness skill

- Status: active
- Owner/agent: Codex
- Started: 2026-05-11
- Last updated: 2026-05-11
- Trajectory role: exec-plan index

## User Request

在 Codex 中安装 openai-harness-engineering skill，并创建新项目端到端测试其效果。

## Goal

把 skill 安装到 Codex skills 目录，并在一个全新测试项目里完成初始化、审计、漂移检查与结果评估，记录证据。

## Non-Goals

- 发布 skill 到远程仓库或 marketplace
- 修改 sample app 业务逻辑到超出验证所需的程度

## Context

- `skills/openai-harness-engineering/SKILL.md`：要求按 initialize/audit/operate 工作流测试 skill
- `skills/openai-harness-engineering/scripts/init_harness.py`：skill 的核心初始化器
- `skills/openai-harness-engineering/scripts/audit_harness.py`：判断输出是否达到 harness 预期
- `skills/openai-harness-engineering/scripts/check_harness_drift.py`：漂移检查
- `~/.codex/skills/`：Codex 本地 skill 安装目录

## Context Read

- `skills/openai-harness-engineering/SKILL.md` - 确认端到端测试应覆盖初始化、审计、漂移检查
- `~/.codex/skills/.system/skill-installer/SKILL.md` - 确认官方安装脚本偏向 GitHub 源，当前本地仓库场景需要本地复制安装
- `skills/openai-harness-engineering/scripts/init_harness.py` - 确认 standard profile 会自动检测 frontend/backend/ops surface
- `skills/openai-harness-engineering/scripts/audit_harness.py` - 确认审计失败来源既可能是待接入占位符，也可能是文档误判

## Plan

1. 将 skill 安装到 `~/.codex/skills/openai-harness-engineering`。
2. 创建一个能触发 frontend/backend 自动检测的干净测试项目。
3. 使用已安装 skill 的脚本初始化该项目并检查输出。
4. 运行 audit/drift，区分接入占位符问题与 skill 级问题。
5. 对测试项目做最小接入，复跑验证并记录最终结果。

## Actions Taken

- 复制 `skills/openai-harness-engineering/` 到 `~/.codex/skills/openai-harness-engineering`，完成本地安装。
- 创建测试仓库 `/tmp/ohe-e2e-skill-app`，包含 `package.json`、`src/app/page.tsx`、`server/index.js`，用于触发 frontend/backend 检测。
- 从已安装路径运行 `init_harness.py`，以 `standard` profile 初始化测试仓库。
- 运行首次 `audit_harness.py`，记录原样生成结果的失败项。
- 在测试仓库中用最小真实命令替换占位符，随后运行 `npm install --package-lock-only --ignore-scripts`、`npm run validate`、`audit_harness.py`、`check_harness_drift.py`。
- 修正 runbook 中被审计器误判为命令的 ``exit code 0`` 文本，复跑 audit 至全绿。

## Decisions

- 采用本地复制安装而不是 GitHub 安装脚本 - 当前 skill 源在本地仓库内，且 `skill-installer` 的 helper 仅覆盖 GitHub 源。
- 用 `standard` profile 测试而不是 `minimal` - 这样能同时覆盖 surface detection、ops 文档、manifest 与核心 map。
- 不直接修改 skill 源码来消除首次审计失败 - 本轮目标是先验证已安装 skill 的真实使用效果，再区分接入成本与框架缺陷。

## Decision Links

- ADR: none
- Design doc/spec: none

## Validation

- [x] `cp -R /Users/ubuntu/1-project/openai-harness-engineering/skills/openai-harness-engineering ~/.codex/skills/openai-harness-engineering` - skill 被安装到 Codex 本地 skills 目录
- [x] `python3 ~/.codex/skills/openai-harness-engineering/scripts/init_harness.py --target /tmp/ohe-e2e-skill-app --project-name "OHE E2E Skill App" --project-description "Fixture app for validating the installed openai-harness-engineering skill" --tech-stack "Node.js, React, Express" --domains "developer tooling, harness operations" --primary-agent Codex --profile standard` - 测试仓库生成 harness 文件与 manifest
- [x] `python3 ~/.codex/skills/openai-harness-engineering/scripts/audit_harness.py --target /tmp/ohe-e2e-skill-app --mode full` - 初始结果暴露占位符和 runbook 命令解析问题；最小接入后复跑为全绿
- [x] `npm install --package-lock-only --ignore-scripts` - fixture 安装命令成功
- [x] `npm run validate` - fixture 验证命令成功
- [x] `python3 ~/.codex/skills/openai-harness-engineering/scripts/check_harness_drift.py --target /tmp/ohe-e2e-skill-app` - 输出 `No harness drift detected`

## Validation Evidence

- Validation log: none
- Summary: 已安装 skill 可在全新项目中成功生成标准 harness，并正确检测出 `frontend`、`backend`、`ops` surfaces。首次 audit 出现 12 个 workflow failures，主要来自未接入前的占位符；最小接入后仅剩 1 个 runbook 文本误判，修正后 audit 全通过，drift check 也通过。

## Incident Links

- Incident: none

## Learnings

- 这个 skill 的“原样生成”更像可接入 scaffold，而不是开箱即过审的最终态。
- `audit_harness.py` 会把 runbook 中的反引号文本解析成命令；runbook 写法需要避免把纯结果描述放进反引号。
- 新增的 `AGENTS.md` 规则章节已经随安装版本生效，并体现在测试项目的生成结果中。

## Progress Log

- 2026-05-11: Plan created.

## Open Questions

- 是否要在 skill 源码里调整审计器，避免把 runbook 中的非命令反引号文本误判为可执行命令。
- 是否要让 `validation-log-template.md` 的模板占位格式与 placeholder 审计规则解耦，以减少初始化后的首轮审计噪声。

## Follow-Ups

- 若要把“初始化后首轮 audit 更安静”作为目标，可进一步优化模板占位策略和 runbook 命令识别规则。
- 若要验证更重的真实项目场景，可再补一个包含真实 dev server 和 UI smoke 的 fixture。

## Closure Notes

- Outcome: 已完成安装与端到端测试；效果整体符合“薄 harness 脚手架”的预期，但首次 audit 需要接入与少量文案注意事项。
- Changed files/modules: `~/.codex/skills/openai-harness-engineering`, `/tmp/ohe-e2e-skill-app/*`
- Residual risk: 本轮 fixture 是轻量项目，尚未覆盖真实前端 dev server、浏览器 smoke 或复杂 CI 命令。

## Next Agent Handoff

- Current state: 安装完成，测试项目初始化与验证完成，结论可直接对用户汇报。
- Next recommended action: 如需提升体验，优先修正审计器对 runbook 反引号文本的误判，并考虑降低首轮 placeholder 噪声。
- Blockers: none
