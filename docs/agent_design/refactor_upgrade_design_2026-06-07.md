# MaaZJ 后续重构升级设计文档

版本：2026-06-07

状态：设计草案

范围：面向后续 MaaZJ 资源重构、ProjectInterface 治理、模板残留清理与 MaaFramework 生态上游对齐。

## 目标

本文档把当前项目理解转化为后续可执行的重构升级设计。它不替代 `docs/agent_context/PROJECT_UNDERSTANDING_2026-06-06.md`，而是在该快照基础上回答三个问题：

1. 后续重构升级应先保护哪些运行事实。
2. 哪些问题应分阶段处理，避免一次性改动造成比较噪声。
3. 每个阶段完成后应如何验证，才能确认 MaaZJ 仍可运行。

本设计不执行实际升级，不修改 `assets/interface.json`、pipeline、图片资源、Python agent、`deps/`、`install/` 或 CI。

## 当前项目定位

MaaZJ 是 MaaFramework 资源项目，不是传统应用代码库。运行链路应理解为：

```text
MFAAvalonia -> ProjectInterface -> resource bundle -> MaaFramework pipeline -> optional Python agent
```

当前业务行为主要由以下位置决定：

- `assets/interface.json`：运行与发布配置的 canonical source，定义 `controller`、`resource`、`agent` 与 `task`。
- `assets/resource/pipeline/`：MaaFramework pipeline 节点和任务流。
- `assets/resource/image/`：TemplateMatch 等识别资源。
- `assets/resource/model/ocr/`：OCR 模型文件。
- `agent/`：Python custom action/custom recognition 入口，目前已配置启动，但业务接入未证实。

根目录 `interface.json` 与 `assets/interface.json` 不一致。除非任务明确要求处理根目录文件，否则后续重构升级都应以 `assets/interface.json` 为准。

## 与项目理解快照的关系

`docs/agent_context/PROJECT_UNDERSTANDING_2026-06-06.md` 是项目理解快照，记录了当时观察到的任务数量、pipeline 结构、Python agent 状态、本地依赖状态和上游版本观测。

本文档不重复快照的所有事实，而是抽取其中对后续实施最重要的设计约束：

- `assets/interface.json` 是运行真相。
- `install.py` 从 `assets/interface.json` 生成发布用 `install/interface.json`。
- pipeline 可能包含 MaaFramework-compatible JSONC-like 内容，不应使用严格 JSON 工具批量改写。
- 账号/服务器 task 依赖大量 `pipeline_override`，在替代机制落地前不能直接折叠。
- Python agent 已配置启动，但当前 registered names 的业务 pipeline 引用未证实。
- `deps/` 与 `install/` 视为 vendor/generated runtime artifacts，除非任务明确涉及运行时或发布产物。
- 2026-06-06 的上游版本观测只作为历史快照，实施升级前必须重新确认。

## 设计原则

1. 先保可运行，再降重复。

   重构目标不能优先于资源可加载、任务可展示、任务可启动。每次跨模块改动前后都应保留可比较的验证结果。

2. `assets/interface.json` 优先。

   ProjectInterface、发布入口和 task override 以 `assets/interface.json` 为准。根目录 `interface.json` 的处理应作为单独决策，不顺手同步、迁移或删除。

3. 小模块优先。

   pipeline 重构优先选择单个日常 flow、单个活动 flow、单个商城或公会路径。登录、选服、账号切换、跨模块流水线属于高风险路径，应小步推进。

4. 保留 override 语义。

   账号/服务器 task 重复是明确重构目标，但在 generator 或受支持 MFAAvalonia 配置机制落地前，应保留现有 `pipeline_override` 行为。

5. 上游对齐不等于覆盖模板。

   MaaPracticeBoilerplate 只作为模板结构、脚本、CI 和 README 做法参考；MaaHub 只作为 skill、pipeline、custom、experience 组织方式参考。不能机械复制上游模板或社区样例覆盖 MaaZJ 业务资源。

6. 工具化晚于人工验证。

   task generator、pipeline 引用审计、图片使用检查等工具应在至少完成一次人工重构并明确规则后再创建。

## 主要风险

### ProjectInterface 重复与误编辑

根目录 `interface.json` 与 `assets/interface.json` 不一致，后续维护者可能误编辑根目录文件。应先在文档和 AGENTS 规则中强化 canonical source，再单独决定根目录文件的处置方式。

可选处置方向：

- 保留但标注 stale 或非 canonical。
- 同步为生成产物。
- 迁移或删除。

上述动作都可能影响维护习惯，应另开任务评估。

### 账号/服务器 task 膨胀

当前多组账号/服务器组合依赖手写 task 和 `pipeline_override`。直接删除重复项会改变运行入口和账号选择行为。

设计方向：

- 先抽取现有 task、entry、override 的结构表。
- 再评估目标 MFAAvalonia 是否支持更合适的 task 配置能力。
- 最后决定使用生成器、配置机制或保留手写方式。

### JSON 与 JSONC 边界

`assets/interface.json` 必须是严格 JSON，因为 `install.py` 使用 `json.load` 读取。pipeline 可包含 MaaFramework-compatible JSONC-like 注释，不应被严格 JSON 工具批量格式化。

后续脚本如需解析 pipeline，应使用 JSONC-capable parser 或 MaaFramework 自身资源检查结果作为依据。

### Python agent 接入未证实

`assets/interface.json` 已配置 `{PROJECT_DIR}/agent/main.py`，当前已知 registered names 包括 `地图定位检测` 与 `my_reco_222`。截至 2026-06-06，未在 pipeline 中证实业务引用。

后续方向：

- 不把 Python agent 简化判断为“没用”。
- 新增或修改 custom action/recognition 前，先确认 pipeline 是否有对应 registered name 引用。
- 能用 pipeline 稳定表达的自动化优先使用 pipeline。

### 本地运行时与 CI 差异

`deps/`、`install/` 是 vendor/generated runtime artifacts。CI 可能下载上游 latest artifacts，本地依赖可能固定在较旧状态。升级前应冻结当前资源验证结果，避免无法判断行为差异来自业务变更还是运行时变更。

## 分阶段路线图

### 阶段 0：冻结基线

目标：

- 明确当前资源加载是否通过。
- 记录当前 task 展示、关键入口和已知高风险路径。
- 确认后续改动比较基准。

建议动作：

- 运行 `python .\check_resource.py .\assets\resource\`。
- 记录 `assets/interface.json` task 数量、主要 entry、账号/服务器 override 结构。
- 记录 Python agent registered names 与 pipeline 引用搜索结果。

验收：

- 资源检查通过或明确记录失败原因。
- 后续重构任务能引用一份明确 baseline。

### 阶段 1：ProjectInterface source-of-truth 治理

目标：

- 降低误编辑根目录 `interface.json` 的风险。
- 保留 `assets/interface.json` 的现有 task、entry 和 override 语义。

建议动作：

- 单独评估根目录 `interface.json` 的用途。
- 决定标注、同步、生成或迁移策略。
- 不在本阶段改动业务 pipeline。

验收：

- 维护者能清楚知道运行与发布配置来源。
- `install.py` 仍从 `assets/interface.json` 生成发布配置。

### 阶段 2：账号/服务器 task 重复治理

目标：

- 降低 `assets/interface.json` 中手写重复。
- 不改变账号选择和服务器选择行为。

建议动作：

- 先生成只读结构表，列出 task name、entry、server expected、account expected。
- 重新确认目标 MFAAvalonia 是否支持更合适的 task 参数化或配置展示能力。
- 若无受支持机制，再评估 generator。

验收：

- 重复 task 的行为对照表完整。
- 任意替代方案都能还原现有 `pipeline_override` 语义。

### 阶段 3：pipeline 模块化重构

目标：

- 让启动、账号切换、日常 farm、活动、商城、公会、笔记、探索、起号等边界更清晰。
- 降低跨模块 `next` 链接的维护成本。

建议动作：

- 每次只处理一个 flow。
- 删除或重命名节点前搜索 `assets/interface.json` 与所有 pipeline 引用。
- 保留 MaaFramework-compatible JSONC-like 注释。

验收：

- `python .\check_resource.py .\assets\resource\` 通过。
- 被改 flow 的入口、下游 `next`、`interrupt`、`on_error` 路径被人工检查。

### 阶段 4：Python agent 归位

目标：

- 判断现有 Python agent 是继续保留为可用 custom 扩展，还是清理模板残留。
- 如果新增 custom 逻辑，确保 pipeline 有真实引用和验证路径。

建议动作：

- 重新搜索 `地图定位检测|my_reco_222|custom_action|custom_recognition`。
- 对齐新版 MaaFramework 前，重新确认 Python agent API 和 runtime requirements。
- 若业务确需 custom 逻辑，先设计 registered name、pipeline 调用点和回退行为。

验收：

- agent 状态不再停留在“看起来存在但用途不明”。
- 新增 custom 逻辑必须有 pipeline 引用和验证记录。

### 阶段 5：模板残留清理

目标：

- 让 README、脚本和文档更像 MaaZJ，而不是 MaaPracticeBoilerplate 残留。

建议动作：

- 对齐 MaaPracticeBoilerplate 当前模板结构前，重新确认上游最新目录、CI、install/configure 脚本和 README。
- 只吸收适合 MaaZJ 的结构和写法，不覆盖业务资源。

验收：

- README 能解释 MaaZJ 的真实运行入口和验证方式。
- 模板示例代码如果保留，应明确用途；如果删除，应确认无业务引用。

### 阶段 6：上游升级与 release 对齐

目标：

- 分阶段对齐 MaaFramework、MFAAvalonia 与 MaaPracticeBoilerplate 当前主线。
- 明确 release workflow 的目标上游和 artifact 命名。

实施前必须重新确认：

- `MaaXYZ/MaaFramework` latest stable release、artifact 命名、资源加载、pipeline 协议、custom API、运行时要求。
- `MaaXYZ/MFAAvalonia` latest stable release、artifact 命名、ProjectInterface 字段、task 展示能力、controller/resource/agent 配置行为。
- `MaaXYZ/MaaPracticeBoilerplate` 目录结构、CI、install/configure 脚本、README 和资源组织方式。
- `MaaXYZ/MaaHub` 中可参考的 skill、pipeline、custom、experience 组织范式。

验收：

- 升级前后资源加载结果可比较。
- task 展示和 task 启动行为被检查。
- 若涉及发布产物，检查 `install.py` 对 `assets/interface.json` 的复制和版本写入流程。

### 阶段 7：工具化

目标：

- 在规则稳定后，用轻量工具降低重复劳动。

候选工具：

- `generate-interface-tasks.py`：生成账号/服务器 task。
- `check-pipeline-refs.py`：检查 task entry 与 pipeline 节点引用。
- `check-image-usage.py`：检查图片资源引用。
- `check-upstream-releases.py`：只读查询上游 release 和 artifact 命名，生成升级前检查报告。

验收：

- 工具不改变资源，或只在明确输入和 review 后生成变更。
- 工具输出能被人工审查。

## 上游对齐检查规则

任何依赖版本号、release 日期、artifact 名称、API 支持或模板结构的任务，都必须在实施当天重新查官方来源或官方文档，并在任务文档中记录检查日期。

历史事实的写法应类似：

```text
截至 2026-06-06 的历史观察是 ...；实施前必须重新确认。
```

不要写成：

```text
当前最新版是 ...
```

除非该信息刚刚被重新确认。

## 验证矩阵

| 变更类型 | 最低验证 | 额外检查 |
| --- | --- | --- |
| 只改文档、AGENTS、skill、`.agent/` | 人工检查 Markdown/JSON 可读性 | 说明不运行资源检查的原因 |
| 改 `assets/interface.json` | JSON 严格解析、资源检查 | task entry、`pipeline_override` 语义检查 |
| 改 pipeline | `python .\check_resource.py .\assets\resource\` | `next`、`interrupt`、`on_error`、`expected` 路径检查 |
| 改图片/OCR/ROI | 资源检查 | 搜索图片引用和对应 pipeline 节点 |
| 改 Python agent | 资源检查或手动 debug 路径 | 搜索 registered name 的 pipeline 引用 |
| 改 CI/release/`deps`/`install` | 资源检查、打包检查 | 上游 release、artifact 命名和运行时要求确认 |

## 暂不做事项

- 不直接升级 MaaFramework 或 MFAAvalonia。
- 不编辑 `deps/` 或 `install/`。
- 不删除、同步或迁移根目录 `interface.json`。
- 不折叠账号/服务器 task override。
- 不创建 generator 或引用审计脚本。
- 不批量格式化 pipeline。
- 不把 MaaHub 样例直接当作 MaaZJ 业务实现。

## 推荐的下一批任务

1. 冻结当前资源 baseline，并记录 `check_resource.py` 输出。
2. 生成 `assets/interface.json` task/override 只读结构表。
3. 单独决策根目录 `interface.json` 的处置方式。
4. 选择一个低风险单模块 pipeline flow 做人工重构试点。
5. 重新确认上游当前状态后，再设计 MaaFramework/MFAAvalonia 升级任务。
