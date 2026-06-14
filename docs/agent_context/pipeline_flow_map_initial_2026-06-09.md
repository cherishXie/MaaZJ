# R2 Pipeline Flow Map Initial

Date: 2026-06-09

Source of truth: `assets/interface.json`

Scope: read-only initial flow map for key MaaZJ pipeline entries.

## 结论摘要

- 当前 canonical ProjectInterface 仍以 `assets/interface.json` 为准；本报告未读取、同步、迁移或修改根目录 `interface.json`。
- R1 已确认当前有 35 个 task；R2 观察到 entry 实际分为 6 组：`点击罗小黑联动`、`sub_启动杖剑传说官`、`FARM_点击世界`、`FARM_点击杂货店`、`开始刷友情点`、`用户切换_账号列表`。
- 本报告覆盖 R1 follow-up 标记的高/中优先级 flow：启动/选服、账号切换、FARM 杂货店/宝库、打野猪、特殊账号 `next` 覆盖、罗小黑联动、刷友情币。
- 账号/服务器 task 的真实路径必须叠加 `pipeline_override` 理解：`sub_启动杖剑传说官_选择服务器.expected` 决定服务器，`用户切换_选择账号.expected` 决定账号。
- `暖阳 18918203738` 除账号/服务器 override 外，还覆盖 `FARM_宝库购买体力.next`、`FARM_点击笔记.next`、`FARM_家园主界面.next`，应单独进入后续 smoke 候选。
- 未执行 V1-V5。本报告只证明静态 flow map 初步可追踪，不证明 task 能启动或真实流程可达。

## 输入与边界

读取：

- `AGENTS.md`
- `assets/resource/pipeline/AGENTS.md`
- `docs/agent_context/PROJECT_UNDERSTANDING_2026-06-06.md`
- `docs/agent_context/interface_inventory_2026-06-08.md`
- `assets/interface.json`
- `assets/resource/pipeline/` 中 R1 follow-up 相关文件

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
- 只读搜索/读取 pipeline 节点和关键边。
- 抽查关键 `next`、`interrupt` 目标节点存在。
- 不 strict-format pipeline，不删除注释，不解析为严格 JSON。

## Entry 分组

| entry | task 数 | 代表 task | 类型 | 主要文件 |
| --- | ---: | --- | --- | --- |
| `点击罗小黑联动` | 1 | `罗小黑联动` | activity | `assets/resource/pipeline/小号/联动活动/罗小黑.json` |
| `sub_启动杖剑传说官` | 1 | `启动杖剑传说官` | startup | `assets/resource/pipeline/start_up.json` |
| `FARM_点击世界` | 1 | `打野猪` | daily/farm | `assets/resource/pipeline/小号/地图/打野猪.json` |
| `FARM_点击杂货店` | 1 | `流水线` | daily/farm | `assets/resource/pipeline/小号/杂货店/杂货店.json` |
| `开始刷友情点` | 1 | `刷友情币` | activity | `assets/resource/pipeline/activity/刷友情币.json` |
| `用户切换_账号列表` | 30 | server/account tasks | account/server | `assets/resource/pipeline/小号/用户.json` |

## Flow Map 初版

### S1/S2 启动与选服 flow

- 入口 task：`启动杖剑传说官`
- entry：`sub_启动杖剑传说官`
- 关键节点：
  - `sub_启动杖剑传说官`：`StartApp`，package `com.leiting.zjcs`。
  - `用户切换_点击雷霆账密登录`：位于 `小号/用户.json`，从启动后进入账密登录判断；其默认 `next` 是 `用户流水线终止`。
  - `sub_启动杖剑传说官_关闭公告`：OCR `公告`，关闭公告后进入切换服务器。
  - `sub_启动杖剑传说官_切换服务器`：OCR `服务器`，点击进入服务器列表。
  - `sub_启动杖剑传说官_服务器列表`：OCR `角色列表`，`interrupt` 包含 `执行滑动`。
  - `sub_启动杖剑传说官_选择服务器`：默认 OCR expected `暖阳`，账号/server task 会通过 override 改成 `晶`、`暖阳`、`朋克`、`蒸汽`。
  - `sub_启动杖剑传说官_点击开始`：OCR `健康游戏忠告`，进入 `登录进入主家园界面`。
  - `登录进入主家园界面`：位于 `小号/杂货店/杂货店.json`，TemplateMatch `家园图标.png`，默认进入 `FARM_点击杂货店`。
- 主要路径：
  - `sub_启动杖剑传说官` -> `用户切换_点击雷霆账密登录`
  - 账号登录后可进入 `sub_启动杖剑传说官_关闭公告` -> `sub_启动杖剑传说官_切换服务器` -> `sub_启动杖剑传说官_服务器列表` -> `sub_启动杖剑传说官_选择服务器` -> `sub_启动杖剑传说官_点击开始` -> `登录进入主家园界面` -> `FARM_点击杂货店`
- interrupt / recovery 候选：
  - 多数启动节点包含 `启动再等等`。
  - `sub_启动杖剑传说官_服务器列表` 可被 `执行滑动` 打断，用于服务器列表滚动。
  - `sub_启动杖剑传说官_点击开始` interrupt 引用自身，表现为等待/重试开始点击。
- 出口/停止点：
  - standalone 启动 flow 最终进入 `FARM_点击杂货店`，不是独立 StopTask。
  - `sub_关闭杖剑传说官` 是独立 StopApp 节点，当前 R2 追踪路径未从 task entry 直接进入它。
- override 影响：
  - 30 个 account/server task 均覆盖 `sub_启动杖剑传说官_选择服务器.expected`。
- unknown：
  - `sub_启动杖剑传说官` 直接 `next` 到 `用户切换_点击雷霆账密登录` 后默认会 `用户流水线终止`；实际 standalone 启动如何从登录态进入关闭公告/选服，需要 V2/V3 观察。

### S3 账号切换 flow

- 入口 task：30 个账号/服务器 task。
- entry：`用户切换_账号列表`
- 关键节点：
  - `用户切换_账号列表`：OCR `雷霆账号登录`，点击账号列表，进入 `用户切换_选择账号`。
  - `用户切换_选择账号`：默认 OCR expected `18918203738`，由每个账号 task 覆盖为目标手机号。
  - `用户切换_同意协议`：坐标点击，进入登录。
  - `用户切换_点击登录`：OCR `雷霆账号登录`，登录后进入 `sub_启动杖剑传说官_关闭公告` 或 `sub_启动杖剑传说官_切换服务器`。
  - 登录后复用启动/选服 flow。
- 主要路径：
  - `用户切换_账号列表` -> `用户切换_选择账号` -> `用户切换_同意协议` -> `用户切换_点击登录` -> `sub_启动杖剑传说官_关闭公告` / `sub_启动杖剑传说官_切换服务器` -> 选服 -> 开始 -> 家园 -> FARM。
- interrupt / recovery 候选：
  - `用户切换_账号列表` interrupt 包含 `用户执行滑动`，用于账号列表滚动。
  - 登录相关节点普遍包含 `启动再等等`。
- 出口/停止点：
  - 账号切换 task 本身没有直接 StopTask；登录后衔接启动/选服和后续 FARM。
  - `用户流水线终止` 是 `用户切换_点击雷霆账密登录` 的默认 StopTask，但不是账号列表 entry 主路径的正常出口。
- override 影响：
  - `用户切换_选择账号.expected` 按 task 覆盖为手机号。
  - `sub_启动杖剑传说官_选择服务器.expected` 按 task 覆盖为服务器。
- unknown：
  - 账号列表滚动与目标账号定位是否稳定，需要 V3/V4 真实截图或日志验证。

### S4 FARM 杂货店/宝库 flow

- 入口 task：`流水线`
- entry：`FARM_点击杂货店`
- 关键节点：
  - `登录进入主家园界面`：识别家园后进入 `FARM_点击杂货店`。
  - `FARM_点击杂货店`：TemplateMatch `杂货店.png` / `杂货店_晚上.png`。
  - `FARM_杂货店商店`：OCR `商店`，进入 `FARM_杂货店购买限购` 或 `FARM_点击宝库`。
  - `FARM_杂货店购买限购`：循环购买限购后回到商店判断。
  - `FARM_点击宝库`：OCR `宝库`，进入 `FARM_宝库购买体力`。
  - `FARM_宝库购买体力`：默认 OCR `免费`，默认 `next` 是 `FARM_宝库返回`。
  - `FARM_宝库返回`：返回后进入 `FARM_点击公会`。
  - `FARM_点击公会`：跨到公会模块，后续可到 `FARM_点击笔记`。
- 主要路径：
  - `FARM_点击杂货店` -> `FARM_杂货店商店` -> `FARM_杂货店购买限购` / `FARM_点击宝库` -> `FARM_宝库购买体力` -> `FARM_宝库返回` -> `FARM_点击公会`
- interrupt / recovery 候选：
  - `FARM_点击杂货店` interrupt 包含 `升级礼包弹窗`、`礼包弹窗`、自身和 `启动再等等`。
  - `FARM_杂货店商店`、`FARM_杂货店购买限购` interrupt 包含 `FARM_找不到商店`。
- 出口/停止点：
  - 默认流不在宝库停止，而是进入公会模块。
- override 影响：
  - `暖阳 18918203738` 将 `FARM_宝库购买体力.next` 从默认 `FARM_宝库返回` 改为 `FARM_宝库购买限购` -> `FARM_宝库返回`。
- unknown：
  - `FARM_杂货店购买限购` 是自循环候选，实际何时退出依赖识别状态；R2 不判断稳定性。

### S5 特殊账号 FARM override flow

- 入口 task：`暖阳 18918203738`
- entry：`用户切换_账号列表`
- 特殊覆盖：
  - `FARM_宝库购买体力.next`：`FARM_宝库购买限购` -> `FARM_宝库返回`
  - `FARM_点击笔记.next`：`FARM_点击每日活动` -> `FARM_点击幻想阶梯`
  - `FARM_家园主界面.next`：`判断是否有新邮件` -> `领取小推车` -> `用户切换_点击菜单`
- 影响路径：
  - 宝库阶段会多走 `FARM_宝库购买限购`。
  - 笔记阶段默认 `FARM_点击笔记` 只进入 `FARM_点击竞技`；特殊账号改成每日活动/幻想阶梯路径。
  - 家园收尾阶段默认 `FARM_家园主界面` 进入 `FARM_收经验` / `FARM_无需收经验`；特殊账号改成邮件、小推车、切号菜单。
- 关键下游：
  - `FARM_点击每日活动` -> `FARM_进入每日活动` -> `FARM_进入圣兽页面` -> `FARM_匹配圣兽` -> `FARM_返回笔记首页` -> `FARM_点击幻想阶梯`
  - `FARM_点击幻想阶梯` -> `FARM_进入幻想阶梯` -> 挑战/一键/切回 -> `FARM_幻想阶梯返回2` -> `FARM_点击地图探索`
  - `判断是否有新邮件` -> `FARM_邮件页面` -> `FARM_领取邮件` / `FARM_无需领取邮件` -> `领取小推车` / `用户切换_点击菜单`
  - `领取小推车` 可进入樱花树、绯乐、资源领取、最终回到 `用户切换_点击菜单`。
- interrupt / recovery 候选：
  - 特殊覆盖目标下游普遍包含 `启动再等等`、礼包弹窗、返回首页等恢复节点。
- 出口/停止点：
  - 特殊账号收尾明显更早接到 `用户切换_点击菜单`，使账号切换成为后续候选出口。
- unknown：
  - 特殊账号是否意图跳过竞技/收经验，R2 只记录 override 事实，不做业务正确性判断。

### S6 打野猪 flow

- 入口 task：`打野猪`
- entry：`FARM_点击世界`
- 关键节点：
  - `FARM_点击世界`：TemplateMatch 地图图标，进入世界首页。
  - `FARM_世界首页`：TemplateMatch `地图宝箱.png`，进入 `FARM_定位到森之国`。
  - `FARM_定位到森之国` / `FARM_到达森之国` / `FARM_点击小地图` / `FARM_小地图页面`：定位地图与小地图。
  - `FARM_寻找森之国二`：进入 `FARM_定位到森之国二` 或 `FARM_定位到森之国一`，通过滑动 interrupt 辅助定位。
  - `FARM_返回到地图中` -> `FARM_循环打野猪`。
  - `FARM_打野猪`：TemplateMatch 野猪，进入体力判断、托管、继续打或找不到野猪。
  - `FARM_找不到野猪` / `FARM_体力不足`：进入 `FARM_世界返回家园`。
  - `FARM_世界返回家园`：默认返回后进入 `FARM_点击公会`。
- 主要路径：
  - `FARM_点击世界` -> 地图定位 -> `FARM_循环打野猪` -> `FARM_打野猪` / `FARM_找不到野猪` -> `FARM_世界返回家园`
- interrupt / recovery 候选：
  - 地图定位大量依赖滑动节点：`执行横向左滑动`、`执行横向右滑动`、`执行横向下滑动`。
  - `FARM_循环打野猪` 通过 interrupt 触发 `FARM_打野猪`。
  - 托管路径经 `FARM_AUTO`、`FARM_托管页面`、`FARM_托管增加次数`、`FARM_开始托管` 回到 `FARM_AUTO`。
- 出口/停止点：
  - 默认 `FARM_世界返回家园` 进入 `FARM_点击公会`。
  - `打野猪` task 覆盖 `FARM_世界返回家园.action = StopTask`，因此该 task 的实际终止点是 `FARM_世界返回家园`。
- override 影响：
  - `FARM_世界返回家园` 的动作从 Click 改为 StopTask，终止行为改变明显，应单独 smoke。
- unknown：
  - 地图定位与野猪识别依赖多个模板和 ROI，R2 不做图片完整性审计；R4 才主产出 image usage report。

### S7 活动 flow：罗小黑联动

- 入口 task：`罗小黑联动`
- entry：`点击罗小黑联动`
- 关键节点：
  - `点击罗小黑联动`：OCR `联动开启中`，进入 `点击小黑的冒险`。
  - `点击小黑的冒险`：TemplateMatch `小黑的冒险.png`，进入关卡。
  - `点击小黑联动_关卡`：TemplateMatch `红点.png`，自循环；interrupt 承担任务状态、对话、聊天、奖励、困难模式点击。
  - `小黑联动任务中状态文字`：OCR `进入` / `开始战斗`。
  - `对话继续`、`聊天继续`、`获得奖励`、`小黑活动点击困难`：活动内推进/收尾候选。
- 主要路径：
  - `点击罗小黑联动` -> `点击小黑的冒险` -> `点击小黑联动_关卡`，后续由 interrupt 推进战斗、对话和奖励。
- interrupt / recovery 候选：
  - `点击小黑联动_关卡` 的 interrupt 是该活动的主要分支集合。
- 出口/停止点：
  - 未看到明确 StopTask；活动关卡节点自循环，实际终止依赖活动状态与 interrupt 推进。
- override 影响：
  - task 具有空 `pipeline_override`，当前不改变路径。
- unknown：
  - 活动是否仍开放、红点/奖励状态是否存在，只能通过 V3/V4 验证。

### S7 活动 flow：刷友情币

- 入口 task：`刷友情币`
- entry：`开始刷友情点`
- 关键节点：
  - `开始刷友情点`：OCR `世界树`，进入 `点击世界树副本` 或 `点击接受`。
  - `点击世界树副本`：TemplateMatch `世界树.png`。
  - `世界树副本页面`：OCR `进入副本`，可继续页面、接受或等待战斗结束。
  - `点击准备`：TemplateMatch `准备按钮.png`，作为 interrupt。
  - `点击接受`：TemplateMatch `接受按钮.png`，进入 `战斗结束`。
  - `战斗结束`：OCR `掉落奖励`，进入 `点击退出`。
  - `点击退出`：返回后进入 `开始刷友情点`，形成循环。
  - `确定退出`：OCR `确定`，用于退出确认。
- 主要路径：
  - `开始刷友情点` -> `点击世界树副本` -> `世界树副本页面` / `点击接受` -> `战斗结束` -> `点击退出` -> `开始刷友情点`
- interrupt / recovery 候选：
  - 多个节点 interrupt `点击准备`、`点击接受`、`确定退出`，表现为活动副本内的等待/确认循环。
- 出口/停止点：
  - 未看到明确 StopTask；默认是刷友情点循环。
- override 影响：
  - task 具有空 `pipeline_override`，当前不改变路径。
- unknown：
  - 任务说明要求提前组队和副本入口准备；R2 无法证明这些前置条件满足。

## 跨模块边候选

这些只是候选边，最终 module boundary 由 R7 生产。

| 来源节点 | 目标节点 | 来源模块 | 目标模块 | 说明 |
| --- | --- | --- | --- | --- |
| `用户切换_点击登录` | `sub_启动杖剑传说官_关闭公告` / `sub_启动杖剑传说官_切换服务器` | 用户 | startup | 账号登录后进入启动/选服链路 |
| `sub_启动杖剑传说官_点击开始` | `登录进入主家园界面` | startup | 杂货店/FARM | 启动进入家园后默认接 FARM |
| `登录进入主家园界面` | `FARM_点击杂货店` | startup/FARM | 杂货店 | 日常默认入口 |
| `FARM_宝库返回` | `FARM_点击公会` | 杂货店 | 公会 | 杂货店结束后进入公会 |
| `FARM_世界返回家园` | `FARM_点击公会` | 地图 | 公会 | 打野猪默认返回后进入公会，`打野猪` task 会覆盖为 StopTask |
| `FARM_无公会` / 公会后续节点 | `FARM_点击笔记` | 公会 | 笔记 | 公会路径结束后进入笔记 |
| `FARM_返回主家园` | `FARM_家园主界面` | 商城 | 床/收尾 | 返回家园后进入收经验/收尾 |
| `FARM_家园主界面` | `判断是否有新邮件` / `领取小推车` / `用户切换_点击菜单` | 商城/家园 | 床/邮件/用户 | 特殊账号覆盖会直接接收尾 |
| `FARM_点击笔记` | `FARM_点击每日活动` / `FARM_点击幻想阶梯` | 笔记 | 圣兽/幻想阶梯 | 特殊账号覆盖新增 |

## Recovery / interrupt 候选

这些只是候选，完整 recovery path catalog 由 R3 生产。

| 候选 | 出现位置 | 作用初判 |
| --- | --- | --- |
| `启动再等等` | 启动、用户、FARM、活动多处 | 等待界面稳定或延迟重试的通用恢复节点 |
| `执行滑动` | 启动服务器列表 | 服务器列表滚动 |
| `用户执行滑动` | 账号列表 | 账号列表滚动 |
| `升级礼包弹窗` / `礼包弹窗` | 家园、杂货店、床、小推车 | 弹窗关闭 |
| `FARM_找不到商店` | 杂货店 | 商店识别失败时回点入口 |
| `FARM_世界返回家园` 自 interrupt | 打野猪返回 | 返回动作重试；在 `打野猪` task 中被 StopTask override 改变语义 |
| `FARM_空白处关闭` | 公会 | 关闭奖励/领取类弹窗 |
| `点击准备` / `点击接受` / `确定退出` | 刷友情币 | 副本等待、接受、退出确认 |
| `小黑联动任务中状态文字` / `对话继续` / `聊天继续` / `获得奖励` | 罗小黑联动 | 活动任务推进与奖励处理 |

## Unknown 节点清单

| unknown | 原因 | 建议后续 |
| --- | --- | --- |
| standalone `启动杖剑传说官` 的真实完成条件 | entry 后先到 `用户切换_点击雷霆账密登录`，默认可 StopTask；登录态/未登录态下是否继续选服需真实观察 | S1/S2 做 V2/V3 |
| 账号列表滚动与手机号选择稳定性 | 依赖 OCR、列表位置和 `用户执行滑动` | S3 做 V3/V4 |
| `FARM_杂货店购买限购` 自循环退出条件 | 取决于商店 OCR 状态 | R3/T6 后续抽查 |
| `FARM_点击笔记` 默认注释分支 | 文件中保留了注释掉的 `FARM_点击幻想阶梯` 分支；特殊账号 override 又重新接入幻想阶梯 | R7/R8 判断模块边界与试点时关注 |
| 罗小黑联动终止条件 | 活动关卡自循环，未见 StopTask | S7 活动验证或后续活动任务审计 |
| 刷友情币终止条件 | `点击退出` 后回到 `开始刷友情点`，未见 StopTask | S7 活动验证或后续活动任务审计 |
| 图片/OCR/ROI 资源完整性 | R2 只记录关键引用，不审计所有图片文件 | R4 主审计 |

## S1-S7 真实流程验证候选点

| 编号 | 候选点 | 建议层级 | 入口 task | 预期观察 | 残余风险 |
| --- | --- | --- | --- | --- | --- |
| S1 | 启动进入主界面 | V2/V3/V4 | `启动杖剑传说官` | app 启动，经过公告/开始，识别 `家园图标.png` | 登录态差异可能改变路径 |
| S2 | 选服 override | V3/V4 | 任一账号/server task | `sub_启动杖剑传说官_选择服务器.expected` 使用 task 覆盖值 | 服务器列表滚动和 OCR 可能不稳定 |
| S3 | 账号切换 | V3/V4 | 任一 `用户切换_账号列表` task | 目标手机号被选中并进入登录 | 账号列表位置、协议勾选、登录等待 |
| S4 | FARM 杂货店入口 | V2/V3 | `流水线` | 从 `FARM_点击杂货店` 到宝库、公会 | 商店限购循环与弹窗 |
| S5 | 特殊账号 FARM override | V2/V3/V4 | `暖阳 18918203738` | 宝库多走限购；笔记进入每日活动/幻想阶梯；家园直接进邮件/小推车/切号 | 覆盖跨多个模块，需单独证据 |
| S6 | 打野猪 StopTask 覆盖 | V2/V3/V4 | `打野猪` | 到 `FARM_世界返回家园` 后 StopTask，不继续公会 | 地图定位、野猪模板、体力状态 |
| S7 | 活动入口 | V2/V3/V4 | `罗小黑联动` / `刷友情币` | 活动入口能进入关键页面；刷友情币能循环副本 | 活动开放状态、组队前置、奖励状态 |

## V0 验证记录

已完成：

- `assets/interface.json` 严格 JSON 解析。
- entry 分组与 R1 一致：6 个 unique entry，35 个 task。
- 抽查关键入口均在 pipeline 中找到：
  - `sub_启动杖剑传说官`
  - `用户切换_账号列表`
  - `FARM_点击杂货店`
  - `FARM_点击世界`
  - `点击罗小黑联动`
  - `开始刷友情点`
- 抽查关键 `next` / `interrupt` 目标节点存在：
  - `sub_启动杖剑传说官_选择服务器`
  - `登录进入主家园界面`
  - `用户切换_选择账号`
  - `FARM_宝库购买限购`
  - `FARM_点击公会`
  - `FARM_点击每日活动`
  - `FARM_点击幻想阶梯`
  - `判断是否有新邮件`
  - `领取小推车`

未执行：

- V1 MaaFramework resource load。本任务未修改资源。
- V2 task entry 启动验证。
- V3 真实控制器流程验证。
- V4 日志、截图或 debug 证据。
- V5 回归矩阵。

## D4/D5/N1 初步判断

- D4：暂不需要。R2 提示词足以承载 flow map 初版、S1-S7 候选、unknown、跨模块边和 recovery 候选。
- D5：暂不需要。本任务没有发现需要同步到 `AGENTS.md` 或项目 skill 的新稳定规则；既有 canonical、JSONC、override 保留规则仍适用。
- N1：暂不需要。未提出实现生成器、修改 pipeline、执行真实控制器流程或选择 C 类试点的新需求；这些应分别进入 R3/R4/R7/R8/T6/C 类后续任务。
