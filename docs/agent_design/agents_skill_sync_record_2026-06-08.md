# Agents Skill Sync Record 2026-06-08

## 来源

- 来源任务：`2026-06-07-refactor-design-maafw-test-automation`
- 触发原因：设计文档新增并稳定化 D4/D5/N1 反馈闭环、R/C/T/D/N 任务矩阵、单任务 Runbook 和 V0-V5 验证分层。
- 本次任务：D5-agents-skill-sync

## 同步结论

需要同步。

`AGENTS.md` 已覆盖 MaaZJ runtime truth、canonical source、资源验证最低要求和安全编辑边界，但缺少设计文档新增的后续重构任务闭环说明。项目专属 skill 已覆盖 ProjectInterface、pipeline、upstream 和 upgrade reference，但缺少面向 D4/D5/N1 与验证分层的可复用检查顺序。

## 已同步内容

- `AGENTS.md`
  - 新增“后续重构任务闭环”。
  - 明确后续 MaaFramework 适配重构、测试体系和文档反馈任务优先使用设计文档的任务矩阵、Runbook 和 D4/D5/N1 判定表。
  - 明确设计文档不改变 runtime truth。
  - 明确任务收尾时检查 D4、D5、N1。
  - 明确不得把单次日志、临时猜测或未验证探索结论写入 `AGENTS.md` 或项目 skill。
  - 在验证要求中补充 V0-V5 分层和代码重构任务的降级记录要求。
- `.codex/skills/maazj-maafw-refactor/SKILL.md`
  - 增加 `references/refactor-workflow.md` 作为后续 refactor/test automation/D4/D5/N1 工作入口。
- `.codex/skills/maazj-maafw-refactor/references/refactor-workflow.md`
  - 新增设计文档入口、可复用任务检查顺序、D4/D5/N1 判定和 V0-V5 验证层说明。

## 未同步内容

- 未复制设计文档中的完整任务矩阵、Runbook、提示词模板和详细任务清单，避免把设计文档大段内容重复写入 AGENTS/skill。
- 未写入任何单次任务日志、临时探索结论或未验证猜测。
- 未修改 `assets/interface.json`、根目录 `interface.json`、pipeline、图片、agent、deps、install 或 CI。

## 一致性检查

- `assets/interface.json` 仍是 runtime/release canonical source。
- 根目录 `interface.json` 仍不是 canonical，除非任务明确针对它。
- `assets/interface.json` 仍必须保持严格 JSON。
- pipeline JSONC-like 边界仍保持不变，不使用严格 JSON 工具批量格式化。
- 资源变更最低验证仍是 `python .\check_resource.py .\assets\resource\`，本次文档/skill-only 变更不需要运行资源检查。
- D4/D5/N1 规则只作为后续任务治理闭环，不改变业务资源行为。
