# R8 Low-Risk Pilot Selection

Date: 2026-06-10

Source of truth: `assets/interface.json`

Scope: R8-low-risk-flow-selection, documentation-only pilot selection and first C-task candidate.

## 结论摘要

- 本文档消费 R1 `interface_inventory_2026-06-08.md`、R2 `pipeline_flow_map_initial_2026-06-09.md`、R4 `image_reference_audit_2026-06-09.md` 与 R7 `module_boundary_r7_2026-06-09.md`。
- 首个低风险试点建议选择 C1-shop-flow-pilot，范围收窄为 M4 商城/杂货店/宝库中的“杂货店入口到宝库免费体力再返回”子 flow。
- 首选试点不直接处理 `FARM_杂货店购买限购` 自循环，不处理特殊账号 `暖阳 18918203738` 接入的 `FARM_宝库购买限购`，不替换共享图片，不合并 recovery。
- 该选择只证明“适合作为第一个 C 类候选”，不证明真实流程已通过 V2/V3/V4；后续 C1 实施仍需 V1+V2，具备环境时补 V3/V4，否则记录降级。
- 本任务未修改 `assets/`、`agent/`、`deps/`、`install/` 或 CI。

## 输入与边界

读取：

- `AGENTS.md`
- `.codex/skills/maazj-maafw-refactor/SKILL.md`
- `.codex/skills/maazj-maafw-refactor/references/refactor-workflow.md`
- `.codex/skills/multi-agent-refactor/SKILL.md`
- `docs/agent_context/PROJECT_UNDERSTANDING_2026-06-06.md`
- `docs/agent_context/interface_inventory_2026-06-08.md`
- `docs/agent_context/pipeline_flow_map_initial_2026-06-09.md`
- `docs/agent_context/image_reference_audit_2026-06-09.md`
- `docs/agent_design/module_boundary_r7_2026-06-09.md`
- `docs/agent_design/refactor_design_maafw_test_automation_2026-06-07.md`

未修改：

- `assets/interface.json`
- `interface.json`
- `assets/resource/pipeline/`
- `assets/resource/image/`
- `agent/`
- `deps/`
- `install/`
- `.github/workflows/`

边界声明：

- 本文档不替代 `assets/interface.json`、pipeline 或图片资源的实际行为。
- R1/R2/R4/R7 的静态结论不能直接作为资源删除、节点合并或图片替换依据。
- 本文档不实施 C1，不运行 MaaFramework，不触发真实控制器流程。

## 评分维度

评分使用 `高`、`中`、`低` 表示风险或适配度，偏向选择“小范围、可回滚、验证入口明确”的候选。

| 维度 | 低风险判定 | 高风险信号 |
| --- | --- | --- |
| 模块范围 | 单模块或单个子 flow | 跨启动、账号、活动、地图或多个 FARM 子模块 |
| 入口可定位性 | 有 canonical task entry 或 R2 S 点候选 | 只能从静态不可达池推测 |
| 出口清晰度 | 有明确返回、下一模块或 StopTask 候选 | 自循环、活动开放状态、无明确终点 |
| override 影响 | 不依赖账号/服务器或特殊账号覆盖 | 依赖 30 个账号/服务器覆盖或特殊账号 next/action 覆盖 |
| 共享识别资源 | 不替换共享图片，仅记录影响 | 直接动 `红点.png`、`家园图标.png`、`auto_add.png` 等共享资源 |
| OCR/ROI 风险 | 仅观察或收窄，不扩大识别范围 | no_roi、large_roi、edge_roi 且缺截图证据 |
| 验证入口 | 有 V2/V3 候选与降级条件 | 缺少任务入口或验证状态不可控 |
| 回滚边界 | 可按单个文件/单个子 flow 回滚 | 改动公共 recovery、全局入口或共享资源 |
| C 类适配 | 可直接转为 C1/C2 单任务 | 需要先做 T3/T4/T6 或 N1 分流 |
| evidence_required | 后续证据类型明确 | 证据依赖活动时段、账号状态或不可复现环境 |
| degraded_verification_condition | 无设备/无账号时可明确降级 | 降级后无法判断风险是否可接受 |

## 候选对比

| 候选 | 模块 | 代表路径 | 优点 | 风险 | 适配任务 | 结论 |
| --- | --- | --- | --- | --- | --- | --- |
| A. 杂货店/宝库免费体力窄 flow | M4 | `FARM_点击杂货店` -> `FARM_杂货店商店` -> `FARM_点击宝库` -> `FARM_宝库购买体力` -> `FARM_宝库返回` | R2 S4 有验证候选；范围集中；可作为 C1；不必改启动/账号/活动/地图 | 可能遇到弹窗、商店状态和共享 `红点.png`；若处理限购会触发 R7-R03/R7-R11 | C1 | 首选 |
| B. 杂货店限购购买 flow | M4 | `FARM_杂货店购买限购` 自循环 | 贴近 shop 业务，适合后续优化 | R7-R11 要求 V2/V3 观察退出条件；静态上不能判定死循环 | C1 | 延后到 A 之后 |
| C. 宝库限购特殊账号 flow | M4/M11 | `FARM_宝库购买体力` -> `FARM_宝库购买限购` -> `FARM_宝库返回` | 覆盖特殊账号真实差异 | 触发 R7-R03；R4 标记 `FARM_宝库购买限购` large_roi；需要特殊账号证据 | C1/C2/T6 | 不作为首选 |
| D. 公会/奖励窄 flow | M5 | `FARM_点击公会` 下游奖励/任务路径 | 与 C2 匹配；可做奖励路径试点 | 共享 `红点.png`、`FARM_空白处关闭`，可能进入 C5 recovery 风险 | C2 | 备选 |
| E. 床/邮件/小推车收尾 | M8/M11 | `判断是否有新邮件` -> `领取小推车` -> `用户切换_点击菜单` | 收尾边界清晰，能覆盖真实账号切换前置 | 特殊账号收尾和疑似未引用图片族相关，触发 R7-R12 | C2/T6 | 备选但需特殊账号证据 |
| F. 启动/选服 | M1 | `sub_启动杖剑传说官` -> 选服 -> 家园 | 价值高 | 高风险，30 个 server override，OCR/no_roi | T6/C later | 拒绝作为首试点 |
| G. 账号切换 | M2 | `用户切换_账号列表` -> 登录 -> 选服 | 价值高 | 高风险，30 个 account override，列表滚动 | T6/C later | 拒绝作为首试点 |
| H. 地图/打野猪 | M7 | `FARM_点击世界` -> 打野猪 -> `FARM_世界返回家园` | task 有 StopTask 覆盖，边界有价值 | 地图定位、野猪模板、托管次数 OCR 高风险 | C4/T6 | 拒绝作为首试点 |
| I. 活动单 flow | M9 | 罗小黑联动或刷友情币 | 可独立成 C3 | 活动开放状态、循环终点和奖励状态不稳定 | C3/T6 | 拒绝作为首试点 |

## 首选试点

首选：C1-shop-flow-pilot 的最小子集，命名建议为“杂货店/宝库免费体力导航试点”。

### 范围

允许范围：

- 只围绕 M4 的默认 `流水线` shop 子 flow。
- 起点：`FARM_点击杂货店`。
- 核心路径：`FARM_点击杂货店` -> `FARM_杂货店商店` -> `FARM_点击宝库` -> `FARM_宝库购买体力` -> `FARM_宝库返回`。
- 终点：`FARM_宝库返回`，后续是否进入 `FARM_点击公会` 只作为出口保持项，不在首个试点中重构公会。
- 可读输入：R1/R2/R4/R7 与必要的 M4 pipeline 文件。
- 可写范围应由后续 C1 plan 再收窄，默认只允许相关 M4 pipeline 节点或说明文档。

禁止触碰：

- 不修改 `assets/interface.json` 或根目录 `interface.json`。
- 不处理 `FARM_杂货店购买限购` 自循环，除非 C1 plan 单独把它列为观察项而非重构项。
- 不处理特殊账号 `暖阳 18918203738` 的 `FARM_宝库购买体力.next` 覆盖，不改 `FARM_宝库购买限购`。
- 不替换或重命名 `红点.png`、`家园图标.png` 或其他共享图片。
- 不合并 `升级礼包弹窗`、`礼包弹窗`、`FARM_找不到商店`、`启动再等等` 等 recovery。
- 不进入启动、选服、账号切换、地图、活动或公会奖励重构。

### 选择理由

- R1 显示 `流水线` task 的 entry 是 `FARM_点击杂货店`，没有 task-level override，是比账号/服务器任务更清晰的默认入口。
- R2 已将 S4 FARM 杂货店入口列为 V2/V3 验证候选，且路径集中在 M4。
- R7 明确 M4 可作为 R8 低风险试点候选，但要求避开特殊账号覆盖和共享图片风险。
- R4 对商城/宝库的证据需求为中优先级，相比启动/账号/地图/活动更适合作为第一个 C 类资源试点。
- 该子 flow 可以把“入口仍可达、出口不悬空、回滚边界明确”作为 C1 的核心验证目标。

### 必须单列风险

| 风险 ID | 内容 | C1 处理要求 |
| --- | --- | --- |
| R7-R03 | 特殊账号 `暖阳 18918203738` 三处 `next` 覆盖 | C1 首试点不改特殊账号覆盖；若运行该账号，只记录降级/跳过。 |
| R7-R07 | `家园图标.png`、`红点.png` 共享图片 | 不改共享图片；如节点引用这些资源，只写影响范围和截图需求。 |
| R7-R11 | `FARM_杂货店购买限购` 自循环 | 不直接判为死循环；首试点只观察是否影响进入宝库，不重构该循环。 |
| R4-OCR-01 | `FARM_宝库购买体力` no_roi | C1 如调整识别，需截图或 debug；否则只记录风险。 |
| R4-OCR-02 | `FARM_宝库购买限购` large_roi | 首试点排除该节点；后续特殊账号任务单独处理。 |

### 验证入口

最低建议：

- V1：C1 实施后运行 `python .\check_resource.py .\assets\resource\`。
- V2：通过 `流水线` task entry 或 `Tasker.post_task(...)` 启动到 `FARM_点击杂货店`，确认入口仍可启动。
- V3：具备真实控制器时观察从杂货店进入宝库、购买/判断免费体力、返回宝库出口。
- V4：保留关键截图或日志，至少包括杂货店入口、宝库页面、`FARM_宝库购买体力` 判断、`FARM_宝库返回`。

降级条件：

- 无设备、无账号、无法进入真实控制器时，C1 可以记录 V2/V3/V4 降级，但必须说明残余风险。
- 若商店状态、免费体力状态或弹窗状态不可复现，记录状态不满足，不把未观察到的分支判为通过。
- 若执行时进入特殊账号路径，停止扩大范围，转为 T6/S5 或后续特殊账号 C 任务。

回滚点：

- C1 所有资源改动必须限制在后续 plan 指定的 M4 节点范围。
- 如 V1 失败或 V2 入口不可达，优先回滚 C1 对相关 M4 pipeline 节点的改动。
- 如 V3/V4 观察到弹窗/recovery 误伤，不在同一 C1 中顺手合并 recovery，转 C5 或记录 N1。

## 备选试点

### 备选 1：C2 reward/cleanup 窄 flow

候选：M5 中可单独验证的公会/奖励领取子 flow。

使用条件：

- 若 C1 shop 路径因设备状态、商店状态或免费体力状态长期不可验证，可选择本备选。
- 必须避开 `FARM_空白处关闭` 跨模块统一抽象，避免提前进入 C5。
- 若触及 `红点.png`，需记录共享图片影响范围和截图证据。

### 备选 2：M8 邮件/小推车收尾观察 flow

候选：特殊账号收尾中的邮件/小推车路径。

使用条件：

- 必须具备 `暖阳 18918203738` 或等价特殊账号证据。
- 不清理 `邮件*.png`、`小推车*.png`、`苹果树.png` 等疑似未引用图片族。
- 更适合作为 T6/S5 证据任务或后续 C2，而不是首个 C1。

## 拒绝作为首试点的候选

| 候选 | 拒绝理由 | 后续路径 |
| --- | --- | --- |
| M1 启动/登录/选服 | 依赖服务器 OCR、公告状态和 30 个 server override，风险高。 | T6 smoke 后再评估。 |
| M2 账号切换 | 依赖手机号 OCR、列表滚动和登录状态，风险高。 | T6 smoke 或账号专项。 |
| M7 地图/打野猪 | 地图定位、野猪模板、托管次数 OCR 需要 V3/V4，且 `StopTask` 覆盖改变终止语义。 | C4 或地图专项。 |
| M9 活动 flow | 活动开放状态、循环终点和奖励状态不可控。 | C3 单活动 flow，需活动状态降级记录。 |
| M10 公共 recovery | 共享 recovery 的复用语义未证实，过早合并会影响多个模块。 | C5 且先单模块验证。 |
| M12 静态不可达候选池 | 缺 canonical task entry，可能是历史、未来或 debug 资源。 | T3/T4/N1。 |

## 首个 C 任务提示词草案

```txt
使用 multi-agent-refactor 工作流创建并处理一个新任务：

任务：C1-shop-flow-pilot，围绕 R8 选定的 M4“杂货店/宝库免费体力导航试点”做首个低风险资源改动。

约束：
- 运行真相以 assets/interface.json 为准，不读取根目录 interface.json 作为 canonical。
- 只允许围绕默认 流水线 的 M4 shop 子 flow 规划：FARM_点击杂货店 -> FARM_杂货店商店 -> FARM_点击宝库 -> FARM_宝库购买体力 -> FARM_宝库返回。
- 不修改 assets/interface.json、interface.json、agent/、deps/、install/ 或 CI。
- 不处理 FARM_杂货店购买限购 自循环，不处理特殊账号 暖阳 18918203738 的 FARM_宝库购买限购。
- 不替换、重命名或移动图片资源；共享图片 红点.png、家园图标.png 只记录影响范围。
- 不合并公共 recovery，如 启动再等等、升级礼包弹窗、礼包弹窗、FARM_找不到商店。
- 资源变更最低验证为 V1：python .\check_resource.py .\assets\resource\。
- 还需要设计 V2 task entry 启动验证；具备环境时执行 V3/V4，否则写明降级原因、残余风险和补验条件。
- safe 模式，implementation/test/code review 后停。
```

## V0 文档交叉检查

| 检查项 | 结果 | 说明 |
| --- | --- | --- |
| R1 task inventory 已消费 | passed | 使用 `流水线` task entry `FARM_点击杂货店`，并避开 30 个账号/服务器高风险 override。 |
| R1 特殊 override 已消费 | passed | `暖阳 18918203738` 的 3 个 `next` 覆盖进入首选风险和排除范围。 |
| R2 S1-S7 已消费 | passed | 首选来自 S4；S1/S2/S3/S6/S7 均拒绝作为首试点；S5 作为特殊账号风险。 |
| R2 unknown 未写成事实 | passed | `FARM_杂货店购买限购` 自循环仅作为风险，不作为可实施结论。 |
| R4 image/OCR 风险已消费 | passed | 共享图片、`FARM_宝库购买体力` no_roi、`FARM_宝库购买限购` large_roi 均已登记。 |
| R7 module boundary 已消费 | passed | 首选限定 M4；M1/M2/M7/M9/M10/M12 按 R7 风险延后。 |
| R7-R03/R7-R07/R7-R11 已单列 | passed | 三项均进入“必须单列风险”。 |
| 首选具备验证入口 | passed | 对应 R2 S4，C1 需 V1+V2，具备环境时 V3/V4。 |
| R8 未修改业务资源 | passed | 本任务只新增设计文档并更新 `.agent/` 任务记录。 |

未执行：

- V1 MaaFramework resource load。本任务不修改资源。
- V2 task entry 启动验证。
- V3 真实控制器流程验证。
- V4 日志、截图或 debug 证据。
- V5 回归矩阵。

## D4/D5/N1 判断

- D4：暂不需要。首选候选具备 R2 S4 验证入口，且本文档已记录 V2/V3/V4 或降级路径；设计矩阵能承载 R8 输出。
- D5：暂不立即触发。试点选择规则与现有 `AGENTS.md`、R7 和项目 skill 边界一致；建议在 C1 实施后再判断是否把“首试点收窄优先级”固化到 skill。
- N1：暂不需要。本文档只输出首个 C 任务候选和提示词草案，没有混入实际资源改动、图片治理或测试脚本新需求。
