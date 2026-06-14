# R9 Test Script Design

## 任务定位

本设计用于后续 T1-T7 测试工具与验证方案任务。它只定义只读脚本边界、verification matrix、报告格式和后续任务提示词，不实现脚本、不接入 CI、不修改业务资源。

运行与发布配置仍以 `assets/interface.json` 为准；根目录 `interface.json` 不作为 canonical 配置。`assets/interface.json` 必须按严格 JSON 处理，`assets/resource/pipeline/` 允许 MaaFramework-compatible JSONC-like 内容，后续脚本不得 strict-format pipeline。

## 输入产物

| 输入 | 当前可消费结论 | R9 使用方式 |
| --- | --- | --- |
| R0 baseline | `python .\check_resource.py .\assets\resource\` exit code `0`，V1 resource load 通过；不证明 task entry 启动或真实流程可达 | 把 V1 resource load 作为 T7 或资源变更后的最低验证参考，不用 V0 脚本替代 |
| R1 interface inventory | `assets/interface.json` 严格 JSON 解析通过；35 个 task；64 项 `pipeline_override`；entry missing 数为 0；root `interface.json` 未作为运行真相 | 作为 T1/T2 输入，保留 override 语义，不折叠、不重排、不同步 root config |
| R2 flow map | 35 个 task 分为 6 组 unique entry；账号/服务器任务必须叠加 `pipeline_override` 理解；S1-S7 均未证明 V2/V3/V4 | 作为 T3/T6 输入，脚本报告需区分静态路径与真实可达 |
| R3 graph audit | 47 个 pipeline JSON 文件、389 个节点、1073 条引用边；未发现悬空引用；139 个静态不可达候选不能作为删除依据 | 作为 T3 引用完整性和 recovery 分类字段来源 |
| R4 image audit | 121 个图片文件；116 条 template 引用；74 个 unique template 图片全部存在；47 个疑似未引用图片只作为 review 候选；OCR/ROI 风险是静态候选 | 作为 T4 图片/OCR/ROI 风险字段来源，不支持自动删除或重命名图片 |
| R5 custom audit | `assets/interface.json` 配置 Python agent 启动；注册 `地图定位检测`、`my_reco_222`；未发现 pipeline 静态业务引用；不推断 agent 无用 | 作为 T5 registered name 状态枚举来源 |

## Verification Matrix

| 验证对象 | 层级 | 主要输入 | 检查方法 | 产出 | hard fail | warning / review 候选 | 后续任务 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `assets/interface.json` strict JSON | V0 | `assets/interface.json`、`install.py` | 使用严格 JSON parser 只读解析；确认 `install.py` 依赖 strict JSON | strict JSON check report | JSON 解析失败；文件不存在 | schema 外字段仅记录，不自动改写 | T1 |
| ProjectInterface task/entry/override | V0 | R1、`assets/interface.json`、pipeline 节点索引 | 枚举 task、entry、`pipeline_override`、agent/controller/resource 字段，检查目标节点存在 | interface audit report | task entry 或 override 目标缺失 | 空 override、重复账号/服务器 override、特殊 `next` 覆盖 | T2、C8 |
| Pipeline reference graph | V0 | R2/R3、pipeline JSON/JSONC-like 文件 | JSONC-aware 解析；抽取 `next`、`interrupt`、`on_error`、`pipeline_override.next` | pipeline ref report | 引用目标缺失；解析失败且无法定位文件 | 静态不可达、自循环、共享 recovery、高风险跨模块边 | T3、C1-C5 |
| Image/template usage | V0 | R4、pipeline、`assets/resource/image/` | 抽取 TemplateMatch/OCR/ROI 字段，检查 template 文件存在和复用情况 | image usage report | 已引用 template 文件缺失 | 疑似未引用图片、多模块共享图片、OCR no/large/edge/small ROI | T4、C1-C5 |
| Agent custom registered name | V0 | R5、`agent/`、`assets/interface.json`、pipeline | 搜索 registered name、custom action/recognition 字段和 import 链路 | custom report | interface 配置 agent 入口缺失但任务要求 agent；pipeline 引用未注册 name | registered 但 pipeline 未引用；runtime call 未验证 | T5、D2、C6/C7 |
| MaaFramework resource load | V1 | `assets/resource/`、`check_resource.py` | 运行 `python .\check_resource.py .\assets\resource\` | resource load report | resource load 失败 | loader 跳过非 pipeline 文件等非阻断 warning | R0、T7、资源变更任务 |
| Task entry startup | V2 | R1/R2/R9、具体 task | 通过 Tasker 或 MFAAvalonia 启动单个 task entry，记录是否进入预期关键节点 | startup evidence | entry 启动失败或立即异常退出 | 启动成功但路径未到目标观察点 | T6、C 类任务 |
| Real controller flow | V3 | T6 case matrix、控制器环境、账号状态 | 在真实控制器执行限定 flow，观察到达关键节点或终止状态 | manual/debug evidence | 关键 flow 无法到达且无降级说明 | 环境、账号、活动状态导致无法完整覆盖 | T6、C 类任务 |
| Evidence package | V4 | 日志、截图、录屏、debug 输出 | 将证据绑定到 case id、task、entry、账号/服务器、时间和结论 | evidence index | 证据缺失导致无法复现判断 | 证据不完整但足以支持降级结论 | T6、C 类任务 |
| Regression matrix | V5 | 多 flow、多账号/服务器、T1-T7 报告 | 对关键路径做矩阵化回归 | regression report | 回归阻断且影响发布/重构继续 | 覆盖不足、环境不可用、需补测 | T7、重大重构后 |

## 统一报告约定

后续只读脚本建议同时支持人类可读 Markdown 与机器可读 JSON。R9 不要求一次性实现两种格式，但字段应提前保持稳定。

通用字段：

- `check_id`：例如 `T1-strict-json`、`T3-pipeline-ref`。
- `version`：脚本或报告格式版本。
- `generated_at`：ISO 时间。
- `source_files`：实际读取的文件或目录。
- `input_reports`：消费的 R0-R9 文档。
- `scope`：只读范围与禁止写入范围。
- `summary`：总数、失败数、warning 数、review 候选数。
- `findings`：结构化问题列表。
- `limitations`：验证边界，不得把 V0 写成 V2/V3。
- `d4_d5_n1`：是否建议触发 D4/D5/N1。

Finding 字段：

- `severity`：`error`、`warning`、`info`。
- `category`：例如 `missing_entry`、`dangling_reference`、`suspected_unused_image`。
- `file`：相对仓库路径。
- `node`：pipeline 节点名，可为空。
- `task`：ProjectInterface task 名，可为空。
- `message`：面向维护者的中文说明。
- `evidence`：命中的字段、引用边、搜索命令或报告来源。
- `recommendation`：后续动作，只能建议，不自动修改资源。

退出码建议：

| 退出码 | 含义 | 适用 |
| ---: | --- | --- |
| 0 | 检查完成且无 hard fail | warning/review 候选允许存在 |
| 1 | 存在 hard fail | strict JSON 失败、缺失 entry、缺失 template、悬空引用 |
| 2 | 检查无法完成 | 读取失败、解析器不可用、必要输入缺失 |

warning 不应让脚本失败，除非 T7 或后续任务明确把某类 warning 升级为 gate。

## 只读脚本设计

### T1-json-strict-check

目标：确认 `assets/interface.json` 能被严格 JSON parser 读取，并记录 `install.py` 对 strict JSON 的依赖。

输入：

- `assets/interface.json`
- `install.py`
- R1 interface inventory

检查项：

- `assets/interface.json` 文件存在且严格 JSON 解析通过。
- 不接受注释、尾逗号或 JSONC-only 语法。
- 只读确认 `install.py` 复制 `assets/interface.json` 到 `install/interface.json` 并用 `json.load` 读取。

hard fail：

- `assets/interface.json` 不存在。
- strict JSON parse 失败。

warning：

- root `interface.json` 与 canonical 文件不一致时只记录提醒，不同步、不删除、不迁移。

禁止事项：

- 不格式化、不重排、不写回 `assets/interface.json`。
- 不读取 root `interface.json` 作为运行真相。

### T2-interface-audit-script

目标：审计 ProjectInterface task、entry、`pipeline_override`、controller/resource/agent 配置，产出只读 audit report。

输入：

- R1 interface inventory
- `assets/interface.json`
- pipeline 节点索引，可由 T3 共享或本脚本只读构建

检查项：

- task 数、task name、entry、entry 静态位置。
- `pipeline_override` 总数、空 override、账号/服务器 override、特殊 `next`/`action` 覆盖。
- `agent.child_exec` 与 `agent.child_args` 是否存在。
- controller/resource 字段是否存在。

hard fail：

- task entry 指向不存在节点。
- override 目标节点不存在。
- canonical interface 无法读取。

warning：

- 空 override 对象。
- 多账号/服务器重复 override。
- 特殊账号 `next` 覆盖，如 `暖阳 18918203738` 的 FARM 路径。

禁止事项：

- 不折叠账号/服务器 override。
- 不生成替换 `assets/interface.json` 的配置。
- 不把 root `interface.json` 当作 canonical。

### T3-pipeline-ref-check-script

目标：JSONC-aware 审计 pipeline 节点引用，输出 graph/reference report。

输入：

- R2 flow map
- R3 graph audit
- `assets/resource/pipeline/`
- `assets/interface.json` 中 task entry 与 override 节点名

解析策略：

- 必须使用 JSONC-aware 策略或 MaaFramework-compatible 解析方式。
- 不 strict-format pipeline，不删除注释。
- 解析失败时报告文件路径和上下文，不自动修复。

检查项：

- 节点集合、文件位置、重复节点名候选。
- `next`、`interrupt`、`on_error`、`pipeline_override.next` 指向存在性。
- 自循环、静态不可达候选、共享 recovery 分类。
- `on_error` 与 `interrupt` 分开输出。

hard fail：

- entry 或 override 引用的节点不存在。
- `next`、`interrupt`、`on_error` 指向不存在节点。

warning：

- 静态不可达候选。
- 自循环节点。
- 共享 recovery 与跨模块边。

禁止事项：

- 不删除不可达候选。
- 不重命名节点。
- 不把 recovery 合并建议直接写成实现要求。

### T4-image-usage-check-script

目标：审计图片引用、TemplateMatch/OCR/ROI 风险，输出 image usage report。

输入：

- R4 image usage report
- `assets/resource/pipeline/`
- `assets/resource/image/`

检查项：

- image 文件总数、template 引用记录、unique template 图片。
- 已引用 template 是否存在。
- 疑似未引用图片候选。
- 多处复用图片，如 `红点.png`、`家园图标.png`、`auto_add.png`、`笔记.png`。
- OCR/ROI 风险：`no_roi`、`large_roi`、`edge_roi`、`small_roi`、`regex_expected`、`multi_expected`。

hard fail：

- pipeline 引用的 template 图片不存在。

warning：

- 疑似未引用图片。
- 多模块共享图片。
- OCR/ROI 静态风险。

禁止事项：

- 不删除、不移动、不重命名图片。
- 不把未引用候选写成无用资源。
- 不修改 OCR 文本或 ROI。

### T5-agent-custom-check-script

目标：审计 Python agent 启动配置、custom action/recognition registered names 与 pipeline 静态引用状态。

输入：

- R5 registered name report
- `assets/interface.json`
- `assets/resource/pipeline/`
- `agent/`

检查项：

- `assets/interface.json` 是否配置 Python agent 启动。
- `agent/main.py` import 链路。
- `@AgentServer.custom_action(...)` 与 `@AgentServer.custom_recognition(...)` 注册名。
- registered name 在 canonical interface 与 pipeline 中的静态引用。
- 自定义逻辑是否包含会改变点击、识别或 next 的调用，仅作为风险提示。

hard fail：

- pipeline 引用 custom registered name，但 `agent/` 未注册。
- 任务要求 agent 检查而 canonical agent 配置缺失。

warning：

- registered name 已注册但 pipeline 静态引用未发现。
- runtime call 未验证。

禁止事项：

- 不删除 agent 注册项。
- 不把 agent 简化判断为“没用”。
- 不新增 custom action/recognition。

### T6-real-flow-smoke-plan

目标：建立真实流程 smoke case matrix 与证据模板。T6 是文档/验证模板任务，执行真实流程需明确用户授权和环境条件。

输入：

- R1 task inventory
- R2 flow map
- R7 module boundary
- R8 pilot selection
- R9 verification matrix

建议 case 字段：

- `case_id`
- `task_name`
- `entry`
- `account_or_server`
- `pipeline_override_summary`
- `start_condition`
- `expected_key_nodes`
- `stop_condition`
- `required_evidence`
- `validation_layer`
- `degrade_reason`
- `residual_risk`

优先 smoke 候选：

- 首个 C 类试点 flow。
- 启动/选服、账号切换只在单独 C6/C7 或授权 smoke 中验证。
- 地图/野猪、活动自循环、特殊账号 FARM override 需要更高证据要求。

禁止事项：

- 不执行未授权真实流程。
- 不修改资源。
- 不把 V2/V3/V4 缺失写成通过。

### T7-ci-readonly-checks

目标：设计或接入只读 CI 检查。R9 只定义边界，不修改 `.github/workflows/`。

输入：

- T1-T5 输出报告
- R9 verification matrix
- R0 V1 resource load 经验

可作为 CI gate 的候选：

- T1 strict JSON hard fail。
- T2 entry/override missing hard fail。
- T3 dangling reference hard fail。
- T4 missing template hard fail。
- T5 pipeline 引用未注册 custom name hard fail。

不宜默认作为 CI gate：

- 疑似未引用图片。
- 静态不可达候选。
- OCR/ROI 风险。
- registered name 已注册但未被 pipeline 引用。
- V2/V3/V4 真实流程缺失。

禁止事项：

- 不接入会写资源的检查。
- 不修改 release workflow、`deps/`、`install/` 或 runtime artifact。
- 不把 warning 类问题升级为阻断，除非已有 D4/D5 或任务批准。

## 降级记录模板

当后续任务无法执行更高验证层级时，使用以下字段记录：

```text
目标层级：V2/V3/V4/V5
实际层级：V0/V1/...
降级原因：
已完成证据：
未覆盖风险：
补验条件：
建议后续任务：
```

降级记录不能把未执行的验证写成通过，只能说明当前结论的边界。

## 后续任务提示词

### T1

```text
继续 multi-agent-refactor 工作流，创建并执行 T1-json-strict-check。

目标：根据 R1 与 R9 设计，实现或记录 `assets/interface.json` 严格 JSON 只读检查命令/脚本。
边界：只读 `assets/interface.json` 与 `install.py`；不格式化、不重排、不写回 JSON；不处理 root `interface.json`。
产出：strict JSON check 命令或脚本、报告、V0 验证记录、D4/D5/N1 判断。
```

### T2

```text
继续 multi-agent-refactor 工作流，创建并执行 T2-interface-audit-script。

目标：根据 R1 与 R9 设计，实现 ProjectInterface task/entry/override 只读审计。
边界：只读 `assets/interface.json` 与 pipeline 节点索引；不写回 interface；不折叠账号/服务器 override。
产出：audit report、hard fail/warning 分类、V0 验证记录、D4/D5/N1 判断。
```

### T3

```text
继续 multi-agent-refactor 工作流，创建并执行 T3-pipeline-ref-check-script。

目标：根据 R2/R3/R9 设计，实现 JSONC-aware pipeline 引用检查。
边界：只读 `assets/resource/pipeline/`；不 strict-format pipeline；不删除不可达候选或 recovery 节点。
产出：ref report、dangling reference 检查、recovery 分类、V0 验证记录、D4/D5/N1 判断。
```

### T4

```text
继续 multi-agent-refactor 工作流，创建并执行 T4-image-usage-check-script。

目标：根据 R4/R9 设计，实现图片引用、TemplateMatch/OCR/ROI 只读检查。
边界：只读 pipeline 与 `assets/resource/image/`；不删除、不移动、不重命名图片；不改 OCR/ROI。
产出：image report、missing template hard fail、疑似未引用/共享图片 warning、V0 验证记录、D4/D5/N1 判断。
```

### T5

```text
继续 multi-agent-refactor 工作流，创建并执行 T5-agent-custom-check-script。

目标：根据 R5/R9 设计，实现 Python custom registered name 只读检查。
边界：只读 `assets/interface.json`、pipeline 与 `agent/`；不删除 agent 注册；不声称 agent 无用。
产出：custom report、registered name 与 pipeline 引用状态、V0 验证记录、D4/D5/N1 判断。
```

### T6

```text
继续 multi-agent-refactor 工作流，创建并执行 T6-real-flow-smoke-plan。

目标：根据 R1/R2/R7-R9 建立真实流程 smoke case matrix、证据模板和降级记录格式。
边界：文档/模板为主；不执行未授权真实流程；不修改资源。
产出：smoke plan、case matrix、证据模板、V2/V3/V4 执行或降级边界、D4/D5/N1 判断。
```

### T7

```text
继续 multi-agent-refactor 工作流，创建并执行 T7-ci-readonly-checks。

目标：根据 T1-T5 与 R9 设计 CI readonly check 方案或只读 workflow。
边界：不得接入会写资源的检查；不修改 release 产物、`deps/`、`install/`；是否修改 `.github/workflows/` 需单独确认。
产出：CI readonly check 方案、hard fail/warning gate 策略、V0/V1 验证记录、D4/D5/N1 判断。
```

## D4/D5/N1 判断

- D4：暂不需要。R9 任务矩阵和 Runbook 足以承载 verification matrix、脚本边界、报告格式和后续提示词。
- D5：建议后续 T3/T4/T7 执行后再检查。R9 复用了现有稳定规则：strict JSON、pipeline JSONC-aware、只读脚本、疑似未引用不删除、agent 不简化为无用；当前没有新增必须同步到 `AGENTS.md` 或 skill 的稳定规则。
- N1：暂不需要。本任务没有实现脚本、接入 CI、修改资源或提出新的真实流程执行需求。

## R9 验证记录

- V0 文档交叉检查：本设计已对照 R0-R5 报告、R9 矩阵、T1-T7 矩阵与 Runbook。
- 路径检查：引用的 R0-R5 报告均位于 `docs/agent_context/`。
- 边界检查：本设计不修改 `assets/interface.json`、root `interface.json`、pipeline、图片、agent、`deps/`、`install/` 或 `.github/workflows/`。
- 资源检查：未运行 `python .\check_resource.py .\assets\resource\`，因为本任务只新增设计文档和 `.agent/` 任务记录，不修改运行资源。
