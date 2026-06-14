# MaaZJ Verification Evidence 2026-06-14

本文记录 2026-06-14 对 V3: 真实控制器流程验证条件的补验结果。运行真相以 `assets/interface.json` 为准，未使用根目录 `interface.json`。

## Run: 2026-06-14-s1-startup-adb-mumu-r2

| 字段 | 内容 |
| --- | --- |
| case_id | S1 |
| 验证目标 | 启动到首页；若未登录，记录停在登录/账号节点 |
| controller_type | Adb |
| execution_method | Python Tasker |
| task / entry | `启动杖剑传说官` / `sub_启动杖剑传说官` |
| 设备 | MuMu 主实例 `0`，`127.0.0.1:16384` |
| 资源 | `assets/resource` |
| 结果 | `degraded` |
| 边界 | 入口可启动，真实控制器可连接，但 180 秒内未到达登录节点或首页节点 |

实际节点：

- `sub_启动杖剑传说官`
- 多次 `启动再等等`
- 180 秒后手动 `post_stop`

证据：

- 日志：`install/debug/maa.log`
- 截图：
  - `docs/agent_context/evidence/2026-06-14-s1-startup-adb-mumu-r2.png`
  - `docs/agent_context/evidence/2026-06-14-s1-startup-adb-mumu-r2-after45s.png`
  - `docs/agent_context/evidence/2026-06-14-s1-startup-adb-mumu-r2-after135s.png`

观察：

- 初始截图停在“健康游戏忠告”黑屏页。
- 45 秒后进入游戏初始化加载页。
- 135 秒后停在雷霆登录弹窗。

结论边界：

- 该 run 证明 `StartApp` 能启动 `com.leiting.zjcs`，并且 MuMu Adb 控制器可用。
- 该 run 不证明 S1 到首页通过。
- 该 run 的降级原因是启动后加载耗时与未登录前置状态导致 180 秒内未到达目标节点。

## Run: 2026-06-14-s1-startup-adb-mumu-login-state-r3

| 字段 | 内容 |
| --- | --- |
| case_id | S1 |
| 验证目标 | 未登录状态下记录停在登录/账号节点 |
| controller_type | Adb |
| execution_method | Python Tasker |
| task / entry | `启动杖剑传说官` / `sub_启动杖剑传说官` |
| 设备 | MuMu 主实例 `0`，`127.0.0.1:16384` |
| 资源 | `assets/resource` |
| 结果 | `pass with boundary` |
| 边界 | 通过范围限定为“真实控制器启动到登录节点并终止”；未覆盖进入首页 |

实际节点：

- `sub_启动杖剑传说官`
- `用户切换_点击雷霆账密登录`
- `用户流水线终止`

关键日志位置：

- `install/debug/maa.log:5953`：`MaaTaskerPostTask` 启动 `sub_启动杖剑传说官`。
- `install/debug/maa.log:5994`：执行 `StartApp`，目标 package 为 `com.leiting.zjcs`。
- `install/debug/maa.log:6028`：OCR 命中 `雷霆账密登录`。
- `install/debug/maa.log:6029`：节点命中 `用户切换_点击雷霆账密登录`。
- `install/debug/maa.log:6040`：节点命中 `用户流水线终止`。
- `install/debug/maa.log:6058`：`Tasker.Task.Succeeded`。

证据：

- 日志：`install/debug/maa.log`
- 截图：`docs/agent_context/evidence/2026-06-14-s1-startup-adb-mumu-login-state-r3.png`
- 前台窗口：`com.leiting.zjcs/com.leiting.unity.AppActivity`

结论边界：

- 当前已补齐 S1 的 V3/V4 最低可复查证据：真实 Adb 控制器可连接，task entry 可启动，流程能到达未登录状态下的账号登录节点并终止。
- 仍未证明“已登录账号进入首页”路径，也未覆盖 S2/S3 账号和选服 override、S4 shop、S5 日常、S6 活动或 S7 recovery。

## 后续补验条件

- 若要把 S1 从 `pass with boundary` 提升为完整通过，需要准备已登录账号状态，或允许人工完成登录后再执行 S1，观察 `登录进入主家园界面` / `家园图标.png`。
- S2/S3 需要明确目标账号、服务器和登录前置条件。
- S4 及后续 C 类任务应继续引用 `docs/agent_design/real_flow_smoke_plan_2026-06-14.md`，并在对应任务的 `test.md` 或后续 evidence index 中记录 V2/V3/V4。
