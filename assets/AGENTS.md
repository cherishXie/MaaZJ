# Assets Agent 指南

## 最高优先级

`assets/interface.json` 是当前运行与发布配置的 canonical / release-facing 来源。除非任务明确针对根目录 `interface.json`，否则不要把根目录 `interface.json` 当作运行真相。

`assets/interface.json` 必须保持严格 JSON。不要写入注释、尾逗号或 JSONC-only 语法。

修改 `assets/` 内资源时，优先保护从 `assets/interface.json` 到 resource bundle、pipeline、image、agent 启动入口的行为链。

## ProjectInterface 边界

`controller` 定义控制器配置，`resource` 定义资源包路径，`agent` 定义 Python agent 启动入口，`task` 定义 MFAAvalonia 展示与启动的任务。

新增、删除、重排 task 必须有明确运行意图。不要为了整理文件而改变 task 展示、启动入口或账号/服务器差异行为。

`task.entry` 必须指向 `assets/resource/pipeline/` 中的 pipeline 节点。修改 entry 前，先搜索目标节点是否存在，并确认下游 `next`、`interrupt`、`on_error` 路径。

`pipeline_override` 是当前账号、服务器或任务入口差异行为的重要配置。生成器或新版 MFAAvalonia 支持机制落地前，不要删除、折叠或批量改写这些 override。

## Resource Bundle 规则

`resource` 路径保持与 `{PROJECT_DIR}/resource` 兼容。`install.py` 会把 `assets/resource` 复制到 `install/resource`，所以 `assets/interface.json` 里的 `{PROJECT_DIR}/resource` 不要随意改。

`assets/resource/pipeline/` 存放 pipeline 节点定义；修改前阅读 `assets/resource/pipeline/AGENTS.md`。

`assets/resource/image/` 存放 TemplateMatch 等识别资源。不随意移动或重命名图片资源，因为 pipeline 可能通过 `template` 文件名或逻辑节点间接引用它们。

## Pipeline / Image / OCR 关系

修改 pipeline 节点、图片、OCR 文本、ROI、`template` 时，都要回查相关 pipeline 节点，确认识别方式、资源文件和执行路径仍然匹配。

改图片文件名前，搜索 pipeline 中的 `template` 引用；改 OCR 文本或 ROI 前，确认对应 `recognition`、`expected`、`roi` 和 `target` 是否仍适配当前界面。

删除或重命名 pipeline 节点前，搜索 `assets/interface.json` 与所有 `assets/resource/pipeline/` 文件中的引用。

## Python Agent 配置关系

`assets/interface.json` 只配置 Python agent 启动入口：`{PROJECT_DIR}/agent/main.py`。

业务是否使用 custom action/custom recognition，仍以 pipeline 中是否引用 registered name 为准。不要只因为 agent 已配置启动，就判断 custom 逻辑已经接入业务流程。

修改 Python agent 相关配置前，先搜索 `assets/interface.json`、`assets/resource/pipeline/` 与 `agent/` 中的 registered name 引用。

## JSON 与 JSONC 边界

`assets/interface.json` 是严格 JSON，因为 `install.py` 会复制它到 `install/interface.json`，随后用 `json.load` 读取并写入版本号。

`assets/resource/pipeline/` 下的 pipeline 可保留 MaaFramework 兼容的 JSONC-like 写法，例如 `//` 注释。不要用严格 JSON 工具批量格式化 pipeline，也不要剥离注释。

不要把 pipeline 的 JSONC 习惯带到 `assets/interface.json`，也不要把 `assets/interface.json` 的严格 JSON 要求套到所有 pipeline 文件上。

## MFAAvalonia 对齐提醒

对齐新版 MFAAvalonia 前，重新确认 ProjectInterface 字段、task 展示能力、controller/resource/agent 配置、artifact 命名和兼容性变化。

如果新版 MFAAvalonia 提供更合适的账号、服务器或 task 配置机制，应先做小范围验证，再替代现有 `pipeline_override` 行为。

对齐 MaaPracticeBoilerplate 时，只吸收适合 MaaZJ 的资源组织、脚本和 CI 做法，不要用模板覆盖 MaaZJ 已沉淀的业务资源。

## 打包与发布边界

`install.py` 会复制 `assets/resource` 到 `install/resource`，并复制 `assets/interface.json` 到 `install/interface.json` 后写入版本号。

不要直接修改 `install/interface.json` 作为源配置。源配置始终回到 `assets/interface.json`。

`install/` 是生成或发布产物目录，除非任务明确涉及打包、运行时或发布产物，不要把它当作源目录编辑。

## 验证清单

以下命令默认在仓库根目录执行：

```powershell
python .\check_resource.py .\assets\resource\
```

只修改文档或 AGENTS 文件时，可以不运行资源检查。

修改 `assets/interface.json`、pipeline、图片、OCR 文本、ROI、`template` 或 task entry 后，应运行资源检查；涉及登录、选服、账号切换或跨模块流水线时，还应安排手动 debug。
