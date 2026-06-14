# R1 Interface Inventory

Date: 2026-06-08

Source of truth: `assets/interface.json`

Scope: read-only inventory for ProjectInterface tasks and `pipeline_override`.

## 结论摘要

- `assets/interface.json` 严格 JSON 解析通过。
- 当前 canonical ProjectInterface 中有 35 个 task。
- 顶层 `pipeline_override` 字段覆盖共 64 项；所有 override 目标节点均能在 `assets/resource/pipeline/` 中找到静态定义。
- 所有 `task[].entry` 都能在 `assets/resource/pipeline/` 中找到静态定义。
- 根目录 `interface.json` 未作为运行真相读取、同步、迁移或修改。
- 本报告不证明 V2 task entry 启动、不证明 V3 真实控制器流程，也不证明活动、账号或服务器路径真实可达。

## 顶层 ProjectInterface 摘要

| 字段 | 当前值 |
| --- | --- |
| `name` | `杖剑传说小助手` |
| `custom_title` | `杖剑传说小助手` |
| `version` | `v0.1.0` |
| `controller` | `安卓端` = `Adb`; `桌面端` = `Win32`, `window_regex` = `Visual Studio` |
| `resource` | `官服` 与 `B 服` 均指向 `{PROJECT_DIR}/resource` |
| `agent` | `child_exec` = `python`; `child_args` = `{PROJECT_DIR}/agent/main.py` |

## Task Inventory

风险等级是静态初判，仅用于后续任务排序；不代表真实流程验证结论。

| # | task name | entry | 类型 | override | override 节点数 | entry 静态位置 | 风险 |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| 1 | 罗小黑联动 | 点击罗小黑联动 | activity | yes | 0 | `assets/resource/pipeline/小号/联动活动/罗小黑.json` | medium：活动入口 |
| 2 | 启动杖剑传说官 | sub_启动杖剑传说官 | startup | yes | 0 | `assets/resource/pipeline/start_up.json` | high：启动/选服入口 |
| 3 | 打野猪 | FARM_点击世界 | daily/farm | yes | 1 | `assets/resource/pipeline/小号/地图/打野猪.json` | medium：FARM 子流程入口 |
| 4 | 流水线 | FARM_点击杂货店 | daily/farm | no | 0 | `assets/resource/pipeline/小号/杂货店/杂货店.json` | medium：FARM 子流程入口 |
| 5 | 刷友情币 | 开始刷友情点 | activity | yes | 0 | `assets/resource/pipeline/activity/刷友情币.json` | medium：活动/组队相关入口 |
| 6 | 晶 19292464450 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 7 | 晶 19202585239 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 8 | 晶 19521466084 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 9 | 晶 19229786583 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 10 | 晶 17701717598 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 11 | 晶 15221861705 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 12 | 晶 18918203738 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 13 | 暖阳 19292464450 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 14 | 暖阳 19202585239 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 15 | 暖阳 19521466084 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 16 | 朋克 19292464450 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 17 | 朋克 19202585239 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 18 | 朋克 19521466084 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 19 | 朋克 19229786583 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 20 | 朋克 17701717598 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 21 | 朋克 15221861705 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 22 | 朋克 18918203738 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 23 | 蒸汽 19292464450 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 24 | 蒸汽 19202585239 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 25 | 蒸汽 19521466084 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 26 | 蒸汽 19229786583 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 27 | 蒸汽 17701717598 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 28 | 蒸汽 15221861705 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 29 | 蒸汽 18918203738 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 30 | 蒸汽 13006710920 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 31 | 暖阳 19229786583 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 32 | 暖阳 17701717598 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 33 | 暖阳 15221861705 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 34 | 暖阳 13006710920 | 用户切换_账号列表 | account/server | yes | 2 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override |
| 35 | 暖阳 18918203738 | 用户切换_账号列表 | account/server | yes | 5 | `assets/resource/pipeline/小号/用户.json` | high：账号/服务器 override + 任务专属 next |

## Pipeline Override Matrix

### 空 override 对象

以下 task 显式存在 `pipeline_override` 字段，但对象为空。它们当前不覆盖节点；保留现状，不据此同步或清理配置。

| task | 说明 |
| --- | --- |
| 罗小黑联动 | 空 `pipeline_override` |
| 启动杖剑传说官 | 空 `pipeline_override` |
| 刷友情币 | 空 `pipeline_override` |

### 账号/服务器 override

下表每一行都对应两个覆盖：

- `sub_启动杖剑传说官_选择服务器.expected`：服务器选择，目标节点在 `assets/resource/pipeline/start_up.json`。
- `用户切换_选择账号.expected`：账号选择，目标节点在 `assets/resource/pipeline/小号/用户.json`。

禁止折叠原因：服务器和账号值直接改变登录、选服、切号路径。没有生成器或受支持 MFAAvalonia 配置机制前，不能把重复视为可删除。

| task | server expected | account expected | 额外 override |
| --- | --- | --- | --- |
| 晶 19292464450 | 晶 | 19292464450 | - |
| 晶 19202585239 | 晶 | 19202585239 | - |
| 晶 19521466084 | 晶 | 19521466084 | - |
| 晶 19229786583 | 晶 | 19229786583 | - |
| 晶 17701717598 | 晶 | 17701717598 | - |
| 晶 15221861705 | 晶 | 15221861705 | - |
| 晶 18918203738 | 晶 | 18918203738 | - |
| 暖阳 19292464450 | 暖阳 | 19292464450 | - |
| 暖阳 19202585239 | 暖阳 | 19202585239 | - |
| 暖阳 19521466084 | 暖阳 | 19521466084 | - |
| 朋克 19292464450 | 朋克 | 19292464450 | - |
| 朋克 19202585239 | 朋克 | 19202585239 | - |
| 朋克 19521466084 | 朋克 | 19521466084 | - |
| 朋克 19229786583 | 朋克 | 19229786583 | - |
| 朋克 17701717598 | 朋克 | 17701717598 | - |
| 朋克 15221861705 | 朋克 | 15221861705 | - |
| 朋克 18918203738 | 朋克 | 18918203738 | - |
| 蒸汽 19292464450 | 蒸汽 | 19292464450 | - |
| 蒸汽 19202585239 | 蒸汽 | 19202585239 | - |
| 蒸汽 19521466084 | 蒸汽 | 19521466084 | - |
| 蒸汽 19229786583 | 蒸汽 | 19229786583 | - |
| 蒸汽 17701717598 | 蒸汽 | 17701717598 | - |
| 蒸汽 15221861705 | 蒸汽 | 15221861705 | - |
| 蒸汽 18918203738 | 蒸汽 | 18918203738 | - |
| 蒸汽 13006710920 | 蒸汽 | 13006710920 | - |
| 暖阳 19229786583 | 暖阳 | 19229786583 | - |
| 暖阳 17701717598 | 暖阳 | 17701717598 | - |
| 暖阳 15221861705 | 暖阳 | 15221861705 | - |
| 暖阳 13006710920 | 暖阳 | 13006710920 | - |
| 暖阳 18918203738 | 暖阳 | 18918203738 | `FARM_宝库购买体力.next`; `FARM_点击笔记.next`; `FARM_家园主界面.next` |

### 非账号/服务器特殊 override

| task | override path | 覆盖字段 | 覆盖值 | 目标节点静态位置 | 语义 | 禁止折叠原因 |
| --- | --- | --- | --- | --- | --- | --- |
| 打野猪 | `FARM_世界返回家园` | `action` | `StopTask` | `assets/resource/pipeline/小号/地图/打野猪.json` | 任务终止点 | `StopTask` 会改变终止行为 |
| 暖阳 18918203738 | `FARM_宝库购买体力` | `next` | `FARM_宝库购买限购` -> `FARM_宝库返回` | `assets/resource/pipeline/小号/杂货店/杂货店.json` | 任务专属下游路径 | `next` 覆盖会改变执行路径，需要单独 V2/V3 验证 |
| 暖阳 18918203738 | `FARM_点击笔记` | `next` | `FARM_点击每日活动` -> `FARM_点击幻想阶梯` | `assets/resource/pipeline/小号/笔记/笔记.json` | 任务专属下游路径 | `next` 覆盖会改变执行路径，需要单独 V2/V3 验证 |
| 暖阳 18918203738 | `FARM_家园主界面` | `next` | `判断是否有新邮件` -> `领取小推车` -> `用户切换_点击菜单` | `assets/resource/pipeline/小号/商城/商城.json` | 任务专属下游路径 | `next` 覆盖会改变执行路径，需要单独 V2/V3 验证 |

## Entry 异常清单

未发现 missing entry。35 个 `task[].entry` 均能在 `assets/resource/pipeline/` 中找到静态节点定义。

## R2 Follow-up 候选

- 高优先级：`用户切换_账号列表` -> 账号切换 -> 启动/选服链路。原因：30 个 account/server task 依赖同一 entry 与不同 override。
- 高优先级：`sub_启动杖剑传说官` 与 `sub_启动杖剑传说官_选择服务器`。原因：启动与选服对账号任务和 standalone 启动任务都有影响。
- 高优先级：`暖阳 18918203738` 的 3 个 `next` 覆盖。原因：除账号/服务器外还改变 FARM 下游路径。
- 中优先级：`FARM_点击世界` / `FARM_世界返回家园`。原因：`打野猪` 使用 `StopTask` 终止覆盖。
- 中优先级：`FARM_点击杂货店`。原因：`流水线` 为 FARM 子流程入口，且和特殊账号的 `FARM_宝库购买体力.next` 相关。
- 中优先级：`点击罗小黑联动`、`开始刷友情点`。原因：活动入口受活动状态和前置条件影响。

## 验证记录

V0 已完成：

- 严格 JSON 解析 `assets/interface.json`。
- task inventory 行数 = 35，与当前 `task[]` 数量一致。
- override 字段覆盖数 = 64。
- entry missing 数 = 0。
- override target missing 数 = 0。

未执行：

- V1 MaaFramework resource load。本任务未修改资源；参考 R0 baseline 中 `python .\check_resource.py .\assets\resource\` 通过，resource hash 为 `387624f731808bde`。
- V2 task entry 启动验证。
- V3 真实控制器流程验证。
- V4 日志、截图或 debug 证据。
- V5 回归矩阵。

## D4/D5/N1 初步判断

- D4：暂不需要。R1 提示词字段足以记录 task inventory、override matrix 和 entry 异常清单。
- D5：暂不需要。本任务没有发现需要同步到 `AGENTS.md` 或项目 skill 的新稳定规则。
- N1：暂不需要。未实现生成器、未修改 task、未同步 root `interface.json`，也未提出真实流程执行新需求。
