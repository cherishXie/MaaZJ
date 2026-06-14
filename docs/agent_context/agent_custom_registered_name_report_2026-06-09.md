# R5 Agent Custom Registered Name Report

Date: 2026-06-09

Source of truth: `assets/interface.json`

Scope: read-only audit for Python custom action / custom recognition registered names and business integration status.

## 结论摘要

- `assets/interface.json` 严格 JSON 解析通过，并配置 Python agent 启动：`child_exec = python`，`child_args = {PROJECT_DIR}/agent/main.py`。
- 当前 `agent/main.py` 会 import `my_action` 与 `my_reco`，这些 import 使两个 decorator 注册项进入 agent 启动链路。
- 当前可识别 registered name 共 2 个：
  - `地图定位检测`：custom action，位于 `agent/my_action.py`。
  - `my_reco_222`：custom recognition，位于 `agent/my_reco.py`。
- 对 `assets/interface.json` 与 `assets/resource/pipeline/` 执行静态引用搜索后，未发现这两个 registered name 的业务 pipeline 引用。
- 本报告不推断 Python agent “没用”，也不建议删除。当前状态应记为：agent 已配置启动，registered name 已注册进入 import 链路，但业务 pipeline 静态接入未证实，且没有 V2/V3/V4 调用证据。

## 输入与边界

读取：

- `AGENTS.md`
- `agent/AGENTS.md`
- `.codex/skills/maazj-maafw-refactor/references/refactor-workflow.md`
- `docs/agent_design/refactor_design_maafw_test_automation_2026-06-07.md`
- `docs/agent_context/PROJECT_UNDERSTANDING_2026-06-06.md`
- `docs/agent_context/interface_inventory_2026-06-08.md`
- `docs/agent_context/pipeline_flow_map_initial_2026-06-09.md`
- `.agent/tasks/2026-06-08-r1-interface-inventory/`
- `.agent/tasks/2026-06-09-r2-pipeline-flow-map-initial/`
- `assets/interface.json`
- `assets/resource/pipeline/`
- `agent/`

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
- 只读搜索 registered name 在 canonical interface、pipeline 与 agent 中的引用。
- 只读检查 `agent/main.py` 的 import 启动链路与 custom decorator 注册点。
- 不执行 MaaFramework resource load。
- 不执行 task entry 启动、真实控制器流程、截图、日志或 debug 调用验证。

## Canonical Agent 启动配置

`assets/interface.json` 是本报告唯一 runtime truth。根目录 `interface.json` 未作为运行真相读取、同步、迁移或修改。

| 字段 | 当前值 | 静态证据 |
| --- | --- | --- |
| `agent.child_exec` | `python` | `assets/interface.json:34` |
| `agent.child_args` | `{PROJECT_DIR}/agent/main.py` | `assets/interface.json:35-36` |

启动链路：

| 文件 | 证据 | 说明 |
| --- | --- | --- |
| `agent/main.py` | `import my_action` at line 6 | import 后触发 custom action decorator 注册 |
| `agent/main.py` | `import my_reco` at line 7 | import 后触发 custom recognition decorator 注册 |
| `agent/main.py` | `AgentServer.start_up(socket_id)` at line 16 | 使用 MaaFramework agent server 启动 |
| `agent/main.py` | `AgentServer.join()` / `AgentServer.shut_down()` at lines 17-18 | agent 生命周期保持模板启动结构 |

## Registered Name 明细

| registered name | 类型 | 注册文件 | 注册方式 | 启动链路 | 当前业务接入状态 |
| --- | --- | --- | --- | --- | --- |
| `地图定位检测` | custom action | `agent/my_action.py` | `@AgentServer.custom_action("地图定位检测")` at line 6；`MyCustomAction.run(...)` at line 9 | `agent/main.py` line 6 import `my_action` | 未发现 `assets/interface.json` 或 pipeline 静态引用；无 V2/V3/V4 调用证据 |
| `my_reco_222` | custom recognition | `agent/my_reco.py` | `@AgentServer.custom_recognition("my_reco_222")` at line 6；`MyRecongition.analyze(...)` at line 9 | `agent/main.py` line 7 import `my_reco` | 未发现 `assets/interface.json` 或 pipeline 静态引用；无 V2/V3/V4 调用证据 |

## Static Reference 搜索结果

执行搜索：

```powershell
rg -n "地图定位检测|my_reco_222" assets\interface.json assets\resource\pipeline agent
```

结果摘要：

| registered name | `assets/interface.json` | `assets/resource/pipeline/` | `agent/` | 结论 |
| --- | --- | --- | --- | --- |
| `地图定位检测` | 未命中 | 未命中 | 命中 `agent/AGENTS.md`、`agent/my_action.py` | 仅注册侧可见，业务静态引用未发现 |
| `my_reco_222` | 未命中 | 未命中 | 命中 `agent/AGENTS.md`、`agent/my_reco.py` | 仅注册侧可见，业务静态引用未发现 |

补充搜索：

```powershell
rg -n "CustomAction|CustomRecognition|custom_action|custom_recognition|recognition\s*[:=]\s*Custom|action\s*[:=]\s*Custom" assets\interface.json assets\resource\pipeline agent
```

结果摘要：

- `assets/interface.json` 未命中 custom action / custom recognition 业务引用。
- `assets/resource/pipeline/` 未命中 custom action / custom recognition 业务引用。
- 命中均在 `agent/AGENTS.md`、`agent/my_action.py`、`agent/my_reco.py`。

## 状态枚举

本报告使用以下状态：

| 状态 | 含义 |
| --- | --- |
| `configured_agent_startup` | canonical `assets/interface.json` 已配置 Python agent 启动 |
| `registered_imported` | registered name 位于 `agent/main.py` import 链路中 |
| `pipeline_static_reference_not_found` | 未在 `assets/interface.json` 或 `assets/resource/pipeline/` 中找到静态业务引用 |
| `runtime_call_unverified` | 未执行 V2/V3/V4，因此没有真实调用证据 |
| `requires_followup_validation` | 后续接入、清理、文档化或测试脚本任务需要继续消费本报告 |

| registered name | 状态 |
| --- | --- |
| `地图定位检测` | `configured_agent_startup`; `registered_imported`; `pipeline_static_reference_not_found`; `runtime_call_unverified`; `requires_followup_validation` |
| `my_reco_222` | `configured_agent_startup`; `registered_imported`; `pipeline_static_reference_not_found`; `runtime_call_unverified`; `requires_followup_validation` |

## Custom 逻辑风险观察

这些是静态观察，不代表运行时已被调用：

- `agent/my_action.py` 的 `MyCustomAction.run(...)` 当前打印日志后 `return False`。若未来接入 pipeline，需要确认 `False` 返回值对调用节点的语义影响。
- `agent/my_reco.py` 的 `MyRecongition.analyze(...)` 当前调用 `context.run_recognition("MyCustomOCR", ...)`、`context.override_pipeline(...)`、`context.tasker.controller.post_click(...)` 与 `context.override_next(...)`，这些行为若被 pipeline 引用，会直接改变识别、点击和后续路径。
- `MyCustomOCR`、`TaskA`、`TaskB` 只在 `agent/my_reco.py` 中出现；本报告未在 pipeline 中验证这些节点存在或可用，因为 `my_reco_222` 本身未发现业务引用。

## 后续任务消费建议

| 后续任务 | 可消费内容 | 建议边界 |
| --- | --- | --- |
| `T5-agent-custom-check-script` | registered name 列表、搜索命令、状态枚举 | 实现只读检查脚本即可，不删除注册项、不改 agent |
| `D2-agent-status-doc` | 当前 Python agent 状态说明 | 文档应写为“已配置启动、业务接入未证实”，不要写成“无用” |
| `C6-account-flow-design-only` | account flow 不依赖当前 registered name 的 V0 结论 | 若未来账号流程要引入 custom，需要单独证明 pipeline 引用与真实调用 |
| `C7-startup-flow-design-only` | startup/server flow 不依赖当前 registered name 的 V0 结论 | 若未来启动/选服要引入 custom，需要定义返回语义和 V2/V3/V4 验证 |

## V0 验证记录

已完成：

- `assets/interface.json` 严格 JSON 解析通过。
- `rg -n "地图定位检测|my_reco_222" assets\interface.json assets\resource\pipeline agent`：
  - `assets/interface.json` 未命中。
  - `assets/resource/pipeline/` 未命中。
  - `agent/` 中命中 registered name 注册和说明。
- `rg -n "CustomAction|CustomRecognition|custom_action|custom_recognition|recognition\s*[:=]\s*Custom|action\s*[:=]\s*Custom" assets\interface.json assets\resource\pipeline agent`：
  - `assets/interface.json` 未命中。
  - `assets/resource/pipeline/` 未命中。
  - `agent/` 中命中注册类和说明。
- `agent/main.py` 当前 import `my_action` 与 `my_reco`，两个 registered name 位于启动 import 链路中。

未执行：

- V1 MaaFramework resource load。本任务未修改资源。
- V2 task entry 启动验证。
- V3 真实控制器流程验证。
- V4 日志、截图或 debug 证据。
- V5 回归矩阵。

## D4/D5/N1 初步判断

- D4：暂不需要。R5 矩阵字段足以承载 registered name、类型、注册文件、pipeline 引用、状态枚举和调用证据缺口。
- D5：暂不需要。当前审计结果没有形成超出现有 `AGENTS.md` / `agent/AGENTS.md` 的新稳定规则；既有“不要简化判断为没用”和“新增 custom 必须有 pipeline 引用与验证”的规则仍适用。
- N1：暂不需要。未提出删除 Python agent、新增 custom、执行真实流程验证或实现 T5 脚本的新需求；这些应分别进入 D2/T5/C6/C7 或单独后续任务。
