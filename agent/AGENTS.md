# Python Agent 指南

## 当前角色

`agent/` 是 MaaFramework Python custom action/custom recognition 的入口目录。它不是当前业务 pipeline 的默认主要实现层。

`assets/interface.json` 已配置启动 `{PROJECT_DIR}/agent/main.py`，但业务是否使用 custom action/custom recognition，仍以 `assets/resource/pipeline/` 中是否引用 registered name 为准。

截至 2026-06-06，未证实 pipeline 使用当前 registered names。修改前必须重新搜索引用，不要把 Python agent 简化判断为“没用”，也不要默认它已深度接入业务流程。

## 启动路径

`agent/main.py` 会初始化 Toolkit，读取 MaaFramework 传入的 socket id，并启动 `AgentServer`。

当前 `main.py` 通过 import 加载 `my_action` 与 `my_reco`。这些 import 会触发 decorator 注册 custom action/custom recognition。

不要随意改动 `main.py` 的启动顺序、socket id 读取方式或 `AgentServer.start_up` / `join` / `shut_down` 流程，除非任务明确涉及 MaaFramework agent API 升级或运行时修复。

## 当前注册项

当前已知注册名：

- `地图定位检测`：在 `my_action.py` 中通过 `@AgentServer.custom_action(...)` 注册。
- `my_reco_222`：在 `my_reco.py` 中通过 `@AgentServer.custom_recognition(...)` 注册。

新增、重命名或删除 registered name 前，必须搜索 `assets/interface.json`、`assets/resource/pipeline/` 与 `agent/` 中的引用。

以下命令默认在仓库根目录执行：

```powershell
rg -n "地图定位检测|my_reco_222|新的注册名" assets\interface.json assets\resource\pipeline agent
```

## Pipeline 优先原则

能用 pipeline 稳定表达的自动化优先用 pipeline，例如点击流、OCR、TemplateMatch、简单条件分支、等待和跳转。

只有 pipeline 难以可靠表达时，再使用 Python custom action/custom recognition，例如复杂状态判断、需要组合多次识别的逻辑、或必须调用 MaaFramework context/controller API 的场景。

新增 custom 逻辑时，必须同时明确 pipeline 中的引用节点、传参约定、返回语义、验证方式和手动 debug 路径。

不要新增未被 pipeline 使用的 custom demo、临时 recognition 或孤立 helper，除非任务明确是实验或调研。

## Custom Action / Recognition 边界

custom action 应尽量承担动作或状态处理，不要把可读的 pipeline 点击流整体搬进 Python。

custom recognition 应返回可被 pipeline 消费的识别结果。修改返回结构、box、detail 或 context override 行为前，先确认目标 MaaFramework API 的当前协议。

谨慎使用 `context.override_pipeline`、`context.override_next` 和 controller 直接操作。这些调用可能改变整个 task 的执行路径或绕过 pipeline 中的显式节点。

日志应服务 debug，保持简洁。不要输出敏感账号信息、服务器信息或大量高频噪声。

## 上游对齐提醒

对齐新版 MaaFramework 前，重新确认 Python agent API、`AgentServer` 启动方式、custom action/custom recognition 注册方式、回调参数、返回值协议和运行时 agent binary 要求。

参考 MaaHub 或其他 MaaFramework 项目时，只吸收适合 MaaZJ 的 custom 组织方式和 debug 经验，不要机械复制社区样例中的 registered name、坐标、ROI、业务逻辑或临时代码。

如果升级涉及 MFAAvalonia 的 agent 配置方式，先检查 `assets/interface.json` 的 `agent` 字段是否仍符合新版 ProjectInterface 要求。

## 依赖与运行时

不要随意新增 Python 依赖、修改启动命令或改变运行时路径。涉及依赖时，需要同时考虑打包、`deps/`、CI、MFAAvalonia 启动方式和用户本地环境。

`agent/config/` 与 `agent/debug/` 若用于实验或调试，修改前先确认是否会被运行时读取。不要把临时 debug 数据当作业务配置。

## 验证清单

以下命令默认在仓库根目录执行：

```powershell
rg -n "registered name 或节点名" assets\interface.json assets\resource\pipeline agent
```

修改 custom 逻辑后，至少运行资源检查：

```powershell
python .\check_resource.py .\assets\resource\
```

如果 custom 逻辑被 pipeline 引用，还应安排手动 debug，确认 agent 能启动、registered name 能被调用、返回值能被 pipeline 正确消费。
