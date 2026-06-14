# Root Interface Decision

Date: 2026-06-09

Task: R6-root-interface-decision

Decision owner: MaaZJ refactor workflow

## 决策摘要

MaaZJ 当前运行与发布配置继续以 `assets/interface.json` 为唯一 canonical source。根目录 `interface.json` 不作为 runtime truth、release truth、task inventory 来源或 `pipeline_override` 决策来源。

根目录 `interface.json` 当前应被视为历史/兼容/待处置对象。后续可以通过单独任务选择“删除、迁移、同步生成或明确保留兼容入口”等路径，但 R6 不执行这些处置动作。

## 输入来源

- `AGENTS.md`
- `docs/agent_context/PROJECT_UNDERSTANDING_2026-06-06.md`
- `docs/agent_context/interface_inventory_2026-06-08.md`
- `docs/agent_design/refactor_design_maafw_test_automation_2026-06-07.md`
- `.agent/tasks/2026-06-09-r6-root-interface-decision/`
- 只读解析 `assets/interface.json`
- 只读解析根目录 `interface.json`

## 当前事实

`AGENTS.md` 已规定最高优先级运行与发布配置为 `assets/interface.json`。它定义 `controller`、`resource`、`agent` 与 `task`，也是发布入口；`install.py` 会复制 `assets/interface.json` 到 `install/interface.json`，并用 `json.load` 读取。

R1 inventory 已确认：

- `assets/interface.json` 严格 JSON 解析通过。
- canonical ProjectInterface 中有 35 个 task。
- 顶层 `pipeline_override` 字段覆盖共 64 项。
- 所有 `task[].entry` 都能在 `assets/resource/pipeline/` 中找到静态定义。
- 根目录 `interface.json` 未作为运行真相读取、同步、迁移或修改。

R6 只读检查确认：

| 项目 | `assets/interface.json` | root `interface.json` |
| --- | ---: | ---: |
| `name` | `杖剑传说小助手` | `杖剑传说小助手` |
| `version` | `v0.1.0` | `v0.1.0` |
| task 数量 | 35 | 14 |
| controller preset 数量 | 8 | 8 |
| resource preset 数量 | 8 | 8 |
| 是否配置 agent | yes | yes |

两份文件同名同版本，但 task 数量和 task 名称集合不同。root `interface.json` 中仍保留 `执行小号流水线...`、`执行大号流水线...` 等旧命名 task；`assets/interface.json` 中则包含当前 R1 inventory 记录的 35 个 task 和账号/服务器 `pipeline_override` 结构。

## 当前决策

1. `assets/interface.json` 保持 runtime/release canonical source。
2. 根目录 `interface.json` 不用于判断 task 展示、task entry、账号/服务器差异、`pipeline_override` 或发布行为。
3. 后续审计、测试脚本、README runtime truth、task generation POC 和真实流程 smoke 均应优先读取 `assets/interface.json`。
4. 如果某个任务明确针对根目录 `interface.json`，也只能把它作为被审计或被处置对象；不能在该任务中反向改变 canonical source。
5. 在没有单独批准的 root 文件处置任务前，不删除、不同步、不迁移、不格式化根目录 `interface.json`。

## 禁止事项

- 不把 root `interface.json` 当作 `assets/interface.json` 的替代品。
- 不用 root `interface.json` 生成 task inventory、override matrix、smoke matrix 或 task generator 输入。
- 不因为 root 文件 task 数量较少而删除 `assets/interface.json` 中的账号/服务器 task。
- 不把两份文件的差异当作自动同步补丁。
- 不在 C 类 pipeline 重构、T 类只读脚本或 D 类 README 更新中顺手修改 root `interface.json`。
- 不在未确认上游 ProjectInterface 能力和发布流程前，把 root 文件改造成新入口。

## 推荐后续路径

### D1-readme-runtime-truth

D1 可以引用本决策，在 README 或运行说明中明确：

- 当前运行真相是 `assets/interface.json`。
- 根目录 `interface.json` 非 canonical。
- 发布产物由 `install.py` 使用 `assets/interface.json` 生成。

D1 不应借此修改两份 interface 文件。

### C8-interface-task-generation-poc

C8 可以引用本决策，把 `assets/interface.json` 和 R1 override matrix 作为 POC 对照对象。root `interface.json` 只可作为“误用风险”或“旧入口差异”说明，不可作为 generator 的输入基线。

如果 C8 评估生成器，应证明账号/服务器 `pipeline_override` 保真，不能用 root 文件较少 task 的结构替代 canonical 配置。

### D5-agents-skill-sync

本决策主要复述并固化现有 AGENTS 规则，未改变仓库级 canonical source。因此 R6 本身暂不要求立即执行 D5。

如果后续 D1、C8 或单独 root 文件处置任务把本决策扩展成新的稳定操作流程，例如新增“root 文件只允许由脚本生成”或“root 文件应删除”的仓库级规则，则应创建 D5 检查并同步 `AGENTS.md` 与项目专属 skill。

### 单独 root 文件处置任务

如果维护者希望真正处理根目录 `interface.json`，建议新建独立任务，而不是混入 R6 或其他 C/T/D 任务。可选方向包括：

- 删除 root `interface.json`，并更新文档和发布流程风险说明。
- 保留 root `interface.json`，但新增明显的文档声明或生成机制。
- 从 `assets/interface.json` 生成 root `interface.json` 的兼容副本。
- 验证目标 MFAAvalonia 或其他工具是否仍需要根目录文件。

这些方向都需要重新评估影响范围，并至少完成 V0 文档/配置检查；若触及发布或运行入口，还需要更高层验证。

## 验证边界

R6 完成的是 V0 静态决策验证：

- 严格 JSON 解析 `assets/interface.json`。
- 严格 JSON 解析 root `interface.json`。
- 比较两份文件的顶层摘要和 task 数量。
- 交叉检查 `AGENTS.md`、R1 inventory 与设计文档 R6 矩阵。

R6 未执行：

- V1 MaaFramework resource load。
- V2 task entry 启动验证。
- V3 真实控制器流程验证。
- V4 日志、截图或 debug 证据。
- V5 回归矩阵。

未执行这些验证是符合预期的，因为 R6 不修改资源、pipeline、图片、agent、发布产物或运行配置。

## 残余风险

- root `interface.json` 仍然存在，后续人工或工具仍可能误读它。
- 旧 task 命名保留在 root 文件中，可能在搜索或快速浏览时制造噪声。
- 当前决策不解决“是否最终删除或生成 root 文件”的问题，只把处置动作推迟到独立任务。
- 如果某个外部工具默认读取仓库根目录 `interface.json`，本决策不会自动改变该工具行为；需要单独验证和处置。

## D4/D5/N1 判断

- D4：暂不需要。设计文档中 R6 的输入、产出、禁止事项、验证和消费者描述足够支撑本任务。
- D5：暂不需要立即执行。本决策固化的是既有 AGENTS 规则，没有引入新的 canonical source 规则。
- N1：暂不需要。未发现新的用户需求；删除、同步、迁移或生成 root `interface.json` 均应在用户明确提出后单独分流。
