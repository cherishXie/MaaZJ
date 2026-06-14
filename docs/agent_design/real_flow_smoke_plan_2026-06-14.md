# MaaZJ Real Flow Smoke Plan

Date: 2026-06-14

Source of truth: `assets/interface.json`

Scope: T6-real-flow-smoke-plan, documentation-only smoke matrix, evidence template, and degraded verification format.

## 定位

本文档定义 MaaZJ 后续真实流程 smoke 的最小矩阵和证据格式。它不是 CI 全自动承诺，也不表示当前已经跑通真实游戏流程。

运行入口、task name、entry 与 `pipeline_override` 语义以 `assets/interface.json` 为准。根目录 `interface.json` 不作为 canonical source，不参与 case 选择、验证判定或回滚判断。

本文档只消费 R1/R2/R7/R8/R9 与 T1-T5 的只读结论，不修改 `assets/interface.json`、pipeline、图片、Python agent、`deps/`、`install/` 或 CI。

## 输入事实摘要

| 输入 | T6 使用方式 |
| --- | --- |
| R1 `interface_inventory_2026-06-08.md` | 选择 task、entry、账号/服务器 override 与特殊 `next/action` override。 |
| R2 `pipeline_flow_map_initial_2026-06-09.md` | 选择 S1-S7 候选点、关键节点、出口和 unknown 风险。 |
| R3 `pipeline_graph_audit_2026-06-09.md` | 使用引用完整性、recovery 分类和 `on_error`/interrupt 边界。 |
| R4 `image_reference_audit_2026-06-09.md` | 记录截图/debug 证据需求，特别是选服、账号、地图、商城、活动与 recovery。 |
| R7 `module_boundary_r7_2026-06-09.md` | 将 S1-S7 映射到模块和 risk register。 |
| R8 `low_risk_pilot_selection_r8_2026-06-10.md` | 将 C1 首试点绑定到 S4 shop/reward smoke，不混入特殊账号覆盖。 |
| R9 `test_script_design_r9_2026-06-10.md` | 复用 V0-V5 验证层、报告字段和降级记录格式。 |
| T1-T5 任务结果 | 作为 V0 静态前置检查；不证明 V2 task entry 启动或 V3 真实控制器流程。 |

## 验证层边界

| 层级 | 在 T6 中的含义 | 证据 |
| --- | --- | --- |
| V0 | 检查 task/entry/override、引用、图片、custom 静态事实完整。 | T1-T5 脚本输出、R1-R9 报告。 |
| V1 | MaaFramework resource bundle 可加载。 | `python .\check_resource.py .\assets\resource\` 结果。 |
| V2 | 指定 ProjectInterface task entry 能启动，并到达第一个预期关键节点或明确失败。 | Tasker/MFAAvalonia 启动记录、日志。 |
| V3 | 在真实 Adb/Win32 控制器下到达关键节点或终止状态。 | 运行日志、人工观察记录。 |
| V4 | 证据可复查。 | `debug/maa.log`、截图、录屏、任务返回状态、证据索引。 |
| V5 | 多 case 回归矩阵。 | 发布前或大范围重构后的回归记录。 |

`check_resource.py` 和 T1-T5 只读脚本不能证明真实流程通过。C 类资源变更至少需要 V1；涉及真实 flow 的完成标准需要记录 V2/V3/V4 执行结果，或填写降级记录。

## C 类 V3/V4 执行条件与路径规则

后续 C 类任务执行真实控制器验证前，必须先判断是否具备以下条件。条件不满足时不要把 V3/V4 写成通过，应填写降级记录并说明补验条件。

### 执行条件

- 控制器可用：Adb 设备为 `device`，或 Win32 窗口可被 MaaFramework 控制。
- 目标应用可用：目标包已安装并可启动；若使用模拟器，应记录模拟器实例、ADB 地址或窗口标识。
- 资源可加载：资源变更后已完成 V1 `python .\check_resource.py .\assets\resource\`。
- 入口可解释：task、entry 和 `pipeline_override` 均来自 `assets/interface.json` 或当前任务明确记录的一次性运行时 override。
- 前置页面可满足：账号、服务器、活动开放状态、当前位置、弹窗状态能够支撑目标子 flow 被观察。
- 证据目录已准备：当前 `.agent/tasks/<task-id>/` 中有截图、日志摘录或 evidence index 的保存位置。

### 路径选择

- 优先使用 `assets/interface.json` 中的 ProjectInterface task 执行完整目标路径。
- 若完整 task 会立即进入当前 C 任务边界外的分支，可以分段投递目标 entry，但必须写明分段原因、起点和停止点。
- 分段投递只能证明该段路径通过，不能证明被跳过的上游、下游或兄弟分支通过。
- 可以使用一次性运行时 override 阻止流程越界，例如把已验证出口节点的 `next` 临时置空；这种 override 只能用于停止验证，不得改变被验证节点的识别、动作或业务语义。
- 若使用运行时 override，必须在 V4 证据中记录 override 摘要，并在结论中写明资源文件未因此改变。

### 通过标准

- V2 通过：Tasker/MFAAvalonia 成功投递目标 task 或 entry，并到达第一个预期关键节点，或以可解释方式失败。
- V3 通过：真实控制器日志或人工观察证明目标子 flow 到达预期关键节点或终止状态。
- V4 通过：证据可复查，至少包含日志节点序列、关键页面截图或 debug 记录；涉及 OCR/TemplateMatch/ROI 变化时，应记录命中的文本/模板、位置、score 或截图。
- 有边界通过：目标子 flow 通过，但因为分段投递、运行时 stop override、账号/活动状态限制，没有覆盖完整 task 或特殊 override。此时结论必须写成“通过，有边界”。

### C1 实证回写

2026-06-14 对 C1-shop-flow-pilot 的补验确认：S4 shop 子 flow 可以在 MuMu Adb 控制器中分两段验证。

- 第一段：`FARM_点击杂货店 -> FARM_杂货店商店`，验证默认入口能进入商店页。
- 第二段：`FARM_点击宝库 -> FARM_宝库购买体力 -> FARM_宝库返回`，使用一次性运行时 override `FARM_宝库返回.next=[]` 阻止继续进入公会下游。
- 该补验确认 `FARM_宝库购买体力.roi = [24, 173, 442, 844]` 能覆盖真实宝库页 `免费` 文本；但不覆盖 `FARM_杂货店购买限购`、特殊账号 `暖阳 18918203738` override 或公会下游。

后续 C 类任务可复用这种“完整 task 优先、必要时分段、出口 stop override 仅用于边界控制”的验证策略，但必须按本节记录边界。

## Smoke Matrix

| Case ID | 目标 | 控制器 | 执行方式 | ProjectInterface task | entry | `pipeline_override` | 前置条件 | 操作步骤 | 期望关键节点或终止状态 | 必要证据 | 失败处理和回滚 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | 启动到首页 | Adb 优先；Win32 可补充 | MFAAvalonia 或 Python Tasker | `启动杖剑传说官` | `sub_启动杖剑传说官` | task 有空 override；不改变路径 | App 可启动；账号处于可进入游戏或可观察登录态；资源 bundle 已加载 | 启动 task，观察公告、选服、开始按钮和家园识别 | 至少到达 `登录进入主家园界面` 或识别 `家园图标.png`；若未登录，记录停在登录/账号节点 | `debug/maa.log`，启动页/公告/家园截图，任务状态 | 若卡在登录态或公告状态，降级为环境前置不满足；不得修改启动 pipeline 兜底 |
| S2 | 选服 override | Adb 优先 | MFAAvalonia 或 Python Tasker | `晶 19292464450` | `用户切换_账号列表` | `sub_启动杖剑传说官_选择服务器.expected = 晶`；`用户切换_选择账号.expected = 19292464450` | 账号列表存在目标账号；服务器列表可打开；允许观察选服 | 启动账号 task，登录后进入选服，观察目标服务器选择 | 进入 `sub_启动杖剑传说官_选择服务器`，OCR/点击使用服务器 `晶`，随后尝试 `sub_启动杖剑传说官_点击开始` | 服务器列表截图、目标服务器命中截图、日志中的 task/节点顺序 | 若服务器列表滚动失败，只记录 S2 失败或降级；不得折叠 server override |
| S3 | 账号切换 | Adb 优先 | MFAAvalonia 或 Python Tasker | `晶 19292464450` | `用户切换_账号列表` | `用户切换_选择账号.expected = 19292464450`；同时带 S2 的服务器 override | 账号列表中有目标手机号；协议/登录状态可操作；网络正常 | 从账号列表入口启动，观察账号列表、目标账号、协议、登录按钮 | 命中 `用户切换_选择账号` 的目标手机号，完成 `用户切换_点击登录`，进入启动/选服链路 | 账号列表截图、滑动前后截图、目标手机号命中截图、登录后节点日志 | 若目标账号不可见或需验证码/人工登录，记录前置阻塞；不得改账号 expected 覆盖 |
| S4 | 低风险 shop/reward 子 flow | Adb 或 Win32 | MFAAvalonia 或 Python Tasker | `流水线` | `FARM_点击杂货店` | 默认无 task-level override；必要时可用一次性 stop override 限制出口 | 当前在家园或可进入家园；杂货店状态可观察；避免特殊账号路径 | 优先启动 `流水线` 观察完整路径；若会越出 C 边界，可分段观察杂货店入口、商店、宝库、免费体力判断、返回 | 到达 `FARM_点击杂货店` -> `FARM_杂货店商店` -> `FARM_点击宝库` -> `FARM_宝库购买体力` -> `FARM_宝库返回` 中的关键节点；分段时只声明已覆盖段 | 杂货店入口、商店、宝库页面、体力判断和返回截图；日志节点序列；如有运行时 override，记录 override 摘要 | 若进入 `FARM_杂货店购买限购` 自循环或弹窗，记录状态并停止扩大范围；C1 不顺手合并 recovery |
| S5 | 日常子 flow：打野猪 StopTask 覆盖 | Adb 优先 | MFAAvalonia 或 Python Tasker | `打野猪` | `FARM_点击世界` | `FARM_世界返回家园.action = StopTask` | 地图入口可见；角色能打开世界地图；体力和怪物状态可观察 | 启动 `打野猪`，观察世界地图、森之国定位、小地图、野猪识别或找不到野猪路径 | 到达 `FARM_世界返回家园` 后任务停止，不继续默认 `FARM_点击公会` | 地图入口、小地图、森之国定位、野猪/找不到野猪、返回家园、StopTask 日志 | 若地图定位或模板不稳定，记录 V3/V4 降级；不得把 StopTask 覆盖改为默认 FARM 行为 |
| S6 | 活动 flow | Adb 优先 | MFAAvalonia 或 Python Tasker | 首选 `罗小黑联动`；备选 `刷友情币` | `点击罗小黑联动` 或 `开始刷友情点` | 对应 task 为空 override；不改变路径 | 活动开放或可进入；刷友情币需满足组队/副本前置 | 启动单个活动 task，观察入口、关键页面、奖励/战斗/退出循环 | 罗小黑：到达 `点击小黑的冒险` 或 `点击小黑联动_关卡`；友情币：到达 `世界树副本页面` / `战斗结束` / `点击退出` | 活动入口、关键页面、奖励/战斗状态截图，日志节点序列 | 若活动关闭、无组队或状态不可复现，填写活动状态降级；不得同时重构多个活动 |
| S7 | 异常弹窗或 recovery | Adb 或 Win32 | MFAAvalonia 或 Python Tasker + 人工观察 | 优先 `流水线`；可补 `启动杖剑传说官` | `FARM_点击杂货店` 或 `sub_启动杖剑传说官` | 默认无新增 override；如使用账号 task，必须记录原 task override | 能制造或自然遇到礼包/升级礼包/等待/找不到商店等 recovery 状态 | 在目标 task 运行中观察 `启动再等等`、`升级礼包弹窗`、`礼包弹窗`、`FARM_找不到商店`、`FARM_空白处关闭` 等节点是否恢复到原 flow | recovery 处理后回到原模块关键节点，或明确失败并停在可复查状态 | 弹窗前后截图、节点日志、恢复前后页面、人工观察记录 | 若无法触发异常状态，记录“未覆盖 recovery”；不得为了触发 recovery 修改 pipeline 或图片 |

## 特殊账号补验条目

`暖阳 18918203738` 不作为 S4 低风险 shop case 的默认执行对象，但必须进入后续 C1-C4 的风险检查。

| 补验 ID | task | entry | override | 期望观察 | 适用后续任务 |
| --- | --- | --- | --- | --- | --- |
| S5-special | `暖阳 18918203738` | `用户切换_账号列表` | `FARM_宝库购买体力.next` 接 `FARM_宝库购买限购`；`FARM_点击笔记.next` 接每日活动/幻想阶梯；`FARM_家园主界面.next` 接邮件/小推车/切号 | 宝库、笔记、家园收尾三段均按特殊账号路径执行或记录降级 | C1、C2、C3、C4、D3 |

若 C 类任务触及上述节点但没有执行 S5-special，必须在 test/final 中写明降级原因、残余风险和补验条件。

## 执行前检查清单

- 已确认当前 task 来自 `assets/interface.json`，未使用根目录 `interface.json`。
- 已运行或引用 T1 strict JSON 检查。
- 已运行或引用 T2 interface audit，确认 task entry 与 override 目标存在。
- 已运行或引用 T3 pipeline ref 检查，确认引用无悬空。
- 若涉及图片/OCR/ROI，已运行或引用 T4 image usage 检查。
- 若涉及 Python custom agent，已运行或引用 T5 custom 检查，并明确 custom runtime call 未验证。
- 资源变更后已运行 V1：`python .\check_resource.py .\assets\resource\`。
- 真实执行前已确认账号、服务器、活动、页面状态和控制器类型。

## Evidence Template

```text
run_id:
case_id:
date_time:
executor:
git_revision_or_worktree_note:
controller_type: Adb / Win32
execution_method: MFAAvalonia / Python Tasker / manual observation
project_interface_task:
entry:
pipeline_override_summary:
resource_check:
start_condition:
steps_executed:
expected_key_nodes:
actual_key_nodes:
terminal_state:
result: pass / fail / degraded / blocked
evidence_files:
  - debug/maa.log:
  - screenshots:
  - recording:
  - task_return_status:
manual_notes:
residual_risk:
follow_up:
```

证据默认保存在当前 `.agent/tasks/<task-id>/test.md`，或后续 `docs/agent_context/verification_evidence_<YYYY-MM-DD>.md`。截图、录屏和日志路径应在 evidence index 中可回查。不要把单次真实流程日志写入 `AGENTS.md` 或项目 skill。

## Degraded Verification Record

```text
case_id:
原计划验证层: V2 / V3 / V4 / V5
实际验证层: V0 / V1 / V2 / ...
未执行原因:
  - 无设备
  - 无账号状态
  - 无可用窗口
  - 活动关闭
  - 前置页面不可满足
  - 只做文档/模板
  - 其他:
已完成替代验证:
可能漏掉的风险:
补验条件:
建议后续任务:
结论边界:
```

降级记录只能说明当前验证受限，不能把未执行的 V2/V3/V4 写成通过。

## 后续任务消费规则

### C1-shop-flow-pilot

- 默认消费 S4。
- 若触及 `FARM_宝库购买限购` 或特殊账号 `暖阳 18918203738`，必须引用 S5-special 或写降级记录。
- C1 不应混入 S2/S3 账号/选服、不应修改共享图片、不应合并 recovery。
- C1 后续同类 shop 子 flow 可参考 2026-06-14 补验模式：完整 task 优先；若默认 next 会越出 C1 边界，可分段投递 entry，并只用运行时 stop override 限制出口。
- C1 若涉及 OCR/ROI 调整，V4 至少记录截图或日志中的命中文本、box/位置、score，以及 ROI 是否覆盖真实文本。

### C2-reward-cleanup-flow

- 可消费 S4、S7 和 S5-special 的收尾部分。
- 触及 `FARM_空白处关闭`、`红点.png`、邮件/小推车图片族时，需要截图/debug 证据或降级。

### C3-activity-single-flow

- 消费 S6。
- 一次只处理一个 activity flow；活动关闭时必须用降级记录，不应同时改罗小黑和刷友情币。

### C4-farm-daily-subflow

- 消费 S5。
- 地图、野猪模板、托管次数 OCR 需要 V3/V4 或明确降级。

### C5-recovery-node-normalization

- 消费 S7。
- 优先从单模块 recovery 观察开始，不先动登录、选服、账号、地图或活动开放状态相关 recovery。

### C6/C7 account/startup design-only

- C6 消费 S3。
- C7 消费 S1/S2。
- 设计任务不直接修改账号/启动 pipeline；实现诉求应单独 N1 或 C 任务。

### C8-interface-task-generation-poc

- 至少消费 S2 或 S3 中一个带 `pipeline_override` 的路径。
- POC 必须证明 override 保真；不能用 task inventory 替代真实启动或选服/账号观察。

### D3-refactor-playbook

- 将本 smoke plan 转成 C 类任务前置检查表、证据模板和降级记录模板。
- 不反向改变 `assets/interface.json` canonical source、pipeline JSONC 或 override 保留规则。

### T7-ci-readonly-checks

- 可消费 T1-T5 的 V0 hard fail/warning 分类，以及本文档的 evidence/degrade 模板。
- 不应把 S1-S7 真实控制器执行默认接入 CI gate。

## D4 / D5 / N1 判断

- D4：当前暂不需要。T6 任务矩阵能承载 S1-S7、证据模板和降级格式。
- D5：暂不立即触发。本计划复用既有稳定规则：`assets/interface.json` canonical、root `interface.json` 非 canonical、pipeline JSONC 不 strict-format、override 不折叠、真实流程缺失必须降级记录。若 D3 或首个 C 任务把本证据模板固化为长期 playbook，可再检查是否同步 `AGENTS.md` 或项目 skill。
- N1：暂不需要。本文档没有新增“立即执行真实流程”“新增自动化脚本”“修改资源以通过 smoke”的需求；若后续提出，应单独分流。

## V0 文档检查记录

| 检查项 | 结果 |
| --- | --- |
| S1-S7 均已覆盖 | passed |
| 至少一个 case 显式包含 `pipeline_override` | passed，S2/S3 与 S5-special |
| 文档明确 `assets/interface.json` 为 canonical source | passed |
| 文档未使用根目录 `interface.json` 作为运行真相 | passed |
| 文档未把 T1-T5 或 `check_resource.py` 写成 V2/V3/V4 通过 | passed |
| 文档包含证据模板和降级记录格式 | passed |
| 文档未修改运行资源 | passed |
