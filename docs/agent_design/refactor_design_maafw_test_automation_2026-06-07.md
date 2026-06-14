# MaaZJ MaaFramework 适配重构与自动化测试设计

## 目录

- [如何使用本文档](#如何使用本文档)
- [Plan 到设计文档映射](#plan-到设计文档映射)
- [范围边界](#范围边界)
- [当前运行事实](#当前运行事实)
- [设计主轴](#设计主轴)
- [同步范围判定](#同步范围判定)
- [产出物目录约定](#产出物目录约定)
- [关键产物最小格式](#关键产物最小格式)
- [主轴到任务映射](#主轴到任务映射)
- [验证分层](#验证分层)
- [真实流程 smoke 方案](#真实流程-smoke-方案)
- [详细任务矩阵](#详细任务矩阵)
- [可执行任务清单摘要](#可执行任务清单摘要)
- [单任务 Runbook](#单任务-runbook)
- [下一任务选择规则](#下一任务选择规则)
- [后续任务收尾检查](#后续任务收尾检查)
- [D4/D5 判定表](#d4d5-判定表)
- [真实流程验证降级记录](#真实流程验证降级记录)
- [附录 A：通用任务提示词模板](#附录-a通用任务提示词模板)
- [附录 B：R0/R1/R2 提示词](#附录-br0r1r2-提示词)
- [附录 C：D4/D5/N1 提示词](#附录-cd4d5n1-提示词)
- [附录 D：边界反例](#附录-d边界反例)

## 如何使用本文档

本文档用于指导 MaaZJ 后续资源重构、流程理解、测试体系建设和文档反馈闭环。它不是升级计划，也不是一次性实施清单。

维护者只需要按当前场景选择入口：

| 场景 | 下一步 |
| --- | --- |
| 第一次开始本轮重构 | 从 `R0-baseline-resource` 开始 |
| 需要理解 `assets/interface.json` 的 task 和 override | 执行 `R1-interface-inventory` |
| 需要理解当前 pipeline flow | 执行 `R2-pipeline-flow-map-initial` |
| 某个后续任务发现本文档不准确 | 执行或建议 `D4-design-feedback-sync` |
| 本文档中的稳定规则变化 | 执行或建议 `D5-agents-skill-sync` |
| 有新的业务或工程需求 | 先执行 `N1-new-requirement-triage` |

所有后续任务都应通过 `multi-agent-refactor` 单独创建 `.agent/tasks/<task-id>/`。本文档中的 Runbook 和提示词是后续复制使用的入口，不表示当前文档任务已经执行这些任务。

## Plan 到设计文档映射

本节用于保证后续实现者能从 `plan` 直接检查本文档是否落地完整。每轮修订本文档时，必须把 plan 中的治理要求映射到可阅读章节、可执行任务和可复制提示词，而不是只写原则性说明。

| Plan 要求 | 本文档落点 | 实施验收 |
| --- | --- | --- |
| 设计文档必须能指导 MaaZJ 重构任务拆分 | `设计主轴`、`详细任务矩阵`、`单任务 Runbook` | 每个任务有 Task ID、输入、产出、允许修改、禁止事项、验证和停止点 |
| 后续任务可能反复发现设计文档不足 | `D4-design-feedback-sync`、`后续任务收尾检查`、`附录 C` | 每个任务收尾必须检查是否需要 D4，并提供可复制提示词 |
| 设计文档变化应和 `AGENTS.md`、项目专属 skill 协作 | `同步范围判定`、`D5-agents-skill-sync`、`D4/D5 判定表`、`附录 C` | 稳定规则变化必须触发 D5 检查，产出同步记录或无需同步说明 |
| 新需求进入项目时应先由设计文档帮助落地 | `N1-new-requirement-triage`、`下一任务选择规则`、`附录 C` | 新需求先完成归类、风险分级、依赖产物检查和后续任务提示词 |
| 设计文档必须包含一页目录 | `目录` | 目录位于标题后，能快速定位关键章节 |
| 设计文档必须包含单任务 Runbook | `单任务 Runbook` | Runbook 独立成节，按执行顺序说明边界、产出、验证和下一触发 |
| 任务清单必须足够详细 | `详细任务矩阵` | R/C/T/D/N 任务均覆盖消费产物、生产产物、允许修改、禁止事项和 D4/D5/N1 检查 |

## 范围边界

目标：

- 让 MaaZJ 当前资源组织更贴合 MaaFramework 的运行模型：`ProjectInterface -> resource -> pipeline -> optional custom agent`。
- 先沉淀当前 task、override、pipeline flow、图片/OCR/ROI、Python custom 和验证事实，再开始代码重构。
- 把重构拆成可单独执行、可 review、可验证、可回写的任务。
- 建立从静态检查、资源加载到真实 task entry、控制器证据和回归矩阵的测试分层。
- 建立设计文档、`AGENTS.md`、项目专属 skill 和新需求落地之间的协作机制。

非目标：

- 不升级 MaaFramework、MFAAvalonia、MaaPracticeBoilerplate 或 MaaHub 相关运行时。
- 不修改 `deps/`、`install/`、release workflow 或 artifact 下载。
- 不在本文档任务中新增测试脚本、generator 或 CI workflow。
- 不在本文档任务中直接修改 `assets/interface.json`、pipeline、图片、OCR 或 Python agent。
- 不承诺本文档任务已跑通任何真实游戏流程；真实流程验证必须在后续任务中执行并留证据。

## 当前运行事实

- `assets/interface.json` 是 MaaZJ 当前 runtime/release canonical source。
- 根目录 `interface.json` 不是 canonical，除非任务明确针对它。
- `assets/interface.json` 必须保持严格 JSON；`install.py` 会复制它并用 `json.load` 读取。
- `assets/resource/pipeline/` 可能包含 MaaFramework-compatible JSONC-like 内容，不应被严格 JSON 工具批量格式化。
- task 实际执行入口来自 `assets/interface.json` 的 `task[].entry`。
- `pipeline_override` 承载账号、服务器和 task-specific 差异，在替代机制落地前不得折叠、删除或自动生成覆盖。
- Python agent 已配置启动 `{PROJECT_DIR}/agent/main.py`，但业务 pipeline 接入需要重新搜索验证。
- `check_resource.py` 使用 `Resource.post_bundle(...)` 验证 resource bundle 可加载，只能证明 V1，不证明真实 task 跑通。
- 真实任务执行需要通过 `Tasker.post_task(...)` 或 MFAAvalonia 根据 `task[].entry` 启动，并在控制器环境下观察关键节点、日志或截图。

## 设计主轴

设计主轴不是另一套要执行的任务。主轴用于说明为什么拆任务、哪些产物必须先产生、这些产物如何被后续代码重构和验证消费。真正执行入口始终是后文的 R/C/T/D/N 任务。

### 主轴 A：ProjectInterface 治理

职责：

- 只处理 `assets/interface.json` 作为 source-of-truth 的治理。
- 整理 task、entry、controller/resource/agent 配置、`pipeline_override` 和 root `interface.json` 决策。
- 不负责 pipeline 模块划分、图片引用或真实控制器 smoke 执行。

关键产物：

- `task inventory`
- `pipeline_override matrix`
- `root interface decision`

验证：

- `assets/interface.json` 严格 JSON 解析通过。
- 每个 `task[].entry` 能映射到 pipeline 节点，或明确标记异常。
- 每个 `pipeline_override` 的目标节点存在，并记录账号/服务器语义和禁止折叠原因。

禁止：

- 不修改或同步根目录 `interface.json`。
- 不删除、合并或折叠 `pipeline_override`。
- 不把 `task inventory` 当成 task 生成器实现。

### 主轴 B：Pipeline 结构边界

职责：

- 处理 `pipeline flow map`、模块边界、跨模块边、recovery 路径和低风险试点选择。
- 不处理 ProjectInterface 的 source-of-truth 决策。
- 不直接重命名、删除或移动 pipeline 节点；真正资源修改必须进入 C 类任务。

建议模块：

- `startup`
- `account`
- `farm_daily`
- `shop`
- `guild`
- `notebook`
- `activity`
- `bed_mail_reward`
- `account_creation`
- `recovery`

关键产物：

- `pipeline flow map`：由 R2 主生产。
- `recovery path catalog`：由 R3 主生产。
- `module boundary`：由 R7 主生产。
- `low-risk pilot selection`：由 R8 主生产。

验证：

- `next`、`interrupt`、`on_error` 不出现悬空节点。
- 被改模块入口仍可由 task entry 或上游节点到达。
- C 类代码重构必须通过 V1，并按风险执行 V2/V3/V4 或写降级记录。

禁止：

- 不把跨模块 flow 一次性整体重构。
- 不把 recovery 节点和业务节点混在一个代码重构任务里。
- 不用 strict JSON parser 批量格式化 pipeline。

### 主轴 C：识别资源治理

职责：

- 处理图片、template、OCR、ROI、识别节点和截图证据之间的引用关系。
- 不负责 pipeline 业务语义重构。
- 不负责 Python custom action/recognition 注册治理。

关键产物：

- `image usage report`
- `ocr roi risk table`
- `recognition evidence index`

验证：

- 所有 `template` 引用都能在 `assets/resource/image/` 找到，或明确记录缺失。
- 重命名图片前后引用数量必须一致。
- 涉及 OCR/ROI 的任务必须记录截图或 debug 依据。

### 主轴 D：Python custom agent 扩展边界

职责：

- 处理 `agent/` 中 custom action/recognition 的注册、引用状态和准入条件。
- 不把 Python agent 简化判断为“没用”。
- pipeline 能稳定表达的逻辑优先留在 pipeline。

关键产物：

- `registered name report`
- `custom admission checklist`
- `custom call evidence`

状态枚举：

| 状态 | 含义 |
| --- | --- |
| `wired` | 已在 pipeline 中引用且有真实调用证据 |
| `referenced_unverified` | 已引用但缺少真实调用证据 |
| `registered_unreferenced` | 已注册但未发现业务引用 |
| `candidate_remove_later` | 后续清理候选，当前任务不得删除 |

验证：

- 每个 registered name 至少有一条 pipeline 引用，或被标记为未接入/待清理。
- 新增 custom 后，必须有 pipeline 引用和真实调用证据。

### 主轴 E：验证体系与证据治理

职责：

- 管理 V0-V5 验证分层、smoke matrix、证据保存和降级记录。
- 不替代 CI/发布升级任务。

关键产物：

- `verification matrix`
- `smoke plan`
- `evidence index`
- `degraded verification record`

验证：

- 每个 R/C/T/D/N 任务都有最低验证层。
- 每个 C 类任务都有 V2/V3/V4 的适用说明或降级记录要求。
- 真实流程证据能从任务总结回查到文件位置。

### 主轴 F：设计文档、AGENTS/skill 与新需求落地治理

职责：

- 管理设计文档持续修订、稳定规则同步、项目协作入口和新需求分流。
- 不直接修改业务资源，不替代 R/C/T 任务实现职责。
- 不把临时探索结论写入 `AGENTS.md` 或项目专属 skill。

关键产物：

- `refactor playbook`
- `runtime truth doc update`
- `feedback log`
- `risk register`
- `design feedback record`
- `agents skill sync record`
- `new requirement triage report`

验证：

- 每个后续任务总结都回答是否需要回写设计文档、是否需要同步 AGENTS/skill、是否需要创建新需求或后续修订任务。
- 设计文档稳定规则变化后，必须检查 `AGENTS.md` 与项目专属 skill 是否需要同步；无需同步时也要记录原因。
- 新需求落地任务必须产出后续可复制提示词，而不是直接混入当前任务实现。

## 同步范围判定

| 承载位置 | 适合写入 | 不适合写入 |
| --- | --- | --- |
| 设计文档 | 重构主轴、任务矩阵、产出物格式、验证分层、Runbook、提示词模板、需求分流规则 | 单次任务日志全文、未确认的临时猜测 |
| `AGENTS.md` | 仓库级稳定安全边界、canonical source、必须遵守的验证规则、语言规则、目录地图 | 某次任务的阶段性计划、尚未稳定的实验结论 |
| 项目专属 skill | MaaZJ 专用操作流程、可复用检查顺序、ProjectInterface/pipeline 安全索引、常用参考路径 | 只适合本文档的一次性段落、业务实现细节的大段复制 |
| `.agent/tasks/*` | 单任务计划、review、implementation、test、final、临时决策和证据索引 | 长期稳定规则的唯一来源 |

## 产出物目录约定

| 产出物类型 | 默认位置 | 命名建议 | 更新条件 |
| --- | --- | --- | --- |
| 只读审计报告 | `docs/agent_context/` | `<topic>_<YYYY-MM-DD>.md` | R 类准备任务完成或发现新的运行事实 |
| 重构设计与决策文档 | `docs/agent_design/` | `<topic>_<YYYY-MM-DD>.md` | R6-R9、D 类任务完成 |
| 真实流程证据索引 | `docs/agent_context/` 或任务 `test.md` | `verification_evidence_<YYYY-MM-DD>.md` | C/T6 任务执行 V2/V3/V4 后 |
| 后续任务总结与反馈 | `.agent/tasks/<task-id>/final.md`，必要时汇总到 `docs/agent_context/` | `refactor_feedback_<YYYY-MM-DD>.md` | 每个 C/T/D/N 任务完成后 |
| smoke matrix/playbook | `docs/agent_design/` | `real_flow_smoke_plan_<YYYY-MM-DD>.md` | T6、D3 或真实流程反馈后 |

## 关键产物最小格式

| 产物 | 最小字段 | 判定标准 | 消费者 |
| --- | --- | --- | --- |
| `task inventory` | task name、entry、task 类型、controller/resource/agent、是否 override、真实验证候选、风险等级 | 每个 `assets/interface.json` task 都有记录；entry 能在 pipeline 中找到或标记异常 | R2、R6、C6-C8、T2、T6、D1 |
| `pipeline_override matrix` | task name、override path、目标节点、覆盖字段、账号/服务器语义、禁止折叠原因、验证候选 | 每个 override 均可追到 pipeline 节点；至少选一个进入 smoke matrix | R2、C6-C8、T2、T6 |
| `pipeline flow map` | task/entry、关键节点、出口、`next`、`interrupt`、`on_error`、跨模块边候选、真实验证候选 | 启动、账号、日常、活动至少各有一个 flow 记录；不替代 module boundary/recovery catalog | R7、R8、C1-C7、T3、T6、D3 |
| `module boundary` | 模块名、职责、入口、出口、共享节点、跨模块边、禁止改动边 | 每个候选 C 类任务能映射到单个模块或子 flow | C1-C7、D3 |
| `recovery path catalog` | recovery 节点、触发来源、期望页面、失败处理、验证 case | recovery 节点能被 C5 和 S7 消费 | C5、T6、D3 |
| `image usage report` | 图片名、引用节点、recognition 类型、是否缺失、复用数量、截图验证需求 | 所有 template 引用能找到文件或标记缺失 | C1-C5、T4、T6 |
| `registered name report` | registered name、类型、注册文件、pipeline 引用、状态枚举、调用证据 | 每个 registered name 有状态；未引用不被直接删除 | R5、T5、D2 |
| `smoke plan` | case id、控制器、执行方式、task、entry、override、前置条件、期望节点、证据位置、降级规则 | S1-S7 覆盖，且至少包含一个 override 路径 | C1-C8、T6、D3 |
| `design feedback record` | 来源任务、发现问题、影响主轴、建议修订、是否需 D5、后续提示词 | 任何设计文档回写都可追溯来源和影响范围 | D4、D5、后续 review |
| `new requirement triage report` | 新需求、归类、风险、建议任务、修改边界、验证层、后续提示词 | 不直接实现，先完成分流和任务拆分 | N1、后续实现任务 |

## 主轴到任务映射

| 主轴 | 关键产物 | 消费任务 | 如何影响重构 | 如何影响验证 |
| --- | --- | --- | --- | --- |
| A ProjectInterface 治理 | task inventory、`pipeline_override matrix`、root `interface.json` decision | R1、R2、R6、C6-C8、T2、T6、D1 | 决定真实入口、override 保留边界和生成器 POC 对照对象 | V0 检查 entry/override；T6 至少选择一个 override flow |
| B Pipeline 结构边界 | pipeline flow map、module boundary、recovery path catalog、low-risk pilot selection | R2、R3、R7、R8、C1-C7、T3、T6、D3 | 决定代码重构最小边界和试点顺序 | C 类任务必须证明入口仍可达、边不悬空，并通过 V2/V3/V4 或记录降级 |
| C 识别资源治理 | image usage report、ocr roi risk table、recognition evidence index | R4、C1-C5、T4、T6、D3 | 决定是否只改 pipeline，还是同步处理 template/OCR/ROI | 识别变化必须有截图或 debug 证据 |
| D Python custom agent | registered name report、custom admission checklist、custom call evidence | R5、后续 agent 任务、T5、D2 | 决定 custom 是保留、接入、拆出还是后续清理 | 新接入 custom 必须证明真实 task 调用 |
| E 验证体系 | verification matrix、smoke plan、evidence index、degraded verification record | R0、R2、R8、C1-C8、T1-T7、D3 | 决定每个任务最低验证层、证据要求和降级规则 | 所有任务完成标准绑定 V0-V5 |
| F 文档与新需求治理 | refactor playbook、feedback log、risk register、D4/D5/N1 产物 | D1-D5、N1、T7、后续所有任务 | 决定如何执行、复盘、回写设计文档、同步稳定规则和承接新需求 | 每个任务收尾自动检查文档回写、AGENTS/skill 同步和需求拆分 |

## 验证分层

| 层级 | 名称 | 证明什么 | 不证明什么 | 适用任务 |
| --- | --- | --- | --- | --- |
| V0 | 静态文件检查 | JSON、JSONC-aware 引用、文件存在性 | 不证明 MaaFramework 能加载 | 准备任务、测试工具任务 |
| V1 | MaaFramework resource load | resource bundle 可被 `Resource.post_bundle(...)` 加载 | 不证明 task 能执行 | 所有资源变更任务 |
| V2 | task entry 启动验证 | 能通过 `Tasker.post_task(...)` 或 MFAAvalonia 启动指定 entry | 不证明完整业务完成 | 低风险代码重构任务 |
| V3 | 真实控制器流程验证 | 在 Adb/Win32 控制器下跑到预期关键节点或终止状态 | 不覆盖所有回归路径 | 所有 C 类代码重构任务 |
| V4 | 证据采集 | 有日志、截图、debug 记录可复查 | 不自动判断全部正确性 | 所有真实运行验证 |
| V5 | 回归矩阵 | 多个关键 flow 未退化 | 不替代人工业务判断 | 高风险 flow、发布前 |

资源变更的最低验证是：

```powershell
python .\check_resource.py .\assets\resource\
```

但这只是 V1。代码重构完成标准必须高于资源加载，至少说明 V2/V3/V4 的执行结果或降级原因。

### C 类 V3/V4 记录要求

C 类任务在执行真实控制器验证时，应优先消费 `docs/agent_design/real_flow_smoke_plan_2026-06-14.md`。后续 C1-C8 的 plan/test/final 至少记录以下内容：

- 执行条件：控制器类型、设备或窗口标识、目标应用状态、账号/服务器/活动前置、资源加载结果。
- 路径来源：ProjectInterface task、entry、task-level `pipeline_override`，以及是否使用一次性运行时 override。
- 路径边界：完整 task 还是分段投递；若分段，分别列出每段起点、期望节点、停止点和未覆盖分支。
- V3 结果：真实控制器到达的关键节点或终止状态。
- V4 证据：日志、截图、录屏、debug 记录或 evidence index；涉及 OCR/TemplateMatch/ROI 变化时记录命中文本/模板、位置、score 或截图。
- 结论措辞：完整覆盖写“通过”；只覆盖目标子 flow 或使用 stop override 阻止越界时写“通过，有边界”；未执行则写降级记录。

一次性运行时 override 只能用于限制验证出口，不能改变被验证节点的识别、动作或业务语义；它不能把被跳过的上游、下游或兄弟分支算作通过。

## 真实流程 smoke 方案

T6 需要定义 smoke matrix，而不是承诺 CI 全自动执行。

每条 smoke case 至少包含：

- Case ID。
- 控制器类型：Adb 或 Win32。
- 执行方式：MFAAvalonia 或 Python Tasker。
- ProjectInterface task name。
- pipeline entry。
- 是否使用 `pipeline_override`。
- 前置条件：账号、服务器、当前页面、资源状态。
- 操作步骤。
- 期望关键节点或终止状态。
- 证据：`debug/maa.log`、截图、录屏、任务返回状态、手动观察记录。
- 失败处理和回滚方式。

最小 smoke 矩阵：

| Case | 目标 |
| --- | --- |
| S1 | 启动到首页 |
| S2 | 选服路径，至少一个带 `pipeline_override` 的服务器 |
| S3 | 账号切换路径，至少一个带账号 override 的任务 |
| S4 | 一个低风险 shop/reward 子 flow |
| S5 | 一个日常子 flow |
| S6 | 一个活动 flow |
| S7 | 异常弹窗或返回首页 recovery |

## 详细任务矩阵

详细任务矩阵是后续创建 `.agent/tasks/<task-id>/` 的最小契约。执行者不得只复制任务标题；必须把对应行中的输入、产出、允许修改、禁止事项、验证、停止点和 D4/D5/N1 检查写入该任务的 plan。

### R 类矩阵：准备、理解与决策

| Task ID | 类型/主轴 | 消费产物 | 生产产物 | 必读输入 | 允许修改 | 禁止事项 | 最低验证/真实流程触发 | 回写与停止点 | 自动检查 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R0-baseline-resource | 准备，主轴 E | 无 | baseline resource result、验证环境说明 | `AGENTS.md`、`check_resource.py`、`assets/resource/` | `.agent/`、`docs/agent_context/` | 不改资源、不修复 pipeline、不改依赖 | V1；不触发真实流程 | 记录资源加载结果后停在 review | 若验证边界不清，触发 D4 |
| R1-interface-inventory | 只读理解，主轴 A | R0 推荐但不强制 | task inventory、override matrix 初版、entry 异常清单 | `assets/interface.json`、AGENTS runtime truth | 报告文档 | 不改 `assets/interface.json`，不碰 root `interface.json`，不折叠 override | V0；不触发真实流程 | inventory 抽查后停在 review | 若 canonical/override 规则需固化，触发 D4/D5 |
| R2-pipeline-flow-map-initial | 只读理解，主轴 B/E | R1 | pipeline flow map 初版、验证候选点、unknown 节点清单 | `assets/interface.json`、`assets/resource/pipeline/`、pipeline AGENTS | 报告文档 | 不格式化 JSONC-like pipeline，不修改节点 | V0；不触发真实流程 | flow map 抽查后停在 review | 若节点边界不足，触发 D4 |
| R3-pipeline-graph-audit | 只读审计，主轴 B/E | R2 | graph/reference report、recovery path catalog 初版 | flow map、pipeline 目录 | 报告或只读脚本方案 | 不自动删除悬空节点，不重命名节点 | V0；不触发真实流程 | 悬空引用和 recovery 候选 review | 若 recovery 规则稳定，触发 D5 检查 |
| R4-image-reference-audit | 只读审计，主轴 C/E | R2 | image usage report、OCR/ROI risk table | pipeline 目录、`assets/resource/image/` | 报告文档 | 不重命名图片，不改 ROI/OCR 文本 | V0；不触发真实流程 | 缺失图片和截图候选 review | 若图片规则需加入指南，触发 D5 |
| R5-agent-custom-audit | 只读审计，主轴 D/E | R1、R2 | registered name report、业务接入状态 | `agent/`、`assets/interface.json`、pipeline | 报告文档 | 不删除 Python agent，不推断“没用” | V0；不触发真实流程 | custom 状态 review | 若 agent 接入判断规则变化，触发 D4/D5 |
| R6-root-interface-decision | 决策，主轴 A/F | R1 | root interface decision | task inventory、AGENTS root interface 规则 | 设计文档、决策记录 | 不同步、迁移或删除 root `interface.json` | 文档 review | 决策 review | 若决策变成稳定规则，触发 D5 |
| R7-module-boundary-doc | 决策，主轴 B/F | R2、R3、R4 | module boundary、risk register 初版 | flow map、graph report、image report | 设计文档 | 不提前重构 pipeline | V0 文档交叉检查 | 模块边界 review | 若边界不适配任务，触发 D4 |
| R8-low-risk-flow-selection | 决策，主轴 B/C/E | R1、R2、R4、R7 | low-risk pilot selection、首个 C 任务候选 | task inventory、flow map、image report、module boundary | 设计文档 | 不直接修改试点 flow | 文档 review | 试点 review | 若候选缺验证路径，触发 D4 |
| R9-test-script-design | 决策，主轴 E/F | R0-R5 | verification matrix、只读脚本设计 | baseline、inventory、flow/image/custom 报告 | 设计文档、脚本方案 | 不把脚本接入 CI，不改业务资源 | 文档 review | 测试设计 review | 若脚本规则可复用，触发 D5 |

### C 类矩阵：代码重构候选

| Task ID | 类型/主轴 | 消费产物 | 生产产物 | 必读输入 | 允许修改 | 禁止事项 | 最低验证/真实流程触发 | 回写与停止点 | 自动检查 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1-shop-flow-pilot | 低风险实现，主轴 B/C/E | R1、R2、R4、R7、R8、T6 | 单个 shop 子 flow 变更、验证证据 | 试点选择、flow map、image report、smoke plan | 限定 shop 子 flow 相关 pipeline/图片引用报告 | 不扩散到账号/选服/活动主链路 | V1+V2；具备环境时执行 V3/V4，否则降级记录 | 代码 review/test 后停 | 必查 D4；稳定规则变化查 D5；衍生需求走 N1 |
| C2-reward-cleanup-flow | 低风险实现，主轴 B/C/E | R2、R4、R7、T6 | reward/bed/mail 子 flow 变更、回归证据 | flow map、module boundary、image report | 单个 reward/收尾子 flow | 不合并无关奖励节点 | V1+V2+V3/V4 或降级 | 证据归档后 review | 同 C1 |
| C3-activity-single-flow | 中风险实现，主轴 B/C/E | R1、R2、R4、R7、T6 | 单个 activity flow 变更、活动验证记录 | activity flow map、图片/OCR 风险 | 单个 activity flow | 不同时重构多个活动或公共 recovery | V1+V2+V3/V4 或降级 | activity review | 同 C1 |
| C4-farm-daily-subflow | 中风险实现，主轴 B/C/E | R1、R2、R4、R7、T6 | 一个 daily 子 flow 变更、daily 回归证据 | daily entry、flow map、image report | 单个 daily 子 flow | 不改账号切换和启动链路 | V1+V2+V3/V4 或降级 | daily review | 同 C1 |
| C5-recovery-node-normalization | 共享路径实现，主轴 B/E | R3、R7、T6 | recovery 节点整理、影响范围表 | recovery catalog、module boundary | recovery 相关节点和报告 | 不删除未验证的 fallback，不改业务目标节点 | V1+V2+至少一个 S7 或降级 | recovery review | 必查 D4/D5 |
| C6-account-flow-design-only | 高风险设计，主轴 A/B/D/E | R1、R2、R5、T6 | account flow 设计、验证计划 | override matrix、registered name report | 文档为主 | 不修改账号切换 pipeline | 文档 review | 设计批准后再拆实现任务 | 若出现实现需求，走 N1 或新 C 任务 |
| C7-startup-flow-design-only | 高风险设计，主轴 A/B/D/E | R1、R2、R5、T6 | startup/server flow 设计、验证计划 | entry/override、flow map、custom 报告 | 文档为主 | 不修改登录、选服、启动 pipeline | 文档 review | 设计批准后再拆实现任务 | 同 C6 |
| C8-interface-task-generation-poc | POC，主轴 A/E/F | R1、R6、R9、T6 | generator POC 或方案、override 保真报告 | task inventory、root decision、verification matrix | POC 文件或方案，不改 canonical config | 不替换 `assets/interface.json`，不生成覆盖发布配置 | V0+至少一个 override V2/V3 | POC review | 若生成器规则稳定，触发 D5 |

### T 类矩阵：测试工具与自动化

| Task ID | 类型/主轴 | 消费产物 | 生产产物 | 必读输入 | 允许修改 | 禁止事项 | 最低验证/真实流程触发 | 回写与停止点 | 自动检查 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T1-json-strict-check | 工具，主轴 A/E | R1 | strict JSON check 命令或脚本 | `assets/interface.json`、`install.py` | 只读脚本/文档 | 不格式化 pipeline，不改 JSON 内容 | V0 | 脚本输出 review | 若成为通用规则，触发 D5 |
| T2-interface-audit-script | 工具，主轴 A/E | R1 | ProjectInterface audit report | task inventory、override matrix | 只读脚本/报告 | 不写回 interface | V0 | audit report review | D4/D5 检查 |
| T3-pipeline-ref-check-script | 工具，主轴 B/E | R2、R3 | JSONC-aware ref report | flow map、pipeline JSONC 规则 | 只读脚本/报告 | 不 strict-format pipeline | V0 | ref report review | D4/D5 检查 |
| T4-image-usage-check-script | 工具，主轴 C/E | R4 | image usage check report | image usage report | 只读脚本/报告 | 不重命名或删除图片 | V0 | image report review | D4/D5 检查 |
| T5-agent-custom-check-script | 工具，主轴 D/E | R5 | custom registered name check report | registered name report、agent 入口 | 只读脚本/报告 | 不删 agent 注册 | V0 | custom report review | D4/D5 检查 |
| T6-real-flow-smoke-plan | 流程验证，主轴 E/F | R1、R2、R7-R9 | smoke plan、case matrix、证据模板 | task inventory、flow map、module boundary | 文档/验证模板 | 不执行未授权真实流程，不改资源 | 文档 review；执行时 V2/V3/V4 | smoke plan review | 若真实流程需求新增，走 N1 |
| T7-ci-readonly-checks | 自动化，主轴 E/F | T1-T5、R9 | CI readonly check 方案或 workflow | 只读脚本、验证矩阵 | CI 方案或只读 workflow | 不接入会写资源的检查，不改 release 产物 | V0/V1 | CI review | 若 CI 规则稳定，触发 D5 |

### D/N 类矩阵：文档同步与新需求

| Task ID | 类型/主轴 | 消费产物 | 生产产物 | 必读输入 | 允许修改 | 禁止事项 | 最低验证/真实流程触发 | 回写与停止点 | 自动检查 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1-readme-runtime-truth | 文档，主轴 A/F | R1、R6 | README runtime truth 小节 | root decision、AGENTS | README/文档 | 不改变配置 | Markdown 检查 | README review | 若 README 规则应同步 skill，触发 D5 |
| D2-agent-status-doc | 文档，主轴 D/F | R5 | Python agent 状态说明 | registered name report | README 或 agent 文档 | 不删 agent，不声称未使用 | registered name 搜索一致 | agent 文档 review | D5 检查 |
| D3-refactor-playbook | 文档，主轴 F | R7-R9、T6 | refactor playbook | module boundary、verification matrix | playbook 文档 | 不替代 AGENTS 最高优先规则 | Markdown 检查 | playbook review | D5 检查 |
| D4-design-feedback-sync | 文档回写，主轴 F | 任意任务反馈 | design feedback record、设计文档修订、可复制后续提示词 | 当前任务 implementation/review/test 证据、本文档 | `docs/agent_design/`、对应 `.agent` 记录 | 不借 D4 直接改业务资源；不扩大成无边界重写 | Markdown 检查、影响范围 review | 回写完成后停在 review | 该任务本身也检查是否引出 D5/N1 |
| D5-agents-skill-sync | 指南同步，主轴 F | 已批准的稳定设计规则 | agents skill sync record、`AGENTS.md`/skill 更新或无需同步说明 | 本文档、`AGENTS.md`、项目专属 skill | `AGENTS.md`、`.codex/skills/maazj-maafw-refactor/SKILL.md`、相关设计记录 | 不把未批准实验写入 AGENTS/skill；不降低 `assets/interface.json` 优先级 | Markdown 检查、规则一致性 review | 同步 review 后停 | 检查是否需要 D4 回写本文档 |
| N1-new-requirement-triage | 新需求入口，主轴 A-F | 用户需求、当前设计产物 | triage report、风险分级、后续任务提示词 | 本文档、AGENTS、相关 inventory/flow/report | `.agent` 任务记录、设计/需求文档 | 不直接实现高风险需求，不绕过 R/C/T/D 依赖 | 文档 review、边界检查；按需求决定是否需要 V1-V4 | 拆分任务提示词确认后停 | 检查是否需要 D4/D5 |

## 可执行任务清单摘要

每个任务都应单独创建 `.agent/` 任务。若前置产物缺失，先补前置任务，不跳到后续任务。

### R 类：准备与理解

| Task ID | 需求 | 输出 | 修改范围 | 最低验证 | 停止点 |
| --- | --- | --- | --- | --- | --- |
| R0-baseline-resource | 冻结当前资源加载基线 | baseline resource result | `.agent/`、`docs/agent_context/` | V1 | resource load 结果记录后 review |
| R1-interface-inventory | 生成 task/override 只读清单 | task inventory、override matrix 初版 | 报告文档 | V0 | inventory review |
| R2-pipeline-flow-map-initial | 生成 pipeline flow map 初版 | flow map 初版、验证候选点 | 报告文档 | V0 | flow map 抽查后 review |
| R3-pipeline-graph-audit | 建立 graph/reference 与 recovery catalog | graph/reference report、recovery path catalog 初版 | 报告或只读脚本方案 | V0 | 悬空引用/recovery 候选 review |
| R4-image-reference-audit | 建立图片/OCR/ROI 引用报告 | image usage report、ocr roi risk table | 报告文档 | V0 | 缺失图片和截图候选 review |
| R5-agent-custom-audit | 明确 Python custom agent 接入状态 | registered name report | 报告文档 | V0 | custom 状态 review |

### R 类：设计与决策

| Task ID | 需求 | 输出 | 修改范围 | 最低验证 | 停止点 |
| --- | --- | --- | --- | --- | --- |
| R6-root-interface-decision | 决策 root `interface.json` 边界 | root interface decision | 设计文档 | 文档 review | 决策 review |
| R7-module-boundary-doc | 定义模块边界 | module boundary | 设计文档 | V0 | 模块边界 review |
| R8-low-risk-flow-selection | 选择第一个低风险试点 | low-risk pilot selection | 设计文档 | 文档 review | 试点 review |
| R9-test-script-design | 设计只读测试脚本 | verification matrix、脚本设计 | 设计文档 | 文档 review | 测试设计 review |

### C 类：真正代码重构

这些任务后续必须逐个创建 `.agent/` 任务执行，不在本文档任务中实现。

| Task ID | 需求 | 依赖产物 | 修改范围 | 验证 |
| --- | --- | --- | --- | --- |
| C1-shop-flow-pilot | 重构一个低风险 shop 子 flow | task inventory、flow map、module boundary、image report、smoke plan | 单个 shop 子 flow | V1+V2+V3+V4 或降级记录 |
| C2-reward-cleanup-flow | 重构奖励领取/收尾子 flow | flow map、module boundary、image report、smoke plan | 单个 reward/bed/mail 子 flow | V1+V2+V3+V4 或降级记录 |
| C3-activity-single-flow | 重构单个活动 flow | task inventory、flow map、module boundary、image report、smoke plan | 单个 activity flow | V1+V2+V3+V4 或降级记录 |
| C4-farm-daily-subflow | 重构 farm daily 一个低风险子流程 | task inventory、flow map、module boundary、image report、smoke plan | 单个 daily 子 flow | V1+V2+V3+V4 或降级记录 |
| C5-recovery-node-normalization | 整理公共 recovery 节点 | recovery catalog、module boundary、smoke plan | recovery 相关节点 | V1+V2+V3+V4 或降级记录 |
| C6-account-flow-design-only | 账号切换 flow 先只做设计 | task inventory、override matrix、flow map、registered name report、smoke plan | 文档为主 | 文档 review |
| C7-startup-flow-design-only | 启动/选服 flow 先只做设计 | task inventory、override matrix、flow map、registered name report、smoke plan | 文档为主 | 文档 review |
| C8-interface-task-generation-poc | 评估 task 生成器 POC | task inventory、override matrix、root interface decision、smoke plan | POC 或方案，不改 canonical config | V0+至少一个 override V2/V3 |

### T 类：测试工具与自动化

| Task ID | 需求 | 输出 | 验证 |
| --- | --- | --- | --- |
| T1-json-strict-check | 实现严格 JSON 检查 | 只读脚本/命令 | V0 |
| T2-interface-audit-script | 实现 ProjectInterface 静态审计 | audit report | V0 |
| T3-pipeline-ref-check-script | 实现 JSONC-aware pipeline 引用检查 | ref report | V0 |
| T4-image-usage-check-script | 实现图片引用检查 | image report | V0 |
| T5-agent-custom-check-script | 实现 custom registered name 检查 | custom report | V0 |
| T6-real-flow-smoke-plan | 建立真实流程 smoke 验证方案 | smoke plan/matrix | 文档 review，执行时 V2/V3/V4 |
| T7-ci-readonly-checks | 接入或设计 CI 只读检查 | CI readonly check 方案 | V0/V1 |

### D 类：文档与同步

| Task ID | 需求 | 输出 | 验证 |
| --- | --- | --- | --- |
| D1-readme-runtime-truth | README 说明真实运行入口和验证方式 | README 变更 | Markdown 检查 |
| D2-agent-status-doc | 说明 Python agent 当前接入状态 | agent 文档或 README 小节 | registered name 搜索一致 |
| D3-refactor-playbook | 将每类重构操作写成 playbook | playbook 文档 | 与 AGENTS 规则一致 |
| D4-design-feedback-sync | 后续任务发现设计文档不足时回写设计文档 | design feedback record、设计文档修订、后续提示词 | Markdown 检查、影响范围 review |
| D5-agents-skill-sync | 设计文档稳定规则变化后同步 AGENTS/skill | agents skill sync record、同步变更或无需同步说明 | Markdown 检查、规则范围 review |

### N 类：新需求落地

| Task ID | 需求 | 输出 | 验证 |
| --- | --- | --- | --- |
| N1-new-requirement-triage | 新需求进入项目时先分流和拆分 | new requirement triage report、风险分级、后续任务提示词 | 文档 review、边界检查 |

## 单任务 Runbook

本 Runbook 用于把本文档中的任务逐个落地到 `.agent/tasks/<task-id>/`。执行者复制某一行启动任务时，必须把该行转写进新任务 plan，并在任务收尾检查 D4/D5/N1。除非用户明确要求，单个任务不得越过本行的允许修改范围，也不得顺手执行下一行任务。

### Runbook 使用规则

- 每次只创建并执行一个 Task ID；任务完成后停在 `review`、`test` 或 `final` 确认点。
- 新任务 plan 必须包含：任务编号、目标、必读输入、允许修改、禁止事项、产出、最低验证、停止点、下一步触发、D4/D5/N1 检查。
- 如果必读输入不存在，先创建缺失的前置任务，不跳过补档。
- 如果执行中发现本文档错误、字段不够或提示词不可用，优先在当前任务允许范围内记录问题；需要修改本文档时触发 D4。
- 如果本文档修订产生稳定规则、长期安全边界或可复用流程变化，触发 D5 检查是否同步 `AGENTS.md` 与项目专属 skill。
- 如果用户提出的新需求不能直接归入当前任务目标，创建 N1 或在当前任务收尾产出 N1 提示词。

### Runbook 顺序表

| 顺序 | Task ID | 目标 | 必读输入 | 允许修改 | 必须产出 | 最低验证/停止点 | 下一步触发 | D4/D5/N1 检查 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | R0-baseline-resource | 冻结当前资源加载基线 | AGENTS、`check_resource.py`、`assets/resource/` | `.agent/`、`docs/agent_context/` | baseline result、环境说明、失败日志或通过证据 | V1；记录后停 review | R1 | 验证层级不清则 D4 |
| 2 | R1-interface-inventory | 建立 task/entry/override 事实清单 | R0 结果、`assets/interface.json` | 报告文档 | task inventory、override matrix、entry 异常清单 | V0；inventory 抽查后停 review | R2、R6、T1/T2 | canonical 或 override 规则变化查 D4/D5 |
| 3 | R2-pipeline-flow-map-initial | 建立 pipeline flow map 初版 | R1、pipeline 目录 AGENTS | 报告文档 | flow map、下游节点、验证候选点 | V0；flow map 抽查后停 review | R3、R4、R7 | flow 边界不足则 D4 |
| 4 | R3-pipeline-graph-audit | 审计引用、悬空节点和 recovery | R2 | 报告或只读脚本方案 | graph/reference report、recovery catalog | V0；异常候选 review | R7、T3、C5 | recovery 稳定规则查 D5 |
| 5 | R4-image-reference-audit | 审计图片/OCR/ROI 引用 | R2、图片目录 | 报告文档 | image usage report、OCR/ROI risk table | V0；缺失图片候选 review | R7、R8、T4 | 图片规则变化查 D4/D5 |
| 6 | R5-agent-custom-audit | 明确 Python custom agent 接入状态 | R1、R2、`agent/` | 报告文档 | registered name report、业务引用状态 | V0；custom 状态 review | C6、C7、T5、D2 | agent 状态规则变化查 D4/D5 |
| 7 | R6-root-interface-decision | 固化 root `interface.json` 边界决策 | R1、AGENTS | 设计/决策文档 | root interface decision | 文档 review | D1、C8 | 稳定规则变化查 D5 |
| 8 | R7-module-boundary-doc | 定义 pipeline 模块边界 | R2、R3、R4 | 设计文档 | module boundary、risk register | V0 文档交叉检查；review | R8、C1-C5 | 边界不适配则 D4 |
| 9 | R8-low-risk-flow-selection | 选择第一个低风险试点 | R1、R2、R4、R7 | 设计文档 | pilot selection、首个 C 任务提示词 | 文档 review | C1 或 C2 | 候选缺验证路径则 D4 |
| 10 | R9-test-script-design | 设计只读测试脚本与矩阵 | R0-R5 | 设计文档、脚本方案 | verification matrix、脚本边界 | 文档 review | T1-T7 | 通用规则查 D5 |
| 11 | T1-json-strict-check | 落地 `assets/interface.json` 严格 JSON 检查 | R1、R9 | 只读脚本/命令、报告 | strict JSON check | V0；review | T2 或 T7 | 工具边界不清则 D4 |
| 12 | T2-interface-audit-script | 审计 task/entry/override | R1、R9 | 只读脚本、报告 | audit report | V0；review | T7、C8 | 审计规则稳定则 D5 |
| 13 | T3-pipeline-ref-check-script | 审计 pipeline 引用 | R2、R3、R9 | 只读脚本、报告 | ref report | V0；review | T7、C1-C5 | JSONC 处理规则查 D5 |
| 14 | T4-image-usage-check-script | 审计图片引用 | R4、R9 | 只读脚本、报告 | image report | V0；review | T7、C1-C4 | 图片策略变化查 D4/D5 |
| 15 | T5-agent-custom-check-script | 审计 custom registered name | R5、R9 | 只读脚本、报告 | custom report | V0；review | T7、C6/C7 | agent 规则变化查 D4/D5 |
| 16 | T6-real-flow-smoke-plan | 建立真实流程 smoke 方案 | R1、R2、R7-R9 | 文档/模板 | smoke matrix、证据模板、降级格式 | 文档 review；执行时 V2/V3/V4 | C1-C8 | 新真实流程诉求走 N1 |
| 17 | T7-ci-readonly-checks | 设计或接入只读 CI 检查 | T1-T5、R9 | CI 方案或只读 workflow | CI readonly check 方案、失败说明 | V0/V1；CI review | D5 或 C 任务 | CI 规则稳定查 D5 |
| 18 | D1-readme-runtime-truth | README 说明运行真相 | R1、R6 | README/文档 | runtime truth 小节 | Markdown 检查；review | D3/D5 | README 规则应同步则 D5 |
| 19 | D2-agent-status-doc | 文档化 Python agent 状态 | R5 | README 或 agent 文档 | agent status doc | registered name 搜索一致；review | D3/D5 | 稳定 agent 规则查 D5 |
| 20 | D3-refactor-playbook | 写出重构操作 playbook | R7-R9、T6 | playbook 文档 | refactor playbook | Markdown 检查；review | D5、C 任务 | playbook 规则查 D5 |
| 21 | C1-shop-flow-pilot | 实施首个 shop 子 flow 试点 | R8、T3/T4/T6 | 限定 pipeline/必要图片引用报告 | 变更、验证证据、回写记录 | V1+V2+V3/V4 或降级；review/test | C2 或 D4 | 必查 D4/D5/N1 |
| 22 | C2-reward-cleanup-flow | 实施 reward/收尾子 flow | R7、T3/T4/T6 | 限定 pipeline | 变更、验证证据 | V1+V2+V3/V4 或降级；review/test | C3/C4 | 必查 D4/D5/N1 |
| 23 | C3-activity-single-flow | 实施单个活动 flow | R1、R2、R4、T6 | 单个 activity flow | 变更、活动验证记录 | V1+V2+V3/V4 或降级；review/test | 后续 activity 任务 | 必查 D4/D5/N1 |
| 24 | C4-farm-daily-subflow | 实施一个 daily 子 flow | R1、R2、R4、T6 | 单个 daily 子 flow | 变更、daily 回归证据 | V1+V2+V3/V4 或降级；review/test | 后续 daily 任务 | 必查 D4/D5/N1 |
| 25 | C5-recovery-node-normalization | 整理公共 recovery 节点 | R3、R7、T6 | recovery 相关节点 | 变更、影响范围表、S7 证据或降级 | V1+V2+S7 或降级；review/test | 更大范围重构 | 必查 D4/D5/N1 |
| 26 | C6-account-flow-design-only | 账号切换 flow 只做设计 | R1、R2、R5、T6 | 文档为主 | account flow design、验证计划 | 文档 review | 单独账号实现任务 | 实现诉求走 N1 或新 C |
| 27 | C7-startup-flow-design-only | 启动/选服 flow 只做设计 | R1、R2、R5、T6 | 文档为主 | startup/server flow design、验证计划 | 文档 review | 单独启动实现任务 | 实现诉求走 N1 或新 C |
| 28 | C8-interface-task-generation-poc | 评估 task 生成器 POC | R1、R6、R9、T6 | POC 或方案 | generator POC、override 保真报告 | V0+至少一个 override V2/V3；review | D5 或放弃记录 | 生成器规则稳定查 D5 |
| 29 | D4-design-feedback-sync | 回写设计文档缺口 | 任意任务反馈 | `docs/agent_design/`、`.agent` 记录 | design feedback record、设计文档修订、可复制提示词 | Markdown 检查、影响范围 review | 原任务重试或下一任务 | 本任务继续检查 D5/N1 |
| 30 | D5-agents-skill-sync | 同步稳定规则到 AGENTS/skill | 已批准设计规则 | `AGENTS.md`、项目专属 skill、同步记录 | sync record、同步变更或无需同步说明 | Markdown 检查、规则一致性 review | 回到原重构链 | 检查是否需要 D4 |
| 31 | N1-new-requirement-triage | 新需求分流、拆分和落地 | 用户需求、本文档、相关产物 | `.agent` 记录、需求/设计文档 | triage report、风险分级、后续任务提示词 | 文档 review、边界检查 | 对应 R/C/T/D 任务 | 检查是否需要 D4/D5 |

### 启动单任务的可复制提示语

把下面模板中的 `<Task ID>`、`<目标>` 和 `<补充上下文>` 替换后即可开始。具体任务的边界必须从上方 Runbook 和详细任务矩阵复制。

```text
继续 multi-agent-refactor 工作流，创建并执行 <Task ID>。

目标：<目标>
补充上下文：<补充上下文>

请在 plan 中纳入本文档对应的详细任务矩阵和单任务 Runbook 边界：必读输入、允许修改、禁止事项、必须产出、最低验证、停止点、下一步触发，以及 D4/D5/N1 自动检查。
如果执行中发现设计文档不准确、字段不足或提示词不可用，请触发或建议 D4-design-feedback-sync。
如果设计文档变化影响 AGENTS.md 或项目专属 skill 的稳定规则，请触发 D5-agents-skill-sync。
如果发现用户新需求不属于当前任务边界，请触发 N1-new-requirement-triage 或产出可复制的 N1 提示语。
```

## 下一任务选择规则

- 若 `R0-baseline-resource` 未完成，下一任务只能是 R0。
- 若 `task inventory` 缺失，下一任务只能是 R1。
- 若 `pipeline flow map 初版` 缺失，下一任务只能是 R2。
- 若 C 类任务依赖的产物缺失，先执行对应 R/T/D 任务。
- 若 smoke plan 缺失，不开始 C 类代码重构。
- 若 V2/V3/V4 无法执行且没有降级记录，不进入更大范围重构。
- 若 V3/V4 使用分段投递或一次性运行时 stop override，只能进入相同边界的后续任务；进入更大范围重构前必须补完整 task 或对应分支的验证/降级记录。
- 若任务发现设计文档不准确、边界缺失或提示词不可用，优先创建 D4 或在允许范围内回写设计文档。
- 若设计文档变化影响稳定安全规则或可复用流程，创建 D5 检查并同步 AGENTS/skill。
- 若维护者提出新需求且尚未完成归类和验证路径选择，下一任务应是 N1。
- 若发现升级前置条件，创建升级任务并停止当前重构链。

## 后续任务收尾检查

每个 R/C/T/D/N 任务在进入 review、test 或 final 前必须回答：

- 本任务生产了哪些主轴产物。
- 本任务消费了哪些主轴产物。
- 消费产物是否过时、缺字段或与真实运行不一致。
- 本任务执行了哪些验证层。
- 是否执行真实流程验证；如果没有，为什么没有。
- 证据保存在哪里。
- 是否需要回写 `pipeline flow map`、`module boundary`、`image usage report`、`registered name report`、`smoke plan`、`risk register` 或 `refactor playbook`。
- 是否需要回写本文档。
- 是否有稳定规则变化需要同步 `AGENTS.md` 或项目专属 skill。
- 是否发现新需求，需要创建 N1 或后续实现任务。

## D4/D5 判定表

| 发现情况 | 处理 |
| --- | --- |
| 只是当前任务报告中的一次性观察 | 写入当前 `.agent/tasks/<task-id>/final.md` |
| 本文档某个字段、边界、提示词不准确 | 当前任务允许则回写；否则创建 D4 |
| 修订会影响多个主轴或任务模板 | 创建 D4 |
| 稳定安全边界、canonical source、验证最低要求变化 | 创建 D5 检查 `AGENTS.md` |
| MaaZJ 专属检查流程或参考路径变化 | 创建 D5 检查项目专属 skill |
| 尚未验证的猜测或临时结论 | 不写入 `AGENTS.md` 或 skill |

## 真实流程验证降级记录

如果计划应执行 V2/V3/V4 但当前环境无法执行，必须生成 `degraded verification record`：

- 原计划验证层。
- 未执行原因：无设备、无账号状态、无可用窗口、前置条件不可满足、任务只做文档等。
- 已执行的替代验证。
- 可能漏掉的风险。
- 补验条件。
- 后续补验任务建议。

降级记录只能说明当前验证受限，不能把代码重构任务直接视为完整通过。高风险账号、启动、选服、recovery flow 在没有 V2/V3/V4 或降级记录前，不允许进入更大范围重构。

若任务通过分段投递或一次性运行时 stop override 完成 V3/V4，应在同一位置记录为“通过，有边界”，并列明未覆盖的上游、下游、兄弟分支和特殊账号/override。该结论不是降级，但也不能替代完整 task 回归。

## 附录 A：通用任务提示词模板

```text
[$maazj-maafw-refactor](C:\Users\xieqi\Documents\GitHub\MaaZJ\.codex\skills\maazj-maafw-refactor\SKILL.md) 使用 multi-agent-refactor 工作流创建并处理一个新任务：

任务：<Task ID>，<一句话任务标题>。

目标：
- <目标 1>
- <目标 2>

必须读取：
- AGENTS.md
- <本任务依赖的主轴产物或报告>
- <相关 canonical 文件>

允许修改：
- `.agent/tasks/<本任务>/` 工作流文件
- <明确的报告/文档/脚本范围>

禁止事项：
- <MaaZJ 安全边界>
- <本任务特定禁止事项>

验证：
- <最低验证层>
- <真实流程触发或降级要求>

停止点：
- <产出完成后停在 review/test/确认点>
```

## 附录 B：R0/R1/R2 提示词

### R0-baseline-resource

```text
[$maazj-maafw-refactor](C:\Users\xieqi\Documents\GitHub\MaaZJ\.codex\skills\maazj-maafw-refactor\SKILL.md) 使用 multi-agent-refactor 工作流创建并处理一个新任务：

任务：R0-baseline-resource，冻结 MaaZJ 当前资源加载基线。

目标：
- 只读确认当前 `assets/resource/` 是否能通过 MaaFramework resource load。
- 记录 `python .\check_resource.py .\assets\resource\` 的结果。
- 产出 baseline 报告，供后续 R1/R2/C 类任务对照。

必须读取：
- AGENTS.md
- check_resource.py
- assets/resource/

允许修改：
- `.agent/tasks/<本任务>/` 工作流文件
- `docs/agent_context/` 下的 baseline 报告

禁止事项：
- 不修改 `assets/interface.json`
- 不修改根目录 `interface.json`
- 不修改 `assets/resource/pipeline/`
- 不修改 `assets/resource/image/`
- 不修改 `agent/`、`deps/`、`install/`、CI

验证：
- 运行 `python .\check_resource.py .\assets\resource\`
- 如果无法运行，记录原因、替代检查和补验条件

停止点：
- baseline 报告完成并进入 review 确认点。
```

### R1-interface-inventory

```text
[$maazj-maafw-refactor](C:\Users\xieqi\Documents\GitHub\MaaZJ\.codex\skills\maazj-maafw-refactor\SKILL.md) 使用 multi-agent-refactor 工作流创建并处理一个新任务：

任务：R1-interface-inventory，生成 `assets/interface.json` 的 task/override 只读结构表。

目标：
- 以 `assets/interface.json` 为 canonical source。
- 生成 task inventory，记录 task name、entry、task 类型、controller/resource/agent、是否包含 `pipeline_override`、真实验证候选和风险等级。
- 生成 `pipeline_override matrix` 初版，记录 override path、目标节点、覆盖字段、账号/服务器语义和禁止折叠原因。

必须读取：
- AGENTS.md
- docs/agent_context/PROJECT_UNDERSTANDING_2026-06-06.md
- assets/interface.json
- R0 baseline 报告（如果已存在）

允许修改：
- `.agent/tasks/<本任务>/` 工作流文件
- `docs/agent_context/` 下的 inventory 报告

禁止事项：
- 不修改 `assets/interface.json`
- 不同步、不删除、不迁移根目录 `interface.json`
- 不折叠或删除任何 `pipeline_override`
- 不修改 pipeline、图片或 agent

验证：
- 严格 JSON 解析 `assets/interface.json`
- 抽查每个 `task[].entry` 是否后续需要在 R2 中追踪
- 抽查每个 `pipeline_override` 是否记录目标节点和语义

停止点：
- task inventory 与 override matrix 初版完成并进入 review 确认点。
```

### R2-pipeline-flow-map-initial

```text
[$maazj-maafw-refactor](C:\Users\xieqi\Documents\GitHub\MaaZJ\.codex\skills\maazj-maafw-refactor\SKILL.md) 使用 multi-agent-refactor 工作流创建并处理一个新任务：

任务：R2-pipeline-flow-map-initial，生成 MaaZJ 当前 pipeline flow map 初版。

目标：
- 从 R1 task inventory 和 `assets/interface.json` 的 `task[].entry` 出发。
- 只读追踪 `assets/resource/pipeline/` 中主要 flow 的入口、关键节点、出口、`next`、`interrupt`、`on_error`。
- 生成 pipeline flow map 初版。
- 标记 S1-S7 真实流程验证候选点。
- 只提供跨模块边、recovery、模块归属候选，不产出最终 module boundary、recovery catalog 或低风险试点决策。

必须读取：
- AGENTS.md
- assets/resource/pipeline/AGENTS.md
- docs/agent_context/PROJECT_UNDERSTANDING_2026-06-06.md
- assets/interface.json
- assets/resource/pipeline/
- R1 task inventory 与 override matrix（如果已存在）

允许修改：
- `.agent/tasks/<本任务>/` 工作流文件
- `docs/agent_context/` 下的 pipeline flow map 初版报告

禁止事项：
- 不修改 `assets/interface.json`
- 不修改任何 pipeline 文件
- 不严格格式化 JSONC-like pipeline
- 不重命名、删除或移动节点
- 不把候选跨模块边当作最终 module boundary
- 不选择 C 类代码重构试点

验证：
- 抽查若干 `task[].entry` 能在 flow map 中找到
- 抽查若干 `next`、`interrupt`、`on_error` 目标节点存在
- 至少为启动、账号切换、一个日常 flow、一个活动 flow 标记真实运行验证候选点

停止点：
- pipeline flow map 初版完成并进入 review 确认点。
```

## 附录 C：D4/D5/N1 提示词

### D4-design-feedback-sync

```text
[$maazj-maafw-refactor](C:\Users\xieqi\Documents\GitHub\MaaZJ\.codex\skills\maazj-maafw-refactor\SKILL.md) 使用 multi-agent-refactor 工作流创建并处理一个新任务：

任务：D4-design-feedback-sync，回写 MaaZJ 重构设计文档。

目标：
- 根据后续任务中发现的设计文档缺口，修订 `docs/agent_design/refactor_design_maafw_test_automation_2026-06-07.md`。
- 明确本次回写影响哪些主轴、任务清单、验证层、Runbook 或提示词。
- 产出 design feedback record，并判断是否需要后续 D5 同步 AGENTS/skill。

必须读取：
- AGENTS.md
- docs/agent_design/refactor_design_maafw_test_automation_2026-06-07.md
- 触发本次回写的 `.agent/tasks/<来源任务>/review.md`、`test.md` 或 `final.md`
- 相关主轴产物或报告

允许修改：
- `.agent/tasks/<本任务>/` 工作流文件
- `docs/agent_design/refactor_design_maafw_test_automation_2026-06-07.md`
- 必要的 design feedback record

禁止事项：
- 不修改 `assets/interface.json`
- 不修改根目录 `interface.json`
- 不修改 pipeline、图片、agent、deps、install、CI
- 不在本任务中同步 AGENTS/skill；如需要同步，创建 D5

验证：
- 检查 Markdown 可读性
- 检查修订是否明确影响范围、回写位置和后续任务提示词
- 检查是否记录“需要或不需要 D5”的理由

停止点：
- 设计文档回写完成并进入 review 确认点。
```

### D5-agents-skill-sync

```text
[$maazj-maafw-refactor](C:\Users\xieqi\Documents\GitHub\MaaZJ\.codex\skills\maazj-maafw-refactor\SKILL.md) 使用 multi-agent-refactor 工作流创建并处理一个新任务：

任务：D5-agents-skill-sync，同步 MaaZJ 设计文档、AGENTS 与项目专属 skill。

目标：
- 根据设计文档中的稳定规则变化，检查 `AGENTS.md` 与 `.codex/skills/maazj-maafw-refactor/` 是否需要同步。
- 只同步仓库级安全边界、canonical source、验证最低要求、目录索引、可复用流程和 MaaZJ 专属检查顺序。
- 产出 agents skill sync record；如果无需同步，写明理由。

必须读取：
- AGENTS.md
- `.codex/skills/maazj-maafw-refactor/SKILL.md`
- `.codex/skills/maazj-maafw-refactor/references/` 中与本次变化相关的文件
- docs/agent_design/refactor_design_maafw_test_automation_2026-06-07.md
- 触发同步的 D4 或来源任务总结

允许修改：
- `.agent/tasks/<本任务>/` 工作流文件
- AGENTS.md
- `.codex/skills/maazj-maafw-refactor/` 中相关 skill/reference 文件
- 必要的 sync record

禁止事项：
- 不修改 `assets/interface.json`
- 不修改根目录 `interface.json`
- 不修改 pipeline、图片、agent、deps、install、CI
- 不把单次任务日志、临时猜测或未验证探索结论写入 AGENTS/skill

验证：
- 检查 Markdown 可读性
- 检查同步内容是否属于稳定规则或可复用流程
- 检查设计文档、AGENTS、skill 之间没有互相矛盾的边界说明

停止点：
- AGENTS/skill 同步或无需同步说明完成，并进入 review 确认点。
```

### N1-new-requirement-triage

```text
[$maazj-maafw-refactor](C:\Users\xieqi\Documents\GitHub\MaaZJ\.codex\skills\maazj-maafw-refactor\SKILL.md) 使用 multi-agent-refactor 工作流创建并处理一个新任务：

任务：N1-new-requirement-triage，使用 MaaZJ 重构设计文档分流一个新需求。

目标：
- 阅读用户新需求，并根据设计文档判断它属于 ProjectInterface、pipeline、识别资源、Python custom、测试工具、文档、升级/运行时或混合任务。
- 给出风险分级、允许修改范围、禁止事项、最低验证层和真实流程验证触发条件。
- 拆分后续单任务，并产出可直接复制给 Codex 的后续任务提示词。

必须读取：
- AGENTS.md
- docs/agent_design/refactor_design_maafw_test_automation_2026-06-07.md
- 与新需求相关的主轴产物或报告
- 用户提供的新需求描述

允许修改：
- `.agent/tasks/<本任务>/` 工作流文件
- `docs/agent_context/` 下的 new requirement triage report（如需要）

禁止事项：
- 不在本任务中直接修改 `assets/interface.json`
- 不在本任务中直接修改 pipeline、图片、agent、deps、install、CI
- 不把升级任务混入资源重构任务
- 不创建后续实现任务，除非用户在 triage review 后明确确认

验证：
- 检查需求归类是否引用设计文档主轴和任务矩阵
- 检查后续任务是否有明确边界、产出和验证层
- 若建议代码重构，必须指定 V1-V4 或降级要求

停止点：
- triage report 和后续任务提示词完成，并进入 review 确认点。
```

## 附录 D：边界反例

- `task inventory` 不是 task 生成器，不允许据此自动改写 `assets/interface.json`。
- `pipeline flow map` 不是 pipeline 重排方案，不允许据此直接重命名或移动节点。
- `image usage report` 不是图片清理清单，删除或重命名前仍必须逐项查引用。
- `registered name report` 不是 Python agent 删除依据，未接入只能标记状态，不能在设计任务里删除。
- `smoke plan` 不是 CI 全自动承诺；真实设备流程可以人工/半自动，但必须有证据和降级记录。
- README/playbook 更新不能反向改变运行真相，运行真相仍以 `assets/interface.json` 为准。
