# MaaZJ Agent 指南

最高优先级：运行与发布配置以 `assets/interface.json` 为准。不要把根目录 `interface.json` 当作 canonical 配置，除非任务明确要求处理它。`install.py` 会复制 `assets/interface.json` 到 `install/interface.json`，并使用 `json.load` 读取，因此 `assets/interface.json` 必须保持严格 JSON。

## 项目定位

MaaZJ 是 MaaFramework 资源项目，不是传统应用代码库。主要业务行为由 `assets/interface.json`、`assets/resource/pipeline/` 与 `assets/resource/image/` 决定；Python agent 已配置启动，但业务接入需核实。

进入仓库后，先把它理解为资源包与 ProjectInterface 的组合：MFAAvalonia 读取 interface 配置，加载 resource bundle，然后由 MaaFramework 执行 pipeline。

长期目标：重构后的项目应对齐 MaaXYZ/MaaFramework、MaaXYZ/MFAAvalonia 和 MaaXYZ/MaaPracticeBoilerplate 的更新版本，并参考 MaaXYZ/MaaHub 的 skill/pipeline/custom/experience 组织方式。执行升级前必须重新确认上游最新 release、模板结构和文档变化，不要依赖 AGENTS 中的历史版本号。

## 语言规则

当前项目下新增或修改的说明文档、设计文档、review 结论、任务总结，默认优先使用中文。

文件名、路径、API 名称、MaaFramework 字段名、命令、错误信息、代码标识保留原文。

当上游规范、库文档或用户明确要求英文时，可以使用英文；否则面向项目维护者的文字输出优先中文。最终回复和中间说明也优先中文，除非用户另有要求。

读取文件时默认首先使用 UTF-8编码。

## 运行真相

运行行为先看 `assets/interface.json`。它定义 `controller`、`resource`、`agent` 与 `task`，也是发布入口。

判断某个 task 实际执行入口时，先看 `task[].entry`，再沿着 pipeline 节点的 `next`、`interrupt`、`on_error` 查下游。

判断某个账号或服务器的差异行为时，先看对应 task 的 `pipeline_override`，不要只看 pipeline 默认节点。

根目录 `interface.json` 与 `assets/interface.json` 当前不一致。除非任务明确针对根目录文件，否则不要把根目录 `interface.json` 当作运行真相，也不要顺手同步、标记、迁移或删除它。

`assets/interface.json` 必须按严格 JSON 处理，不要写入注释、尾逗号或 JSONC-only 语法。

`assets/resource/pipeline/` 下的 pipeline 可能包含 `//` 注释等 JSONC-like 内容，MaaFramework 可接受。不要用严格 JSON 工具批量格式化或改写 pipeline。

## 上游对齐目标

后续重构不只是修补现有模板残留，而是逐步对齐 MaaFramework 生态当前主线。

真正升级 MaaFramework、MFAAvalonia 或对齐 MaaPracticeBoilerplate 前，必须重新确认上游最新状态，包括 stable release、artifact 命名、运行时要求、模板目录结构、CI、install/configure 脚本、README、ProjectInterface 支持能力和配置变化。

截至 2026-06-06 的上游版本观测只作为历史快照，不可作为实施时依据。需要版本号、release 日期、artifact 名称或 API 支持情况时，重新查官方仓库或文档。

参考 MaaHub 时，优先提炼 skill、pipeline、custom、experience 的组织范式和工作流。只把适合 MaaZJ 的模式引入本项目，不要机械复制社区样例，也不要把社区样例直接视为 MaaZJ 的业务实现。

MaaPracticeBoilerplate 对齐应理解为模板结构、脚本和 CI 的新做法对齐，不应覆盖 MaaZJ 已沉淀的业务资源。

## 目录地图

- `assets/interface.json`：当前运行与发布配置的最高优先级来源。
- `assets/resource/pipeline/`：业务 pipeline 节点定义，修改前阅读该目录下的 `AGENTS.md`。
- `assets/resource/image/`：TemplateMatch 等识别资源，重命名前先查引用。
- `agent/`：Python custom action/recognition 入口与注册逻辑。
- `docs/agent_context/PROJECT_UNDERSTANDING_2026-06-06.md`：广泛重构或升级前必须阅读的项目理解快照。
- `docs/agent_design/`：AGENTS 与 skill 设计方案记录。
- `deps/`、`install/`：视为 vendor/generated runtime artifacts，除非用户明确要求更新打包、运行时或发布产物。

## 常用搜索

查节点引用：

```powershell
rg -n "节点名" assets\interface.json assets\resource\pipeline
```

查图片引用：

```powershell
rg -n "图片文件名.png" assets\resource\pipeline
```

查 Python custom action/recognition 是否被业务 pipeline 使用：

```powershell
rg -n "地图定位检测|my_reco_222" assets\interface.json assets\resource\pipeline agent
```

查 task 入口和 override：

```powershell
rg -n '"entry"|"pipeline_override"|要查的节点名' assets\interface.json
```

## 安全编辑规则

保持改动范围贴合任务，不做无关重构。

删除或重命名 pipeline 节点前，必须搜索 `assets/interface.json` 与所有 `assets/resource/pipeline/` 文件中的引用。

不要移除重复账号/服务器 task override，除非已有生成器或受支持的配置机制可以替代现有 `pipeline_override` 行为。

不要随意重命名图片资源。pipeline 可能通过 `template` 文件名或逻辑节点间接引用它们。

修改 `assets/interface.json` 时，只在明确运行意图下新增、删除或重排 task；保留现有账号、服务器、override 语义。

修改 pipeline 时，谨慎处理 `next`、`interrupt`、`on_error`、`expected`、`recognition`、`action`。这些字段会直接改变执行路径或识别动作。

涉及登录、选服、账号切换、跨模块流水线的修改，应优先做小步改动，因为这些路径常被多个 task 复用。

涉及图片、OCR 文本或 ROI 的修改，应同时检查对应 pipeline 节点与图片资源，不要只改一边。

不要为了让文件符合严格 JSON 而删除 pipeline 注释；注释可能记录暂时禁用的分支或历史 debug 结论。

## 验证命令

修改资源后运行：

```powershell
python .\check_resource.py .\assets\resource\
```

执行 T1-T5 只读审计、T7 CI readonly checks 或 D/T 类任务需要统一 V0 检查时，可以运行：

```powershell
python .\check_ci_readonly.py
```

`check_ci_readonly.py` 只聚合当前只读检查入口，不替代资源变更的最低 V1 `check_resource.py`，也不证明 V2/V3/V4 真实流程。

如果只改了文档或 AGENTS 文件，可以不运行资源检查，但应确认 Markdown 文件内容可读、路径准确。

广泛重构或升级前，先阅读：

```text
docs/agent_context/PROJECT_UNDERSTANDING_2026-06-06.md
```

如果变更只涉及 AGENTS、设计文档或说明文档，不需要运行资源检查；但要确认新增规则没有和 `docs/agent_design/` 中批准的范围冲突。

如果变更影响 task 入口、pipeline 路径或图片资源，资源检查是最低验证要求；必要时还要补充手动 debug。

执行设计文档中的 R/C/T/D/N 后续任务时，按 V0-V5 分层记录验证边界：V0 静态文件检查，V1 MaaFramework resource load，V2 task entry 启动验证，V3 真实控制器流程验证，V4 日志/截图/debug 证据，V5 回归矩阵。资源变更至少需要 V1；代码重构任务完成标准应说明 V2/V3/V4 的执行结果，或写明降级原因、残余风险和补验条件。

## Python agent 当前状态

`assets/interface.json` 已配置启动 `{PROJECT_DIR}/agent/main.py`。

`agent/main.py` 启动 `AgentServer`，并通过 import 注册 custom action 与 custom recognition。当前已知注册名包括 `地图定位检测` 与 `my_reco_222`。

截至 2026-06-06，未在 pipeline 中证实这些 registered names 已接入业务流程。修改 Python agent 或判断其用途前，重新搜索 `assets/resource/pipeline/` 与 `assets/interface.json` 中对这些名称的引用。

不要把 Python agent 简化判断为“没用”。它是“已配置启动，但当前业务 pipeline 接入未证实”。

能用 pipeline 稳定表达的自动化优先使用 pipeline；只有 pipeline 难以可靠表达时，再新增或修改 Python custom action/recognition。

新增 custom action/recognition 时，必须确保 pipeline 中存在对应 registered name 的引用，并安排资源验证或手动 debug 路径。

## 重构优先级

优先保持可运行行为稳定，再降低重复与噪声。

账号/服务器 task 与 `pipeline_override` 的重复是已知重构目标，但在生成器或受支持 MFAAvalonia 配置机制落地前，应先保留现有行为。

pipeline 重构优先围绕可验证的小模块进行，例如单个日常 flow、单个活动 flow、单个商城或公会路径。

未进入明确的 v4 后续落地任务前，不要创建 generator、引用审计脚本或 skill initial layout。

涉及 MaaFramework、MFAAvalonia、MaaPracticeBoilerplate、MaaHub 参考、CI release、`deps/` 或 `install/` 的升级任务，应尽量与 pipeline 业务重构分开，减少比较噪声。

## 后续重构任务闭环

后续 MaaFramework 适配重构、测试体系建设和文档反馈任务，优先按 `docs/agent_design/refactor_design_maafw_test_automation_2026-06-07.md` 中的任务矩阵、单任务 Runbook 和 D4/D5/N1 判定表拆分执行。

该设计文档用于指导任务拆分、产物格式、验证分层和反馈闭环；它不改变 MaaZJ 的运行真相，也不能覆盖 `assets/interface.json`、pipeline 或资源文件的实际行为。

每个 R/C/T/D/N 后续任务在进入 review、test 或 final 前，应检查是否需要回写设计文档、是否有稳定规则需要同步 `AGENTS.md` 或项目专属 skill、是否发现需要单独分流的新需求。

发现设计文档字段、边界、Runbook 或提示词不准确时，使用 D4-design-feedback-sync 回写或建议回写设计文档。发现仓库级安全边界、canonical source、验证最低要求、目录索引、可复用流程或 MaaZJ 专属检查顺序变化时，使用 D5-agents-skill-sync 检查并同步 `AGENTS.md` 与项目专属 skill。发现新的业务或工程需求超出当前任务边界时，使用 N1-new-requirement-triage 先分流，不要混入当前重构任务直接实现。

不要把单次任务日志、尚未验证的探索结论或临时猜测写入 `AGENTS.md` 或项目专属 skill；这类内容应留在 `.agent/tasks/<task-id>/` 或对应的设计反馈记录中。

## 升级注意事项

依赖或运行时升级前，先冻结当前资源验证结果，避免无法判断升级造成的行为差异。

修改 workflow 上游引用前，确认目标 MFAAvalonia upstream 与 artifact 命名。优先使用 `MaaXYZ/MFAAvalonia`，不要继续沿用旧的非目标上游，除非用户明确要求。

对齐新版 MaaFramework 前，重新确认资源加载、pipeline 协议、recognition/action 字段、agent/custom API 和运行时 artifact 要求。

对齐新版 MFAAvalonia 前，重新确认 ProjectInterface 字段、任务展示能力、controller/resource/agent 配置和 artifact 命名。

对齐 MaaPracticeBoilerplate 前，先区分模板结构与 MaaZJ 业务资源；只吸收适合当前项目的目录、脚本、CI 和 README 做法。

升级后至少比较资源加载、task 展示、task 启动行为。若任务涉及发布产物，再检查 `install.py` 对 `assets/interface.json` 的复制与版本写入流程。

不要默认编辑 `deps/` 或 `install/`。只有当任务明确涉及打包、运行时、发布产物或依赖落地时，才进入这些目录。
