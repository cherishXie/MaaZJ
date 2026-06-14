# R3 Pipeline Graph Audit

Date: 2026-06-09

Source of truth: `assets/interface.json`

Scope: read-only graph/reference audit and recovery path catalog initial draft.

## 结论摘要

- 本报告只读审计 `assets/interface.json` 与 `assets/resource/pipeline/`，未修改运行资源。
- 当前扫描到 47 个 pipeline JSON 文件、389 个 pipeline 节点、1073 条节点引用边。
- `assets/interface.json` 仍有 35 个 task、6 组 unique entry，和 R2 flow map 一致。
- 未发现悬空引用：task entry、`pipeline_override` 节点、`next`、`interrupt`、`on_error` 的目标节点均能在当前 pipeline 节点集合中找到。
- `pipeline_override` 涉及 6 个节点、64 处 task 覆盖记录；其中只有 7 条覆盖会改写 `next` 边，其余主要覆盖账号、服务器 OCR `expected` 或 `action`。
- 静态不可达候选 139 个，主要集中在未挂到当前 task entry 的活动、起号、探索、素材秘境、妖灵手札、幻装奖励、挑战赛等路径。它们只能作为“当前入口图未触达候选”，不能作为删除依据。
- Recovery/interrupt 边是当前 pipeline 的主要稳定机制之一：本次归类到 709 条 recovery 相关边，其中通用等待/延迟重试 343 条、返回/退出 143 条、弹窗关闭 79 条、活动确认/奖励 55 条、滑动/定位 27 条。

## 输入与边界

读取：

- `AGENTS.md`
- `assets/resource/pipeline/AGENTS.md`
- `.codex/skills/maazj-maafw-refactor/references/refactor-workflow.md`
- `.codex/skills/maazj-maafw-refactor/references/pipeline-rules.md`
- `docs/agent_design/refactor_design_maafw_test_automation_2026-06-07.md`
- `docs/agent_context/pipeline_flow_map_initial_2026-06-09.md`
- `assets/interface.json`
- `assets/resource/pipeline/`

未修改：

- `assets/interface.json`
- `interface.json`
- `assets/resource/pipeline/`
- `assets/resource/image/`
- `agent/`
- `deps/`
- `install/`

V0 边界：

- 严格 JSON 解析 `assets/interface.json`。
- 以 JSONC-aware 方式只读解析 pipeline 文件；保留原文件，不 strict-format。
- 从 `next`、`interrupt`、`on_error` 与 `pipeline_override` 提取引用图。
- 本报告不证明真实流程可达，不替代 V1-V5。

## 数据概览

| 项 | 数量 |
| --- | ---: |
| pipeline JSON 文件 | 47 |
| pipeline 节点 | 389 |
| task | 35 |
| unique task entry | 6 |
| 总引用边 | 1073 |
| `next` 边 | 520 |
| `interrupt` 边 | 541 |
| `on_error` 边 | 5 |
| `pipeline_override.next` 边 | 7 |
| 悬空引用候选 | 0 |
| 静态不可达候选 | 139 |
| 自循环候选 | 94 |
| 双向短循环候选 | 40 |

Action 分布：

| action | 节点数 |
| --- | ---: |
| `Click` | 284 |
| `DoNothing` | 79 |
| 未声明 action | 16 |
| `Swipe` | 5 |
| `InputText` | 2 |
| `StartApp` | 1 |
| `StopApp` | 1 |
| `StopTask` | 1 |

## Task Entry 与 Override

| entry | task 数 | 状态 |
| --- | ---: | --- |
| `点击罗小黑联动` | 1 | 节点存在 |
| `sub_启动杖剑传说官` | 1 | 节点存在 |
| `FARM_点击世界` | 1 | 节点存在 |
| `FARM_点击杂货店` | 1 | 节点存在 |
| `开始刷友情点` | 1 | 节点存在 |
| `用户切换_账号列表` | 30 | 节点存在 |

`pipeline_override` 覆盖节点：

| 节点 | 覆盖类型 | 说明 |
| --- | --- | --- |
| `sub_启动杖剑传说官_选择服务器` | `expected` | 30 个账号/服务器 task 覆盖服务器 OCR，例如 `晶`、`暖阳`、`朋克`、`蒸汽`。 |
| `用户切换_选择账号` | `expected` | 30 个账号/服务器 task 覆盖目标手机号。 |
| `FARM_世界返回家园` | `action` | `打野猪` task 覆盖为 `StopTask`，改变默认继续公会的行为。 |
| `FARM_宝库购买体力` | `next` | `暖阳 18918203738` 额外接入 `FARM_宝库购买限购`。 |
| `FARM_点击笔记` | `next` | `暖阳 18918203738` 改接每日活动/幻想阶梯路径。 |
| `FARM_家园主界面` | `next` | `暖阳 18918203738` 改接邮件、小推车与切号菜单收尾。 |

风险提示：

- `FARM_世界返回家园.action` 覆盖会改变 task 终止点，应继续作为 S6 smoke 候选。
- `暖阳 18918203738` 的 3 处 `next` 覆盖跨宝库、笔记、家园收尾，仍应作为 S5 单独验证候选。
- 账号/服务器 task 的真实路径必须叠加 `expected` 覆盖理解，不能只看 pipeline 默认节点。

## 引用完整性

本次未发现以下异常：

- task entry 指向不存在节点。
- `pipeline_override` 覆盖不存在节点。
- `next` 指向不存在节点。
- `interrupt` 指向不存在节点。
- `on_error` 指向不存在节点。
- `pipeline_override.next` 指向不存在节点。

这说明当前静态引用图没有明显断边，但不证明节点识别条件、图片、ROI 或真实设备流程有效。

## `on_error` 路径

当前仅发现 5 条 `on_error`：

| source | target | 文件 | 初判 |
| --- | --- | --- | --- |
| `魔物讨伐战斗中` | `魔物讨伐战斗中2` | `assets/resource/pipeline/activity/魔物讨伐.json` | 战斗中状态互相兜底。 |
| `魔物讨伐战斗中2` | `魔物讨伐战斗中` | `assets/resource/pipeline/activity/魔物讨伐.json` | 战斗中状态互相兜底。 |
| `FARM_点击本周精选` | `FARM_返回主家园` | `assets/resource/pipeline/小号/商城/本周精选.json` | 商城路径失败后回主家园。 |
| `开始起号` | `开始起号` | `assets/resource/pipeline/起号/start.json` | 起号入口自恢复。 |
| `选择体型` | `开始起号` | `assets/resource/pipeline/起号/start.json` | 起号流程失败回入口。 |

建议：

- T3 脚本应把 `on_error` 和 `interrupt` 分开输出，因为 `on_error` 数量少且语义更接近异常兜底。
- C5 不应先动 `魔物讨伐` 与 `起号` 的 `on_error`，它们当前未被 task entry 触达，缺少真实验证证据。

## 静态不可达候选

从 6 个 task entry 与 6 个 override 节点出发，沿 `next`、`interrupt`、`on_error`、`pipeline_override.next` 遍历后，仍有 139 个节点未触达。

按模块估算：

| 模块 | 不可达候选数 |
| --- | ---: |
| `events` | 34 |
| `notes` | 32 |
| `new-account` | 20 |
| `activity` | 16 |
| `mall` | 11 |
| `explore` | 11 |
| `home/bed` | 6 |
| `startup` | 3 |
| `other` | 3 |
| `farm-root` | 1 |
| `map` | 1 |
| `user` | 1 |

代表候选：

- 活动：`魔物讨伐`、`魔物讨伐战斗中`、`联动活动-进入`、`联动活动-点击开始战斗`、`联动-持续点击`。
- 起号：`开始起号`、`选择体型` 等 `起号/start.json` 节点。
- 探索：`探索_寻找定位标志`、`探索_神庙页面`、`探索_探索神庙`。
- 笔记/活动：`FARM_点击素材秘境`、`FARM_点击赛季活动`、`FARM_点击妖灵手札`、`FARM_本期领取手札`。
- 商城/奖励：`FARM_点击幻装1`、`FARM_幻装奖励页面1`、`挑战赛界面`、`领取挑战赛`。
- 其他：`点击兑换码`、`输入兑换码`、`确定输入兑换码`。

解释边界：

- 不可达候选只说明“从当前 `assets/interface.json` task entry 静态遍历未触达”。
- 它不代表节点无用，因为未来 task、手动 debug、活动入口、注释恢复分支或后续 override 都可能使用这些节点。
- 删除、迁移或重命名前仍必须按 AGENTS 规则重新搜索引用并执行对应验证。

## 循环候选

本次发现 94 个自循环候选、40 条双向短循环候选。

常见自循环类型：

- 等待界面稳定：例如 `sub_启动杖剑传说官_点击开始.interrupt -> sub_启动杖剑传说官_点击开始`。
- 领取/购买重试：例如 `FARM_杂货店购买限购.next -> FARM_杂货店购买限购`、`FARM_宝库购买限购.next -> FARM_宝库购买限购`。
- 返回重试：例如 `FARM_世界返回家园.interrupt -> FARM_世界返回家园`。
- 战斗或活动循环：例如 `FARM_打野猪.next -> FARM_打野猪`、`世界树副本页面.next -> 世界树副本页面`。
- 用户切换步骤重试：例如 `用户切换_点击菜单.interrupt -> 用户切换_点击菜单`。

代表双向短循环：

| A | B | 文件 | 初判 |
| --- | --- | --- | --- |
| `点击接受` | `战斗结束` | `activity/刷友情币.json` | 副本接受与战斗结束等待循环。 |
| `魔物讨伐战斗中` | `魔物讨伐战斗中2` | `activity/魔物讨伐.json` | 战斗中状态兜底循环。 |
| `FARM_委托页面` | `FARM_委托可提交` | `小号/任务/委托.json` | 委托状态轮询。 |
| `FARM_日常任务列表` | `FARM_日常任务` | `小号/任务/日常任务.json` | 日常任务领取轮询。 |
| `FARM_捐赠公会` | `FARM_捐赠公会页面` | `小号/公会/公会.json` | 捐赠页面状态轮询。 |

建议：

- 循环候选不能直接理解为死循环。很多节点依赖 OCR/TemplateMatch 状态变化退出。
- T3 可输出循环长度和字段来源；C 类实现任务再结合 V2/V3/V4 判断是否需要拆分。

## 跨模块边候选

跨模块边数量较高，主要来自各模块共享 `启动再等等`、弹窗关闭、返回主家园等 recovery 节点。

Top cross-module pairs：

| 来源模块 -> 目标模块 | 边数 | 说明 |
| --- | ---: | --- |
| `notes -> startup` | 76 | 笔记路径大量 interrupt 到 `启动再等等`。 |
| `events -> startup` | 56 | 精彩活动路径大量等待恢复。 |
| `mall -> startup` | 48 | 商城路径大量等待恢复。 |
| `home/bed -> startup` | 44 | 家园/床/邮件/小推车路径大量等待恢复。 |
| `guild -> startup` | 30 | 公会路径共享等待恢复。 |
| `map -> startup` | 20 | 地图路径共享等待恢复。 |
| `task -> startup` | 15 | 任务路径共享等待恢复。 |
| `user -> startup` | 15 | 用户切换路径共享启动等待。 |
| `new-account -> startup` | 14 | 起号路径共享启动等待。 |
| `home/bed -> user` | 11 | 家园收尾接用户切换菜单。 |

需要 R7 重点审查的非 recovery 跨模块边：

- `sub_启动杖剑传说官 -> 用户切换_点击雷霆账密登录`：启动与用户登录耦合。
- `sub_启动杖剑传说官_点击开始 -> 登录进入主家园界面`：启动进入 FARM 默认入口。
- `FARM_开始 -> FARM_点击杂货店`：farm root 到杂货店。
- `FARM_任务返回 -> FARM_点击商城`：任务到商城。
- `FARM_无公会 -> FARM_点击笔记`：公会到笔记。
- `FARM_公会商店返回 -> FARM_点击笔记`：公会商店到笔记。
- `FARM_返回主家园 -> FARM_家园主界面`：商城到家园收尾。
- `FARM_世界返回家园 -> FARM_点击公会`：地图到公会；`打野猪` task 会覆盖为 `StopTask`。
- `FARM_点击笔记 -> FARM_点击竞技` 或特殊账号覆盖到 `FARM_点击每日活动` / `FARM_点击幻想阶梯`。
- `FARM_家园主界面 -> 判断是否有新邮件` / `领取小推车` / `用户切换_点击菜单`：特殊账号收尾覆盖。

## Recovery Path Catalog 初版

| 分类 | 边数 | 代表节点/路径 | 作用初判 | 后续建议 |
| --- | ---: | --- | --- | --- |
| 通用等待/延迟重试 | 343 | 多数模块 `interrupt -> 启动再等等` | 等待界面稳定、加载、动画或网络延迟。 | C5 前先明确是否需要保留为共享基础 recovery；不建议早期合并删除。 |
| 返回/退出/回到稳定页 | 143 | `FARM_任务返回`、`FARM_返回主家园`、`FARM_世界返回家园`、`FARM_公会商店返回` | 回到模块出口、主家园或下一模块入口。 | R7 应把这些作为模块出口边处理；C5 可从单模块返回链试点。 |
| 弹窗关闭/遮挡恢复 | 79 | `升级礼包弹窗`、`礼包弹窗`、`FARM_空白处关闭`、委托好感度关闭 | 处理礼包、奖励、好感度、遮挡弹窗。 | R4 需补图片/OCR/ROI 完整性；C5 不应在缺证据时统一抽象。 |
| 活动确认/奖励推进 | 55 | `点击准备`、`点击接受`、`确定退出`、`FARM_任务奖励`、`获得奖励` | 活动、副本、奖励领取的状态推进。 | 活动开放状态影响大，应跟 S7 或活动专项验证绑定。 |
| 滑动/列表定位 | 27 | `执行滑动`、`用户执行滑动`、`执行横向左滑动`、`执行横向右滑动` | 服务器、账号、地图、商店列表定位。 | 登录、选服、账号切换相关滑动必须保守处理。 |
| 失败兜底/找不到目标 | 14 | `FARM_找不到商店`、`FARM_找不到公会商店`、`on_error` | 找不到入口、商店、战斗状态失败时转向恢复路径。 | 是 C5 候选，但需要先按模块验证。 |
| 其他 interrupt recovery | 48 | 自身 interrupt、模块内等待重试 | 多数是节点自身重试或局部轮询。 | T3 输出字段即可，R3 不判断对错。 |

## 对下游任务的建议

### R7-module-boundary-doc

- 把 `启动再等等`、弹窗关闭、返回主家园等共享 recovery 从普通业务跨模块边中拆开看。
- 模块边界文档应单列“共享 recovery 节点”与“业务出口边”。
- `user/startup/FARM` 的耦合边风险最高：登录、选服、账号切换、家园入口应保留更小边界。
- 特殊账号 `暖阳 18918203738` 的 override 应进入风险登记，不应只按默认 FARM 路径建模。

### T3-pipeline-ref-check-script

建议字段：

- 节点定义：`node`、`file`、`module`、`action`、`recognition`。
- 边：`source`、`target`、`field`、`source_file`、`source_module`、`target_module`、`from_override_task`。
- 异常：`missing_target`、`missing_entry`、`missing_override_node`。
- 图分析：`reachable_from_task_entry`、`reachable_from_override_node`、`self_loop`、`two_cycle`、`cross_module`。
- recovery 分类：`wait`、`swipe`、`popup_close`、`return_exit`、`stop`、`activity_confirm`、`fallback`、`other_interrupt`。

处理规则：

- 必须 JSONC-aware；不得 strict-format 或改写 pipeline。
- `assets/interface.json` 使用 strict JSON。
- `pipeline_override` 覆盖边必须标记 task 来源。
- 不可达候选输出必须带免责声明，不能自动生成删除建议。

### C5-recovery-node-normalization

可优先观察：

- `启动再等等` 作为通用等待 recovery 的共享程度。
- `FARM_空白处关闭` 在任务、公会、委托、奖励路径中的复用语义是否一致。
- 返回主家园/返回笔记首页/返回活动列表类路径是否可以按模块出口整理。

暂不建议早动：

- 登录、选服、账号切换相关 recovery。
- `打野猪` 的 `FARM_世界返回家园`，因为 task override 将其动作改成 `StopTask`。
- 活动开放状态不稳定的 `罗小黑联动`、`刷友情币`、`魔物讨伐`。
- 当前静态不可达的起号、探索、兑换码、素材秘境、妖灵手札路径。

## V0 验证记录

已完成：

- `assets/interface.json` 严格 JSON 解析通过。
- 47 个 pipeline JSON 文件以 JSONC-aware 方式只读解析通过。
- task entry 存在性检查通过。
- `pipeline_override` 覆盖节点存在性检查通过。
- `next`、`interrupt`、`on_error`、`pipeline_override.next` 目标节点存在性检查通过。
- R2 的 6 组 entry 与本次扫描一致。

未执行：

- V1 MaaFramework resource load。本任务未修改资源。
- V2 task entry 启动验证。
- V3 真实控制器流程验证。
- V4 日志、截图或 debug 证据。
- V5 回归矩阵。

## D4/D5/N1 判断

- D4：暂不需要。R3 任务矩阵与 Runbook 能承载 graph/reference audit、recovery catalog 和下游消费建议。
- D5：建议后续 T3 或 C5 前再检查。R3 观察到“共享 recovery 应与业务跨模块边分开建模”可能成为稳定规则，但当前仍是单次审计结论，暂不写入 `AGENTS.md` 或 skill。
- N1：暂不需要。本任务发现的是后续脚本字段建议和 C5 候选，没有新增立即实现需求。
